import json
import random
import string
import requests

from flask import Blueprint, request, jsonify, make_response, session, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from captcha.image import ImageCaptcha
from flask_mail import Message
from datetime import datetime
from sqlalchemy import update

from blueprints.forms import RegisterForm, LoginForm, ResetPwdForm
from decorators import check_params
from exts import db, mail
from models import UserInfo, EmailCode, UserMessage
from functions import CustomResponse, SuccessResponse
from static.enums import MessageTypeEnum
from static.globalDto import ADMIN_EMAIL

bp = Blueprint("LoginAndRegister", __name__, url_prefix="/")


@bp.route("/checkCode")
def imagecaptcha():
    characters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(characters) for i in range(5))
    captcha = ImageCaptcha()
    text = result_str  # 这里的文本内容可以替换成任意字符串
    image_data = captcha.generate(text)

    # 将图片数据转化为响应对象
    session["checkCode"] = text
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    print(text)
    # return send_file(image_data, "png")
    return response


@bp.route("/sendEmailCode", methods=['POST'])
@check_params
def sendEmailCode():
    email = request.form.get("email")
    send_type = request.form.get("type")
    # 注册时先判断是否邮箱已经被注册
    if send_type == '0':
        # 检查是否已经存在此邮箱
        user = UserInfo.query.filter_by(email=email).first()
        if user:
            abort(400, description="该邮箱已经被注册")
    # 生成验证码
    source = string.digits * 6
    captcha = random.sample(source, 6)
    captcha = "".join(captcha)
    # 先将之前该邮箱注册过的验证码失效
    db.session.execute(update(EmailCode).where(EmailCode.email == email and EmailCode.status == 0).values(status=1))
    db.session.commit()
    # 将验证码写入数据库
    email_code = EmailCode(email=email, code=captcha, create_time=datetime.now(), status=0)
    db.session.add(email_code)
    db.session.commit()
    try:
        # 发送邮箱验证码
        message = Message(subject="验证码", recipients=[email], body=f"您的验证码是：{captcha}")
        mail.send(message)
        return CustomResponse(code=200).to_dict()
    except Exception as e:
        print("send error" + str(e))
        return "send error" + str(e)


@bp.route("/register", methods=['POST'])
@check_params
def register():
    form = RegisterForm(request.form)
    if form.validate():
        email = form.email.data
        emailCode = form.emailCode.data
        nickName = form.nickName.data
        password = form.password.data
        # # 检查邮箱验证码
        dbInfo = EmailCode.query.get((email, emailCode))
        if dbInfo is None:
            abort(400, description="邮箱验证码不正确")
        if dbInfo.status != 0 or (datetime.now() - dbInfo.create_time).seconds > 900:
            abort(400, description="该邮箱验证码已失效")
        dbInfo.status = 1
        db.session.commit()
        # #  生成用户账号,写入数据库
        userId = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        user = UserInfo(user_id=userId, nick_name=nickName, email=email, password=generate_password_hash(password),
                        join_time=datetime.now(),
                        last_login_time=datetime.now(),
                        status=1)
        db.session.add(user)
        db.session.commit()
        # # 记录消息
        usermessage = UserMessage(received_user_id=userId, message_type=MessageTypeEnum.SYS.value.get("type"),
                                  create_time=datetime.now(), status=1,
                                  message_content=g.registerInfo.getregisterWelcomInfo())
        db.session.add(usermessage)
        db.session.commit()

        return CustomResponse(code=200).to_dict()
    else:
        print(form.errors.values())
        abort(400)


@bp.route("/login", methods=['POST'])
@check_params
def login():
    form = LoginForm(request.form)
    if form.validate():
        email = form.email.data
        password = form.password.data
        checkCode = form.checkCode.data
        # 检查账号
        userinfo = UserInfo.query.filter_by(email=email).first()
        if userinfo is None or not check_password_hash(userinfo.password, password):
            abort(400, description="账户或密码错误")
        if userinfo.status == 0:
            abort(400, description="账号已被禁用")
        # 检查验证码
        sessionCheckcode = session.get('checkCode')
        if not sessionCheckcode:
            abort(400, description="该邮箱已经被注册")
        if checkCode.lower() != sessionCheckcode.lower():
            abort(400, description="验证码错误")
        # 获取登录ip以及地址
        try:
            # user_ip = request.remote_addr
            user_ip = '211.137.7.243'
            # user_ip='67.84.0.0' 纽约地址
            ipapi_url = f'https://ipapi.co/{user_ip}/json/'
            location = requests.get(ipapi_url, timeout=5).json()
            dict_location = {"country_name": "未知", "region": "未知", "city": "未知"}
            if location.get('error') is None:
                dict_location['country_name'] = location['country_name']
                dict_location['region'] = location['region']
                dict_location['city'] = location['city']
        except requests.exceptions.Timeout as e:
            return jsonify(error=str(e)), 408
        else:
            session.pop('checkCode')
            # 修改用户字段
            userinfo.last_login_time = datetime.now()
            userinfo.last_login_ip = user_ip
            userinfo.last_login_ip_address = json.dumps(dict_location)
            db.session.commit()
            # 保存在session中
            session_userInfo = {
                'schoolEmail': userinfo.school_email,
                'school': userinfo.school,
                'nickName': userinfo.nick_name,
                'lastLoginIpAddress': userinfo.last_login_ip_address,
                'userId': userinfo.user_id
            }
            if userinfo.email in ADMIN_EMAIL:
                session_userInfo['isAdmin'] = True
            else:
                session_userInfo['isAdmin'] = False
            session['userInfo'] = session_userInfo
            return SuccessResponse(data=session_userInfo)
    else:
        print(form.errors)
        abort(400)


@bp.route("/getUserInfo", methods=['POST'])
@check_params
def getuserinfo():
    userinfo = None
    if session.get('userInfo'):
        userinfo = session['userInfo']
    return CustomResponse(code=200, data=userinfo).to_dict()


@bp.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return CustomResponse(code=200).to_dict()


@bp.route("/getSysSetting", methods=['POST'])
def getsyssetting():
    return CustomResponse(code=200, data=g.commentInfo.to_dict()).to_dict()


@bp.route("/resetPwd", methods=['POST'])
def resetpassword():
    form = ResetPwdForm(request.form)
    if form.validate():
        email = form.email.data
        password = form.password.data
        checkCode = form.checkCode.data
        emailCode = form.emailCode.data
        # 验证验证码是否正确
        sessionCheckcode = session.get('checkCode')
        if checkCode.lower() != sessionCheckcode.lower():
            abort(400, description="验证码错误")
        user = UserInfo.query.filter_by(email=email).first()
        if not user:
            abort(400, description="邮箱不存在")
        #  检查邮箱验证码
        dbInfo = EmailCode.query.get((email, emailCode))
        if dbInfo is None:
            abort(400, description="邮箱验证码不正确")
        if dbInfo.status != 0 or (datetime.now() - dbInfo.create_time).seconds > 900:
            abort(400, description="邮箱验证码已失效")
        dbInfo.status = 1
        # 更新密码
        user.password = generate_password_hash(password)
        db.session.commit()
        session.pop('checkCode')
        return CustomResponse(code=200).to_dict()
    else:
        print(form.errors)
        abort(400, description=form.errors)

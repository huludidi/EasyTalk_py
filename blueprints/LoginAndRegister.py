import io
import random
import string
from flask import Blueprint, request, send_file, jsonify, make_response, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from captcha.image import ImageCaptcha
from flask_mail import Message
from datetime import datetime
from sqlalchemy import update

from blueprints.forms import RegisterForm
from decorators import check_params
from exts import db, mail
from models import UserInfo, EmailCode, UserMessage
from CustomResponse import CustomResponse
from static.enums import MessageTypeEnum

bp = Blueprint("LoginAndRegister", __name__, url_prefix="/")


@bp.route("/checkcode", methods=['POST'])
def imagecaptcha():
    characters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(characters) for i in range(5))
    captcha = ImageCaptcha()
    text = result_str  # 这里的文本内容可以替换成任意字符串
    image_data = captcha.generate(text)

    # 将图片数据转化为响应对象
    session["check_code"] = text
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'

    # return send_file(image_data, "png")
    return response


@bp.route("/sendEmailCode", methods=['POST'])
@check_params
def sendEmailCode():
    email = request.form.get("email")
    send_type = request.form.get("type")
    # 注册时先判断是否邮箱已经被注册
    if send_type is '0':
        # 检查是否已经存在此邮箱
        user = UserInfo.query.filter_by(email=email).first()
        if user:
            return CustomResponse(info="邮箱已经被注册").to_dict()
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
        return "Sent successfully"
    except Exception as e:
        print("send error" + str(e))
        return "send error" + str(e)


@bp.route("/register", methods=['POST'])
@check_params
def register():
    form = RegisterForm(request.form)
    if form.validate():
        email = request.form.get('email')
        emailCode = request.form.get('emailCode')
        nickName = request.form.get('nickName')
        password = request.form.get('password')
        # user = UserInfo.query.filter_by(nick_name=nickName).first()
        # if user:
        #     return CustomResponse(info="昵称已被注册").to_dict()
        # # 检查邮箱验证码
        dbInfo = EmailCode.query.get((email, emailCode))
        if dbInfo is None:
            return CustomResponse(info="邮箱验证码不正确").to_dict()
        if dbInfo.status != 0 or (datetime.now() - dbInfo.create_time).seconds > 900:
            return CustomResponse(info="邮箱验证码已经失效").to_dict()
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
        return CustomResponse(code=600).to_dict()


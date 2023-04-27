import io
import random
import string
from flask import Blueprint, request, send_file, jsonify, make_response, session
from captcha.image import ImageCaptcha
from flask_mail import Message
from datetime import datetime
from exts import db, mail
from models import UserInfo, EmailCode

bp = Blueprint("LoginAndRegister", __name__, url_prefix="/")


@bp.route("/checkcode", methods=['GET', 'POST'])
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


@bp.route("/sendEmailCode", methods=['GET', 'POST'])
def sendEmailCode():
    email = request.args.get("email")
    send_type = request.args.get("type")
    if email is None or send_type is None:
        return jsonify({'code': 600, 'msg': '请求参数错误', 'data': ''})
    # 检查是否已经存在此邮箱
    user = UserInfo.query.filter_by(email=email).first()
    if not user:
        # 生成验证码并发送
        source = string.digits * 6
        captcha = random.sample(source, 6)
        captcha = "".join(captcha)
        message = Message(subject="", recipients=[email], body=f"您的验证码是：{captcha}")
        email_code = EmailCode(email=email, code=captcha, create_time=datetime.now())
        db.session.add(email_code)
        db.session.commit()
        try:
            mail.send(message)
        except Exception as e:
            print("send error" + str(e))
            return "send error" + str(e)
        else:
            return "Sent successfully"
    else:
        return jsonify({"code": 200, "msg": "邮箱已经被注册", "data": None})


@bp.route("/register", methods=['GET', 'POST'])
def register():
    sessionCode = session.get("check_code")
    checkcode = request.args.get("checkcode")
    if sessionCode == None or checkcode == None:
        return jsonify({'code': 600, 'msg': '请求参数错误', 'data': ''})
    if sessionCode.lower() == checkcode.lower():
        return jsonify({'code': 200, 'msg': '验证成功', 'data': ''})
    else:
        return jsonify({'code': 200, 'msg': '验证失败', 'data': ''})

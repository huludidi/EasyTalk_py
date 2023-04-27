from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from exts import mail, db
from flask_mail import Message
from datetime import datetime
from models import UserInfo
from .forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random

bp = Blueprint("user", __name__, url_prefix="/user")


# @bp.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         return jsonify({"code": 200, "msg": "暂未有此用户", "data": None})
#     else:
#         form = LoginForm(request.form)
#         if form.validate():
#             email = form.email.data
#             password = form.password.data
#             user = UserInfo.query.filter_by(email=email).first()
#             if not user:
#                 return jsonify({"code": 200, "msg": "暂未有此用户", "data": None})
#
#             if check_password_hash(user.password, password):
#                 # 提交给cookie
#                 session['user_id'] = user.id
#                 return redirect(url_for("question.index"))
#             else:
#                 return redirect(url_for("user.login"))
#         else:
#             print(form.errors)
#             return redirect(url_for("user.login"))
#
#
# @bp.route("/register", methods=['GET', 'POST'])
# def register():
#     if request.method == 'GET':
#         return "注册界面get"
#     else:
#         # 验证用户提交的邮箱和验证码是否对应
#         # 表单验证：flask-wtf
#
#         # 拿到前端上传的表单数据
#         form = RegisterForm(request.form)
#         if form.validate():
#             email = form.email.data
#             nickname = form.nickname.data
#             password = form.password.data
#
#             user = UserInfo(email=email, nick_name=nickname, password=generate_password_hash(password))
#             db.session.add(user)
#             db.session.commit()
#             return jsonify({"code": 200, "msg": "登录成功", "data": None})
#         else:
#             return jsonify({"code": 200, "msg": "登录失败", "data": None})
#

@bp.route("/captcha/email")
def get_email_captcha():
    # /captcha/email/<email>
    # get_email_captcha(email)拿到参数
    # /captcha/email?email=xxx@qq.com 两种传参方式
    email = request.form.get("email")
    print(email)
    source = string.digits * 4
    captcha = random.sample(source, 4)
    captcha = "".join(captcha)
    message = Message(subject="验证码", recipients=[email], body=f"您的验证码是：{captcha}")
    mail.send(message)
    # email_captcha = EmailCaptchaModel(email=email, captcha=captcha)
    # db.session.add(email_captcha)
    # db.session.commit()
    # {code:200/400/500, message:“”, data:{}}
    return jsonify({"code": 200, "msg": f"{email}", "data": None})


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
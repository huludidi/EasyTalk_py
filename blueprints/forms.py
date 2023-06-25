import datetime

import wtforms

from wtforms import Form
from wtforms.validators import Email, Length, InputRequired, Regexp, DataRequired

from functions import CustomResponse
from models import UserInfo, EmailCode
from exts import db


class RegisterForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！"), Length(max=150, message="邮箱过长")])
    emailCode = wtforms.StringField(validators=[Length(min=6, max=6, message="验证码格式错误！"), ])
    nickName = wtforms.StringField(validators=[Length(min=3, max=20, message="用户名格式错误")])
    password = wtforms.StringField(validators=[Length(min=8, max=18, message="密码格式错误！"),
                                               Regexp('^(?![0-9a-zA-Z]+$)[a-zA-Z0-9~!@#$%^&*?_-]{1,50}$',
                                                      message="密码格式错误")])

    # 自定义验证邮箱是否已经被注册
    def validate_email(self, field):
        email = field.data
        user = UserInfo.query.filter_by(email=email).first()
        if user:
            return CustomResponse(info="邮箱已被注册").to_dict()

    #     验证昵称是否被注册
    def validate_nickName(self, field):
        nickName = field.data
        user = UserInfo.query.filter_by(nick_name=nickName).first()
        if user:
            return CustomResponse(info="昵称已被注册").to_dict()


class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！")])
    password = wtforms.StringField(validators=[Length(min=4, max=20, message="密码格式错误！")])
    checkCode = wtforms.StringField(validators=[DataRequired(message="请输入验证码")])

class ResetPwdForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误！"), Length(max=150, message="邮箱过长")])
    emailCode = wtforms.StringField(validators=[Length(min=6, max=6, message="验证码格式错误！"), ])
    checkCode = wtforms.StringField(validators=[DataRequired(message="请输入验证码")])
    password = wtforms.StringField(validators=[Length(min=8, max=18, message="密码格式错误！"),
                                               Regexp('^(?![0-9a-zA-Z]+$)[a-zA-Z0-9~!@#$%^&*?_-]{1,50}$',
                                                      message="密码格式错误")])

class UpdateForm(wtforms.Form):
    sex = wtforms.StringField(validators=[DataRequired(message="请输入性别")])
    personDescription = wtforms.StringField(validators=[Length(min=3,max=150,message="内容过长或过短")])
    school = wtforms.StringField(validators=[DataRequired(message="请选择学校")])
    # schoolEmail=wtforms.StringField(validators=[DataRequired(), Email()])
    nickName=wtforms.StringField(validators=[DataRequired(message="请输入昵称")])

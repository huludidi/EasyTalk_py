import json

from flask import Flask, session, g
from exts import db, mail
from models import SysSetting
import config
from blueprints.LoginAndRegister import bp as qa_bp
from blueprints.user import bp as user_bp
from flask_migrate import Migrate
from static.syssetting import Audit, Comment, Email, Like, Post, Register

app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)
app.register_blueprint(qa_bp)
app.register_blueprint(user_bp)

db.init_app(app)
migrate = Migrate(app, db)
mail.init_app(app)


# 钩子函数
@app.before_request
def my_before_request():
    syssetting = SysSetting.query.filter_by(code="register").first()
    register_dict = json.loads(syssetting.json_content)
    register = Register(register_dict.get("registerWelcomInfo"))
    setattr(g, "registerInfo", register)

#
# @app.context_processor
# # 上下文处理器,每个模板中都会有user
# def my_context_processor():
#     return {"user": g.user}


if __name__ == '__main__':
    app.run()

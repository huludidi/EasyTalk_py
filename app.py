import json

from flask import Flask, session, g
from exts import db, mail
from models import SysSetting
import config
from blueprints.LoginAndRegister import bp as lar_bp
from blueprints.ForumBoard import bp as fb_bp
from blueprints.ForumArticle import bp as fa_bp
from flask_migrate import Migrate
from static.syssetting import Audit, Comment, Email, Like, Post, Register

app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)
app.register_blueprint(lar_bp)
app.register_blueprint(fb_bp)
app.register_blueprint(fa_bp)

db.init_app(app)
migrate = Migrate(app, db)
mail.init_app(app)


# 钩子函数
@app.before_request
def my_before_request():
    # 注册设置
    syssetting = SysSetting.query.filter_by(code="register").first()
    register_dict = json.loads(syssetting.json_content)
    register = Register(register_dict.get("registerWelcomInfo"))
    setattr(g, "registerInfo", register)
    # 评论设置
    syssetting = SysSetting.query.filter_by(code="comment").first()
    comment_dict = json.loads(syssetting.json_content)
    comment = Comment(comment_dict.get("commentDayCountThreshold"), comment_dict.get("commentIntegral"),
                      comment_dict.get("commentOpen"))
    setattr(g, "commentInfo", comment)


#
# @app.context_processor
# # 上下文处理器,每个模板中都会有user
# def my_context_processor():
#     return {"user": g.user}


if __name__ == '__main__':
    app.run()

import json

from flask import Flask, g, jsonify
from flask.cli import with_appcontext
from werkzeug.exceptions import BadRequest

from exts import db, mail, cache
from models import SysSetting
import config
from blueprints.LoginAndRegister import bp as lar_bp
from blueprints.ForumBoard import bp as fb_bp
from blueprints.ForumArticle import bp as fa_bp
from blueprints.ForumComment import bp as fc_bp
from blueprints.File import bp as f_bp
from blueprints.Ucenter import bp as uc_bp
from blueprints.ManageArticle import bp as ma_bp
from blueprints.ManageBoard import bp as mb_bp
from blueprints.SysSetting import bp as ss_bp
from blueprints.ManageUserInfo import bp as mui_bp
from blueprints.ManageDataShow import bp as mds_bp
from blueprints.School import bp as s_bp
from blueprints.ForumResource import bp as fr_bp


from flask_migrate import Migrate
from static.globalDto import Audit, Comment, Like, Post, Register, SysSettingDto

app = Flask(__name__)
# 绑定配置文件
app.config.from_object(config)
app.register_blueprint(lar_bp)
app.register_blueprint(fa_bp)
app.register_blueprint(fb_bp)
app.register_blueprint(fc_bp)
app.register_blueprint(f_bp)
app.register_blueprint(uc_bp)
app.register_blueprint(ma_bp)
app.register_blueprint(mb_bp)
app.register_blueprint(ss_bp)
app.register_blueprint(mui_bp)
app.register_blueprint(mds_bp)
app.register_blueprint(s_bp)
app.register_blueprint(fr_bp)


db.init_app(app)
migrate = Migrate(app, db)
mail.init_app(app)
cache.init_app(app)

with app.app_context():
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
        comment = Comment(comment_dict.get("commentDayCountThreshold"),
                          comment_dict.get("commentOpen"))
        setattr(g, "commentInfo", comment)
        # 审核
        syssetting = SysSetting.query.filter_by(code="audit").first()
        audit_dict = json.loads(syssetting.json_content)
        audit = Audit(audit_dict.get("commentAudit"), audit_dict.get("postAudit"))
        setattr(g, "auditInfo", audit)
        # 附件
        syssetting = SysSetting.query.filter_by(code="post").first()
        post_dict = json.loads(syssetting.json_content)
        post = Post(post_dict.get("attachmentSize"), post_dict.get("dayImageUploadCount"),
                    post_dict.get("postDayCountThreshold"))
        setattr(g, "postInfo", post)

        # 点赞
        syssetting = SysSetting.query.filter_by(code="like").first()
        like_dict = json.loads(syssetting.json_content)
        like = Like(like_dict.get("likeDayCountThreshold"))
        setattr(g, "likeInfo", like)


@app.errorhandler(500)
def code_500_error(error):
    error_message = {
        'code': 500,
        'error': error.description,
        'info': ' 服务器返回错误',
    }
    return jsonify(error_message), 500


@app.errorhandler(404)
def code_404_error(error):
    error_message = {
        'code': 404,
        'error': error.description,
        'info': ' 请求地址不存在',
    }
    return jsonify(error_message), 404


@app.errorhandler(BadRequest)
def code_600_error(error):
    error_message = {
        'code': 400,
        'error': error.description,
        'info': '请求参数错误',
    }
    return jsonify(error_message)


@app.errorhandler(422)
def code_500_error(error):
    error_message = {
        'code': 422,
        'error': error.description,
        'info': '数据库操作失败',
    }
    return jsonify(error_message), 422

def create_cache():
    system_settings = SysSetting.query.all()  # 从数据库中获取系统设置数据
    for setting in system_settings:
        cache.set(setting.code, json.loads(setting.json_content))  # 将数据放入缓存


if __name__ == '__main__':
    print("111")
    app.run()

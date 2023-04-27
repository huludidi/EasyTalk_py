from flask import Flask, session, g
from exts import db, mail
from models import UserInfo
import config
from blueprints.LoginAndRegister import bp as qa_bp
from blueprints.user import bp as user_bp
from flask_migrate import Migrate

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
    user_id = session.get("user_id")
    if user_id:
        user = UserInfo.query.get(user_id)
        setattr(g, "user", user)
    else:
        setattr(g, "user", None)


# 上下文处理器,每个模板中都会有user
def my_context_processor():
    return {"user": g.user}


if __name__ == '__main__':
    app.run()

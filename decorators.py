from functools import wraps
from flask import g, redirect, url_for


def login_required(func):
    # 保留func信息
    @wraps(func)
    #     万能参数
    def inner(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        else:
            return redirect(url_for("user.login"))

    return inner

from functools import wraps
from flask import g, request, session, abort

from CustomResponse import CustomResponse


def login_required(func):
    # 保留func信息
    @wraps(func)
    #     万能参数
    def inner(*args, **kwargs):
        if session.get('userInfo'):
            return func(*args, **kwargs)
        else:
            abort(500, description="请先登录")

    return inner


def check_params(func):
    @wraps(func)
    def inner(*args, **kwargs):
        for key, value in request.form.items():
            if not value:
                return CustomResponse(code=600).to_dict()
        return func(*args, **kwargs)

    return inner

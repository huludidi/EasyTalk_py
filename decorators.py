from datetime import datetime
from functools import wraps

from flask import request, session, abort, jsonify, g

from functions import CustomResponse
from static.enums import UserOperFrequencyTypeEnum

def check_admin(func):
    # 保留func信息
    @wraps(func)
    #     万能参数
    def inner(*args, **kwargs):
        user = session.get('userInfo')
        if user and user['isAdmin']:
            return func(*args, **kwargs)
        else:
            abort(500, description="您非管理员，请勿操作")

    return inner
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


# 频次校验装饰器
def rate_limit(limit_type):
    """
    频次校验装饰器
    :param limit_type: 校验类型枚举
    :param limit_count: 限制的请求次数
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            user_id = session['userInfo']['userId']
            if not user_id:
                return jsonify({'message': '无法识别用户信息'}), 400

            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            if not session.get(user_id):
                session[user_id] = {
                    'article': 0,
                    'comment': 0,
                    'like': 0,
                    'image': 0,
                    'updated_at': today
                }  # 记录用户访问次数

            # 获取用户的操作计数和最近更新时间
            access_count = session[user_id]
            last_updated_at = datetime.strptime(access_count['updated_at'], '%Y-%m-%d')
            # 如果最近更新时间与当前日期不同，则重置用户的操作计数
            if last_updated_at.date() < datetime.now().date():
                access_count['comment'] = 0
                access_count['article'] = 0
                access_count['image'] = 0
                access_count['like'] = 0
                access_count['updated_at'] = today

            #     发布评论频次校验
            if limit_type == UserOperFrequencyTypeEnum.POST_COMMENT:
                if access_count['comment'] >= g.commentInfo.getcommentDayCountThreshold():
                    abort(400, description="您今日评论数量过多，请明天再来吧~")
                else:
                    access_count['comment'] += 1
            # 发布文章频次校验
            elif limit_type == UserOperFrequencyTypeEnum.POST_ARTICLE:
                if access_count['article'] >= g.postInfo.getpostDayCountThreshold():
                    abort(400, description="您今日发布的内容数量过多，请明天再来吧~")
                else:
                    access_count['article'] += 1
            # 上传图片频次校验
            elif limit_type == UserOperFrequencyTypeEnum.IMAGE_UPLOAD:
                if access_count['image'] >= g.postInfo.getdayImageUploadCount():
                    abort(400, description="您今日发布的图片数量过多，请明天再来吧~")
                else:
                    access_count['image'] += 1
            # 点赞频次校验
            elif limit_type == UserOperFrequencyTypeEnum.DO_LIKE:
                if access_count['like'] >= g.likeInfo.getlikeDayCountThreshold():
                    abort(400, description="您今日点赞过多，请明天再来吧~")
                else:
                    access_count['like'] += 1
            # 更新用户的操作计数和最近更新时间，并返回被装饰函数的结果
            session[user_id] = access_count

            return func(*args, **kwargs)

        return inner

    return wrapper

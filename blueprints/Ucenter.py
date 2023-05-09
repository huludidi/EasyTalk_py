from math import ceil

from flask import Blueprint, request, abort, session
from sqlalchemy import func

from blueprints.forms import UpdateForm
from decorators import check_params, login_required
from exts import db
from functions import SuccessResponse, uploadFile2Local
from models import UserInfo, ForumArticle, LikeRecord, ForumComment, UserMessage
from static.enums import globalinfoEnum, FileUploadTypeEnum, MessageTypeEnum

bp = Blueprint("Ucenter", __name__, url_prefix="/ucenter")


@bp.route("/getUserInfo", methods=['POST'])
@check_params
def getUserInfo():
    userid = request.values.get('userId')
    user = UserInfo.query.filter_by(user_id=userid).first()
    current_user = session['userInfo']
    if not user or user.status == 0:
        abort(404)
    #     获取用户文章
    article = ForumArticle.query.filter_by(author_id=user.user_id).all()
    article = article.filter_by(status=1, audit=1)
    postcount = len(article)  # 文章数量

    likecord = LikeRecord.query.filter_by(author_user_id=user.user_id).all()
    likecount = len(likecord)  # 获赞数量

    result = {
        'userId': user.user_id,
        'nickName': user.nick_name,
        'sex': user.sex,
        'personDescription': user.person_description,
        'joinTime': user.join_time.strftime('%Y-%m-%d'),
        'lastLoginTime': user.last_login_time.strftime('%Y-%m-%d'),
        'postCount': postcount,
        'likeCount': likecount,
        'school': user.school
    }
    return SuccessResponse(data=result)


@bp.route("/loadUserArticle", methods=['POST'])
@check_params
def loadUserArticle():
    userid = request.values.get('userId')
    type = request.values.get('type')
    page = int(request.values.get('pageNo'))
    userinfo = session['userInfo']
    user = UserInfo.query.filter_by(user_id=userid).first()
    list = []
    result = {"pageSize": globalinfoEnum.PageSize.value, "pageNo": page}
    totalCount = 0
    if not user or user.status == 0:
        abort(404)
    # 发布的文章
    if type == '0':
        articles = ForumArticle.query \
            .filter_by(author_id=userid) \
            .order_by(ForumArticle.post_time.desc())
        # 若非本用户，只能看审核通过的文章
        if userinfo['userId'] != userid:
            articles = articles.filter_by(status=1, audit=1)
        totalCount = len(articles.all())
        #     分页
        articles = articles.paginate(page=page, per_page=globalinfoEnum.PageSize.value, error_out=False).items
        # 加入list
        for item in articles:
            item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
            item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            list.append(item.to_dict())
        result['totalCount'] = totalCount
        result['pageTotal'] = ceil(totalCount / globalinfoEnum.PageSize.value)
        result['list'] = list
    # 评论过的文章
    elif type == '1':
        # 获取用户评论过的所有文章ID
        commented_article_ids = set(
            [comment.article_id for comment in ForumComment.query.filter_by(user_id=userid).all()])
        # 查询所有被评论过的文章
        articles = ForumArticle.query.filter(ForumArticle.article_id.in_(commented_article_ids))
        totalCount = len(articles.all())
        articles = articles.paginate(page=page, per_page=globalinfoEnum.PageSize.value, error_out=False).items
        for item in articles:
            item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
            item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            list.append(item.to_dict())
        result['totalCount'] = totalCount
        result['pageTotal'] = ceil(totalCount / globalinfoEnum.PageSize.value)
        result['list'] = list
    # 点赞过的文章
    elif type == '2':
        # 获取用户点赞过的所有文章ID
        liked_article_ids = set(
            [like.object_id for like in LikeRecord.query.filter_by(user_id=userid, op_type=0).all()])
        # 查询所有被评论过的文章
        articles = ForumArticle.query.filter(ForumArticle.article_id.in_(liked_article_ids))
        totalCount = len(articles.all())
        articles = articles.paginate(page=page, per_page=globalinfoEnum.PageSize.value, error_out=False).items
        for item in articles:
            item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
            item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            list.append(item.to_dict())
        result['totalCount'] = totalCount
        result['pageTotal'] = ceil(totalCount / globalinfoEnum.PageSize.value)
        result['list'] = list
    return SuccessResponse(data=result)


@bp.route("/updateUserInfo", methods=['POST'])
@login_required
@check_params
def updateUserInfo():
    form = UpdateForm(request.form)
    if form.validate():
        sex = form.sex.data
        persondescription = form.personDescription.data
        school = form.school.data
        schoolemail = form.schoolEmail.data
        avatar = request.files.get('avatar')
        userinfo = session['userInfo']

        user = UserInfo.query.filter_by(user_id=userinfo['userId']).first()
        user.sex = sex
        user.person_description = persondescription
        user.school = school
        user.school_email = schoolemail

        if avatar:
            uploadFile2Local(avatar, userinfo['userId'], FileUploadTypeEnum.AVATAR)
        return SuccessResponse()
    else:
        print(form.errors)
        abort(400)


@bp.route("/getMessageCount", methods=['POST'])
def getMessageCount():
    userinfo = session['userInfo']
    total = UserMessage.query.filter_by(status=1, received_user_id=userinfo['userId']).count()
    unread_counts = db.session.query(
        UserMessage.message_type,
        func.count(UserMessage.message_id)
    ).filter(
        UserMessage.received_user_id == userinfo['userId'],
        UserMessage.status == 1  # 只统计未读信息
    ).group_by(
        UserMessage.message_type
    ).all()
    result = {
        "total": 0,
        "sys": 0,
        "reply": 0,
        "likePost": 0,
        "likeComment": 0,
    }
    for message_type, count in unread_counts:
        message_type_obj = MessageTypeEnum.getByType(message_type)
        if message_type_obj:
            result[message_type_obj.value.get('code')] = count
    result['total'] = total
    return SuccessResponse(data=result)


@bp.route("/loadMessageList", methods=['POST'])
@check_params
def loadMessageList():
    code = request.values.get('code')
    pageNo = int(request.values.get('pageNo'))
    typeEnum = MessageTypeEnum.getByCode(code)
    userinfo = session['userInfo']
    result = {
        'totalCount': 0,
        'pageSize': globalinfoEnum.PageSize.value,
        'pageNo': pageNo,
        'pageTotal': 0,
        'list': []
    }
    totalCount = 0
    if not typeEnum:
        abort(400)
    if not pageNo or pageNo == 1:
        UserMessage.query \
            .filter_by(received_user_id=userinfo['userId'], message_type=typeEnum.value.get('type'), status=1) \
            .update({UserMessage.status: 2})

    usermessage = UserMessage.query \
        .filter_by(received_user_id=userinfo['userId'], message_type=typeEnum.value.get('type')) \
        .order_by(UserMessage.create_time.desc())
    totalCount = usermessage.count()
    usermessage = usermessage.paginate(page=pageNo, per_page=globalinfoEnum.PageSize.value, error_out=False) \
        .items

    result['totalCount'] = totalCount
    result['pageTotal'] = ceil(totalCount / globalinfoEnum.PageSize.value)
    for item in usermessage:
        item.create_time = item.create_time.strftime('%Y-%m-%d %H:%M:%S')
        result['list'].append(item.to_dict())
    db.session.commit()
    return SuccessResponse(data=result)

from datetime import datetime
from math import ceil

from flask import Blueprint, request, abort, session
from sqlalchemy import func

from blueprints.forms import UpdateForm
from decorators import check_params, login_required
from exts import db
from functions import SuccessResponse, uploadFile2Local
from models import UserInfo, ForumArticle, LikeRecord, ForumComment, UserMessage, SchoolInfo, EmailCode
from static.enums import globalinfoEnum, FileUploadTypeEnum, MessageTypeEnum

bp = Blueprint("Ucenter", __name__, url_prefix="/ucenter")


@bp.route("/getUserInfo", methods=['POST'])
@check_params
def getUserInfo():
    userid = request.values.get('userId')
    user = UserInfo.query.filter_by(user_id=userid).first()
    if not user or user.status == 0:
        abort(404, description="该用户已被禁用")
    #     获取用户文章
    article = ForumArticle.query.filter_by(author_id=user.user_id)
    article = article.filter_by(status=1, audit=1).all()
    readcount = 0
    for item in article:
        readcount += item.read_count
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
        'readCount': readcount,
        'postCount': postcount,
        'likeCount': likecount,
        'school': user.school,
        'schoolEmail': user.school_email
    }
    return SuccessResponse(data=result)


@bp.route("/loadUserArticle", methods=['POST'])
def loadUserArticle():
    userid = request.values.get('userId')
    type = request.values.get('type')
    page = request.values.get('pageNo')
    if not page:
        page = 1
    else:
        page = int(page)
    userinfo = session.get("userInfo")
    user = UserInfo.query.filter_by(user_id=userid).first()
    list = []
    result = {"pageSize": 10, "pageNo": page}
    totalCount = 0
    if not user or user.status == 0:
        abort(404)
    # 发布的文章
    if type == '0':
        articles = ForumArticle.query \
            .filter_by(author_id=userid) \
            .order_by(ForumArticle.post_time.desc())
        # 若非本用户，只能看审核通过的文章
        if not userinfo or userinfo['userId'] != userid:
            articles = articles.filter_by(status=1, audit=1)
        totalCount = len(articles.all())
        #     分页
        articles = articles.paginate(page=page, per_page=10, error_out=False).items
        # 加入list
        for item in articles:
            item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
            item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            list.append(item.to_dict())
        result['totalCount'] = totalCount
        result['pageTotal'] = ceil(totalCount / 10)
        result['list'] = list
    # 评论过的文章
    elif type == '1':
        # 获取用户评论过的所有文章ID
        commented_article_ids = set(
            [comment.article_id for comment in ForumComment.query.filter_by(user_id=userid).all()])
        # 查询所有被评论过的文章
        articles = ForumArticle.query.filter(ForumArticle.article_id.in_(commented_article_ids))
        totalCount = len(articles.all())
        articles = articles.paginate(page=page, per_page=10, error_out=False).items
        for item in articles:
            item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
            item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            list.append(item.to_dict())
        result['totalCount'] = totalCount
        result['pageTotal'] = ceil(totalCount / 10)
        result['list'] = list
    # 点赞过的文章
    elif type == '2':
        # 获取用户点赞过的所有文章ID
        liked_article_ids = set(
            [like.object_id for like in LikeRecord.query.filter_by(user_id=userid, op_type=0).all()])
        # 查询所有被评论过的文章
        articles = ForumArticle.query.filter(ForumArticle.article_id.in_(liked_article_ids))
        totalCount = len(articles.all())
        articles = articles.paginate(page=page, per_page=10, error_out=False).items
        for item in articles:
            item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
            item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
            list.append(item.to_dict())
        result['totalCount'] = totalCount
        result['pageTotal'] = ceil(totalCount / 10)
        result['list'] = list
    return SuccessResponse(data=result)


@bp.route("/updateUserInfo", methods=['POST'])
@login_required
def updateUserInfo():
    form = UpdateForm(request.form)
    if form.validate():
        sex = form.sex.data
        persondescription = form.personDescription.data
        school = form.school.data
        # schoolemail = form.schoolEmail.data
        nickName = form.nickName.data
        avatar = request.files.get('avatar')
        userinfo = session['userInfo']

        db_info=SchoolInfo.query.filter_by(ch_name=school).first()
        if not db_info:
            abort(400,description="系统暂不支持此学校")
        user = UserInfo.query.filter_by(user_id=userinfo['userId']).first()
        user.sex = sex
        user.person_description = persondescription
        user.school = school
        # user.school_email = schoolemail
        user.nick_name=nickName
        if avatar:
            uploadFile2Local(avatar, userinfo['userId'], FileUploadTypeEnum.AVATAR)
        # 更新session
        session['userInfo']['school']=school
        session['userInfo']['schoolEmail']=user.school_email
        session['userInfo']['nickName']=nickName
        # 更新文章
        update_stmt = (
            ForumArticle.__table__
            .update()
            .where(ForumArticle.author_id == userinfo['userId'])
            .values(nick_name=nickName)
        )
        db.session.execute(update_stmt)
        update_stmt = (
            ForumArticle.__table__
            .update()
            .where(ForumArticle.author_id == userinfo['userId'])
            .values(author_school=school)
        )
        db.session.execute(update_stmt)
        db.session.commit()
        return SuccessResponse(data=session['userInfo'])
    else:
        print(form.errors)
        abort(400,description=form.errors)

@bp.route("/bindSchoolEmail", methods=['POST'])
@login_required
@check_params
def bindSchoolEmail():
    userId=session['userInfo']['userId']
    schoolEmail=request.values.get('schoolEmail')
    code=request.values.get('emailCode')

    #  检查邮箱验证码
    dbInfo = EmailCode.query.get((schoolEmail, code))
    if dbInfo is None:
        abort(400, description="邮箱验证码不正确")
    if dbInfo.status != 0 or (datetime.now() - dbInfo.create_time).seconds > 900:
        abort(400, description="邮箱验证码已失效")
    dbInfo.status = 1

    user=UserInfo.query.filter_by(user_id=userId).first()
    user.school_email=schoolEmail
    db.session.commit()
    return SuccessResponse()

@bp.route("/cencelBindSchoolEmail", methods=['POST'])
@login_required
@check_params
def cencelBindSchoolEmail():
    userInfo = session['userInfo']
    user = UserInfo.query.filter_by(user_id=userInfo['userId']).first()
    if not user.school_email:
        abort(400,description="用户还未绑定邮箱")
    user.school_email=None
    db.session.commit()
    session['userInfo']['schoolEmail']=None
    return SuccessResponse(data=session['userInfo'])

@bp.route("/getMessageCount", methods=['POST'])
def getMessageCount():
    userinfo = session.get("userInfo")
    result = {
        "total": 0,
        "sys": 0,
        "reply": 0,
        "likePost": 0,
        "likeComment": 0,
    }
    if not userinfo:
        return SuccessResponse(data=result)
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

    for message_type, count in unread_counts:
        message_type_obj = MessageTypeEnum.getByType(message_type)
        if message_type_obj:
            result[message_type_obj.value.get('code')] = count
    result['total'] = total
    return SuccessResponse(data=result)


@bp.route("/loadMessageList", methods=['POST'])
def loadMessageList():
    code = request.values.get('code')
    if not code:
        abort(400)
    pageNo = request.values.get('pageNo')
    if not pageNo:
        pageNo = 1
    else:
        pageNo = int(pageNo)
    typeEnum = MessageTypeEnum.getByCode(code)
    userinfo = session['userInfo']
    result = {
        'totalCount': 0,
        'pageSize': 10,
        'pageNo': pageNo,
        'pageTotal': 0,
        'list': []
    }
    totalCount = 0
    if not typeEnum:
        abort(400)
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

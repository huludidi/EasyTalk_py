from datetime import datetime
from math import ceil

from flask import Blueprint, request
from decorators import check_params, check_admin
from exts import db
from functions import SuccessResponse
from models import  UserInfo, ForumArticle, ForumComment, UserMessage
from static.enums import globalinfoEnum, MessageTypeEnum

bp = Blueprint("ManageUserInfo", __name__, url_prefix="/manageUser")


@bp.route("/loadUserList", methods=['POST'])
@check_admin
def loadUserList():
    pageNo = request.values.get('pageNo')
    pageSize=request.values.get('pageSize')
    nickNameFuzzy = request.values.get('nickNameFuzzy')
    sex = request.values.get('sex')
    status = request.values.get('status')
    school=request.values.get('school')
    users = UserInfo.query.order_by(UserInfo.join_time.desc())
    if not pageNo:
        pageNo = None
    else:
        pageNo = int(pageNo)
    if not pageSize:
        pageSize=globalinfoEnum.PageSize.value
    else:
        pageSize=int(pageSize)
    if nickNameFuzzy:
        users = users.filter(UserInfo.nick_name.like(f'%{nickNameFuzzy}%'))
    if school:
        users = users.filter(UserInfo.school.like(f'%{school}%'))
    if sex:
        users = users.filter_by(sex=int(sex))
    if status:
        users = users.filter_by(status=int(status))

    totalcount = users.count()
    users = users.paginate(page=pageNo, per_page=pageSize, error_out=False)
    list = []
    for item in users.items:
        item.join_time = item.join_time.strftime('%Y-%m-%d %H:%M:%S')
        item.last_login_time = item.last_login_time.strftime('%Y-%m-%d %H:%M:%S')
        dict = item.to_dict()
        dict.pop('password')
        list.append(dict)
    result = {
        'totalCount': totalcount,
        'pageSize': pageSize,
        'pageNo': pageNo,
        'pageTotal': ceil(totalcount / pageSize),
        'list': list
    }
    return SuccessResponse(data=result)


@bp.route("/updateUserStatus", methods=['POST'])
@check_admin
@check_params
def updateUserStatus():
    userId = request.values.get('userId')
    status = int(request.values.get('status'))
    if status == 0:
        # 删除该用户所有文章、评论
        ForumArticle.query.filter_by(author_id='1').update({ForumArticle.status: -1})
        ForumComment.query.filter_by(user_id=userId).update({ForumComment.status: -1})
    user = UserInfo.query.filter_by(user_id=userId).first()
    user.status = status
    db.session.commit()
    return SuccessResponse()


@bp.route("/sendMessage", methods=['POST'])
@check_admin
@check_params
def sendMessage():
    userId = request.values.get('userId')
    message = request.values.get('message')
    usermessage = UserMessage(received_user_id=userId,
                              message_type=MessageTypeEnum.SYS.value.get('type'),
                              message_content=message,
                              create_time=datetime.now())
    db.session.add(usermessage)
    db.session.commit()
    return SuccessResponse()

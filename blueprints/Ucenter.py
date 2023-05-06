from flask import Blueprint, request, abort, session

from decorators import check_params
from functions import SuccessResponse, convert_line_to_tree
from models import ForumBoard, UserInfo, ForumArticle, LikeRecord

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
    if user.user_id != current_user.get('userId'):
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

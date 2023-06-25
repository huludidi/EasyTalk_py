from flask import Blueprint
from sqlalchemy import func
from decorators import check_admin
from datetime import datetime, timedelta
from exts import db
from functions import SuccessResponse
from models import UserInfo, SchoolInfo, ForumArticle, ForumBoard

bp = Blueprint("ManageDataShow", __name__, url_prefix="/statistics")


@bp.route('/recentJoinUser', methods=['POST'])
@check_admin
def RecentLoginUsers():
    # 计算一个月前的日期
    one_month_ago = datetime.now() - timedelta(days=30)
    # 查询数据库中最近一个月加入的用户
    users = UserInfo.query.filter(UserInfo.join_time >= one_month_ago).all()
    result = []
    for user in users:
        user.join_time = user.join_time.strftime('%m月%d日')
        user.last_login_time = user.last_login_time.strftime('%Y-%m-%d %H:%M:%S')
        dict_user = user.to_dict()
        dict_user.pop('password')
        result.append(dict_user)
    return SuccessResponse(data=result)


@bp.route('/scatterPlot', methods=['POST'])
@check_admin
def scatterPlot():
    schoolgroup = db.session.query(UserInfo.school, func.count('*').label('count')).group_by(
        UserInfo.school).all()
    result = []
    for row in schoolgroup:
        school = SchoolInfo.query.filter_by(ch_name=row.school).first()
        if school:
            info = {
                'ch_name': row.school,
                'count': row.count,
                'longitude': school.longitude,
                'latitude': school.latitude
            }
            result.append(info)
    return SuccessResponse(data=result)


@bp.route('/articleTypeData', methods=['POST'])
def articleTypeData():
    boards = ForumBoard.query.filter_by(p_board_id=0).all()
    result = []
    for board in boards:
        count = ForumArticle.query.filter_by(p_board_id=board.board_id, status=1, audit=1).count()
        item = {
            'boardName': board.board_name,
            'count': count
        }
        result.append(item)
    return SuccessResponse(data=result)

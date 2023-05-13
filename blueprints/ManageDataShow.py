import time
from geopy.geocoders import Nominatim

from flask import Blueprint
from sqlalchemy import func
from decorators import check_admin
from datetime import datetime, timedelta
from exts import db
from functions import SuccessResponse
from models import UserInfo, SchoolInfo, ForumArticle, ForumBoard

bp = Blueprint("ManageDataShow", __name__, url_prefix="/statistics")


@bp.route('/recentLoginUsers', methods=['POST'])
@check_admin
def RecentLoginUsers():
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    users = UserInfo.query.filter(UserInfo.last_login_time >= two_days_ago).limit(8).all()
    result = []
    for user in users:
        user.join_time = user.join_time.strftime('%Y-%m-%d %H:%M:%S')
        user.last_login_time = user.last_login_time.strftime('%Y-%m-%d %H:%M:%S')
        dict_user=user.to_dict()
        dict_user.pop('password')
        result.append(dict_user)
    return SuccessResponse(data=result)


@bp.route('/scatterPlot', methods=['POST'])
@check_admin
def scatterPlot():
    schoolgroup = db.session.query(UserInfo.school, func.count('*').label('count')).group_by(
        UserInfo.school).all()
    result = {}
    for row in schoolgroup:
        school = SchoolInfo.query.filter_by(en_name=row.school).first()
        info = {
            'count': row.count,
            'longitude': school.longitude,
            'latitude': school.latitude
        }
        result[row.school] = info
    return SuccessResponse(data=result)


@bp.route('/articleTypeData', methods=['POST'])
@check_admin
def articleTypeData():
    boards = ForumBoard.query.filter_by(p_board_id=0).all()
    result = {}
    for board in boards:
        count = ForumArticle.query.filter_by(p_board_id=board.board_id, status=1, audit=1).count()
        result[board.board_name] = count
    return SuccessResponse(data=result)


def get_school_location(school):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(school)
    if location:
        return {'latitude': location.latitude, 'longitude': location.longitude}
    else:
        return {'error': f'Could not find location for {school}'}


@bp.route('/location', methods=['POST'])
def get_location():
    schools = SchoolInfo.query.filter(SchoolInfo.id > 108).all()
    for item in schools:
        location = get_school_location(item.en_name)
        item.latitude = location.get('latitude')
        item.longitude = location.get('longitude')
        db.session.commit()
        time.sleep(10)
    return SuccessResponse()

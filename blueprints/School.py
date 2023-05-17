import time
from geopy.geocoders import Nominatim

from flask import Blueprint
from sqlalchemy import func

from exts import db
from functions import SuccessResponse
from models import SchoolInfo, ForumArticle

bp = Blueprint("School", __name__, url_prefix="/school")


@bp.route('/schoolSort', methods=['POST'])
def schoolSort():
    schoolgroup = db.session.query(ForumArticle.author_school, func.count('*').label('count')).group_by(
        ForumArticle.author_school).all()
    result = []
    index = 1
    for row in schoolgroup:
        if index > 5:
            return
        school = SchoolInfo.query.filter_by(en_name=row.author_school).first()
        info = {
            'en_name': row.author_school,
            'count': row.count,
            'cover': school.cover,
            'ch_name': school.ch_name
        }
        result.append(info)
    return SuccessResponse(data=result)


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


def get_school_location(school):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(school)
    if location:
        return {'latitude': location.latitude, 'longitude': location.longitude}
    else:
        return {'error': f'Could not find location for {school}'}

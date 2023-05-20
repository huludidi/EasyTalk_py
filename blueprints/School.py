import time
from math import ceil

from geopy.geocoders import Nominatim

from flask import Blueprint, request, abort
from sqlalchemy import func

from exts import db
from functions import SuccessResponse
from models import SchoolInfo, ForumArticle
from static.enums import globalinfoEnum

bp = Blueprint("School", __name__, url_prefix="/school")


@bp.route('/getSchoolInfo', methods=['POST'])
def getSchoolInfo():
    pageNo = request.values.get('pageNo')
    pageSize = request.values.get('pageSize')
    if not pageNo:
        pageNo = 1
    else:
        pageNo = int(pageNo)
    if not pageSize:
        pageSize = globalinfoEnum.PageSize.value
    else:
        pageSize = int(pageSize)
    schoolNameFuzzy = request.values.get('schoolNameFuzzy')
    schools = SchoolInfo.query
    if schoolNameFuzzy:
        schools = schools.filter(SchoolInfo.ch_name.like(f'%{schoolNameFuzzy}%'))

    total = schools.count()
    schools = schools.paginate(page=pageNo, per_page=pageSize, error_out=False)
    list = []
    for item in schools:
        list.append(item.to_dict())
    result = {
        'totalCount': total,
        'pageSize': pageSize,
        'pageNo': pageNo,
        'pageTotal': ceil(total / pageSize),
        'list': list
    }
    return SuccessResponse(data=result)


@bp.route('/saveSchoolInfo', methods=['POST'])
def saveSchoolInfo():
    id = request.values.get('id')
    ch_name = request.values.get('ch_name')
    en_name = request.values.get('en_name')
    longitude = request.values.get('longitude')
    latitude = request.values.get('latitude')
    # 新增
    if not id:
        school = SchoolInfo(ch_name=ch_name, en_name=en_name, longitude=longitude, latitude=latitude)
        if not longitude or not latitude:
            location = get_school_location(school)
            school.latitude = location.get('latitude')
            school.longitude = location.get('longitude')
            db.session.add(school)
    # 修改
    else:
        school = SchoolInfo.query.filter_by(id=id).first()
        school.ch_name = ch_name
        school.en_name = en_name
        school.longitude = longitude
        school.latitude = latitude
    db.session.commit()
    return SuccessResponse()

@bp.route('/delSchool', methods=['POST'])
def delSchool():
    id=request.values.get('id')
    school=SchoolInfo.query.filter_by(id=id).first()
    db.session.delete(school)
    db.session.commit()
    return SuccessResponse()

@bp.route('/schoolSort', methods=['POST'])
def schoolSort():
    schoolgroup = db.session.query(
        ForumArticle.author_school,
        func.count('*').label('count')
    ).group_by(
        ForumArticle.author_school
    ).order_by(
        func.count('*').desc()
    ).all()
    result = []
    index = 1
    for row in schoolgroup:
        if index > 5:
            return
        school = SchoolInfo.query.filter_by(ch_name=row.author_school).first()
        if school:
            info = {
                'en_name': school.en_name,
                'count': row.count,
                'cover': school.cover,
                'ch_name': school.ch_name
            }
            result.append(info)
    return SuccessResponse(data=result)


@bp.route('/updateLocation', methods=['POST'])
def get_location():
    id = request.values.get('id')
    school = SchoolInfo.query.filter_by(id=id).first()
    location = get_school_location(school)
    school.latitude = location.get('latitude')
    school.longitude = location.get('longitude')
    db.session.commit()
    return SuccessResponse()


def get_school_location(school):
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(school.en_name)
    if not location:
        location = geolocator.geocode(school.ch_name)
    if not location:
        abort(400,description=f'Could not find location for {school}')
    return {'latitude': location.latitude, 'longitude': location.longitude}

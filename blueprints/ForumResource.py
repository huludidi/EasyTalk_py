import time
from math import ceil

import requests
from geopy.geocoders import Nominatim

from flask import Blueprint, request, abort, jsonify, session
from sqlalchemy import func

import config
from exts import db
from functions import SuccessResponse
from models import SchoolInfo, ForumArticle
from static.enums import globalinfoEnum

bp = Blueprint("ForumResource", __name__, url_prefix="/resource")


@bp.route('/getResource', methods=['POST'])
def getResource():
    target = request.values.get('target')

    # 获取用户经纬度
    current_user = session.get('userInfo')
    if not current_user:
        abort(400, description="请登录")
    school = SchoolInfo.query.filter_by(ch_name=current_user['school']).first()
    if school:
        lat = school.latitude
        lng = school.longitude
    else:
        abort(400, description="您的学校还未录入服务器，抱歉")
    # 调用百度地图API搜索附近的酒店、饭店等资源
    url = f"https://api.map.baidu.com/place/v2/search?query={target}&location={lat},{lng}&scope=2&radius=5000&output=json&ak={config.AK}"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 0:
        return SuccessResponse(data=data['results'])
    # 返回搜索结果
    return 400

import os
import random
import string
from datetime import datetime, timedelta
from math import ceil

from flask import Blueprint, request, session, abort, make_response, send_file, g

from functions import CustomResponse, SuccessResponse
import config

bp = Blueprint("File", __name__, url_prefix="/file")


@bp.route("/uploadImage", methods=['POST'])
def uploadImage():
    file = request.files.get('file')
    if not file:
        abort(400, description="文件不存在")
    # 重写文件名字
    filename = generate_random_string(15) + '.' + file.filename.rsplit('.', 1)[1].lower()
    if not allowed_file(filename):
        abort(400, description="文件格式不允许")
    file.save(config.IMAGE_PATH + config.IMAGE_FOLDER + '/' + filename)
    result = {
        'filename': config.IMAGE_FOLDER + "/" + filename
    }
    return SuccessResponse(data=result)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def generate_random_string(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


@bp.route("/getImage/<imageFolder>/<imageName>", methods=['GET', 'POST'])
def getImage(imageFolder, imageName):
    if request.method == 'GET' or request.method == 'POST':
        filepath = config.IMAGE_PATH + '/' + imageFolder + '/' + imageName
        if not os.path.exists(filepath):
            abort(404, description="文件不存在")
        # 检测图片格式
        with open(filepath, 'rb') as f:
            data = f.read(16)
        if data[:2] == b'\xff\xd8':  # JPEG/JFIF
            mimetype = 'image/jpeg'
        elif data[:3] == b'BM\x00':  # BMP
            mimetype = 'image/bmp'
        elif data[:8] == b'\x89PNG\r\n\x1a\n':
            mimetype = 'image/png'
        elif data[:6] in (b'GIF87a', b'GIF89a'):
            mimetype = 'image/gif'
        else:
            mimetype = 'application/octet-stream'
        # 设置缓存
        response = make_response(send_file(filepath, mimetype=mimetype))
        response.headers['Cache-Control'] = 'max-age=86400'  # 缓存有效期1天
        return response


@bp.route("/getAvatar/<userId>", methods=['GET', 'POST'])
def getavatar(userId):
    if request.method == 'GET' or request.method == 'POST':
        filepath = config.IMAGE_PATH + config.AVATAR_FOLDER + '/' + userId + '.jpg'
        if not os.path.exists(filepath):
            filepath = config.IMAGE_PATH + config.AVATAR_FOLDER + '/' + 'default_avatar.jpg'
        response = make_response(send_file(filepath, mimetype="imaga/jpg"))
        return response
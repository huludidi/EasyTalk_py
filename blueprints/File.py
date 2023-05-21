import os

from flask import Blueprint, request, abort, make_response, send_file, g

from Audit.imageAudit import image_audit
from decorators import rate_limit
from functions import SuccessResponse, generate_random_string
import config
from static.enums import globalinfoEnum, UserOperFrequencyTypeEnum

bp = Blueprint("File", __name__, url_prefix="/file")


@bp.route("/uploadImage", methods=['POST'])
@rate_limit(limit_type=UserOperFrequencyTypeEnum.IMAGE_UPLOAD)
def uploadImage():
    file = request.files.get('file')
    if not file:
        abort(400, description="文件不存在")
    # 重写文件名字
    filename = generate_random_string(15) + '.' + file.filename.rsplit('.', 1)[1].lower()
    if not allowed_file(filename):
        abort(400, description="文件格式不允许")
    file.save(config.IMAGE_PATH + config.TEMP_FOLDER + '/' + filename)
    if g.auditInfo.getPostAudit():
        if not image_audit(config.IMAGE_PATH + config.TEMP_FOLDER + '/' + filename):
            abort(400, description="图片违规，请选择合法图片")
    result = {
        'fileName': config.TEMP_FOLDER + "/" + filename
    }
    # 读取文件数据
    return SuccessResponse(data=result)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in globalinfoEnum.IMAGE_SUFFIX.value


@bp.route("/getImage/<imageFolder>/<imageName>", methods=['GET'])
def getImage(imageFolder, imageName):
    if not imageFolder or not imageName:
        filepath = config.IMAGE_PATH + '/EasyTalk.png'
    else:
        filepath = config.IMAGE_PATH + '/' + imageFolder + '/' + imageName
    if not os.path.exists(filepath):
        filepath = config.IMAGE_PATH + '/EasyTalk.png'
        # abort(400)
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


@bp.route("/getAvatar/<userId>")
def getavatar(userId):
    filepath = config.IMAGE_PATH + config.AVATAR_FOLDER + '/' + userId + '.jpg'
    if not os.path.exists(filepath):
        filepath = config.IMAGE_PATH + config.AVATAR_FOLDER + '/' + 'default_avatar.jpg'
    response = make_response(send_file(filepath, mimetype="imaga/jpg"))
    return response

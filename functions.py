import json
import os
import random
import re
import string
from datetime import datetime

from PIL import Image
from flask import jsonify, abort

import config
from exts import cache
from models import SysSetting
from static.enums import FileUploadTypeEnum
from static.globalDto import FileUpload, SysSettingDto

# 刷新缓存
def refresh_cache():
    cache.clear()
    system_settings = SysSetting.query.all()  # 从数据库中获取系统设置数据
    syssettingDto = SysSettingDto()
    for setting in system_settings:
        if setting.code == 'audit':
            syssettingDto.setAudit(json.loads(setting.json_content))
        elif setting.code == 'comment':
            syssettingDto.setComment(json.loads(setting.json_content))
        elif setting.code == 'email':
            syssettingDto.setEmail(json.loads(setting.json_content))
        elif setting.code == 'like':
            syssettingDto.setLike(json.loads(setting.json_content))
        elif setting.code == 'post':
            syssettingDto.setPost(json.loads(setting.json_content))
        elif setting.code == 'register':
            syssettingDto.setRegister(json.loads(setting.json_content))
        cache.set(setting.code, json.loads(setting.json_content))  # 将数据放入缓存
    return syssettingDto.to_dict()
# 获取板块
def convert_line_to_tree(data_list, pid):
    children = []
    for m in data_list:
        if m["p_board_id"] == pid:
            m["children"] = convert_line_to_tree(data_list, m["board_id"])
            children.append(m)
    return children

# 生成一个由 15 个随机数字组成的字符串
def generate_random_number(length):
    numbers = ''.join(random.choice(string.digits) for _ in range(15))
    return numbers

# 随机生成字符串
def generate_random_string(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

#  HTML 中的图片地址提取
def getImageList(html):
    image_list = []
    reg_ex_img = r'(<img.*src\s*=\s*(.*?)[^>]*?>)'
    p_image = re.compile(reg_ex_img, re.IGNORECASE)
    m_image = p_image.findall(html)
    for img in m_image:
        m = re.compile(r'src\s*=\s*\"?(.*?)(\"|>|\\s+)').findall(img[0])
        for image_url in m:
            image_list.append(image_url[0])
    return image_list

# 图片上传
def uploadFile2Local(file, folder, uploadtypeenum):
    try:
        fileuploaddto = FileUpload()
        originalfilename = file.filename
        filesuffix = originalfilename.rsplit('.', 1)[1]
        if len(originalfilename) > 200:
            originalfilename = originalfilename[:150] + '.' + filesuffix
        if filesuffix not in uploadtypeenum.value.get('suffix'):
            abort(400, description="文件格式不允许")

        month = datetime.now().strftime("%Y%m")
        # 重写文件名
        filename = generate_random_string(15) + '.' + filesuffix
        basepath = config.FILE_PATH
        targetfolder = basepath + folder + '/' + month
        localpath = month + '/' + filename

        if uploadtypeenum == FileUploadTypeEnum.AVATAR:
            targetfolder = basepath + config.PICTURE_FOLDER + config.AVATAR_FOLDER
            filesuffix = "jpg"
            localpath = folder + '.' + filesuffix
            filename = folder + '.' + filesuffix
            # 将图片转换为 JPG 格式
            file = Image.open(file.stream)
            file = file.convert('RGB')


        # 判断文件路径是否存在，不存在则创建
        if not os.path.exists(targetfolder):
            os.mkdir(targetfolder)
        file.save(targetfolder + '/' + filename)

        if uploadtypeenum == FileUploadTypeEnum.COMMENT_IMAGE:
            # 打开原始图片
            image = Image.open(targetfolder + '/' + filename)
            width, height = image.size
            if width > 200 or height > 200:
                size = (200, 200)
                image = image.resize(size)
            # 保存一份缩略图
            thumbnailname = filename.replace(".", "_.")  # 缩略图文件名
            image.save(targetfolder + '/' + thumbnailname)
        elif uploadtypeenum == FileUploadTypeEnum.AVATAR or uploadtypeenum == FileUploadTypeEnum.ARTICLE_COVER:
            image = Image.open(targetfolder + '/' + filename)
            size = (200, 200)
            file = image.resize(size)
            # 覆盖原始图片
            os.remove(targetfolder + '/' + filename)
            file.save(targetfolder + '/' + filename)
        fileuploaddto.setoriginalFileName(originalfilename)
        fileuploaddto.setlocalPath(localpath)
        return fileuploaddto
    except Exception as e:
        print(e)


def SuccessResponse(data=None):
    code = 200
    status = "success"
    info = None
    data = data
    return jsonify({
        'status': status,
        'code': code,
        'info': info,
        'data': data
    })

class CustomResponse:
    def __init__(self, status=None, code=None, info=None, data=None):
        self.code = code
        self.info = info
        self.status = "error"
        if code == 200:
            self.status = "successful"
            self.info = "请求成功"

        if code == 404:
            self.status = "error"
            self.info = "请求地址不存在"
        if code == 600:
            self.status = "error"
            self.info = "请求参数错误"
        if code == 601:
            self.status = "error"
            self.info = "信息已经存在，重复提交"
        if code == 602:
            self.status = "error"
            self.info = "信息提交过多，出发了提交信息阈值，比如当天发帖太多"
        if code == 500:
            self.status = "error"
            self.info = "服务器返回错误"
        if code == 901:
            self.status = "error"
            self.info = "登录超时，长时间未操作"
        if code == 900:
            self.status = "error"
            self.info = "http请求超时"
        self.data = data

    def to_dict(self):
        return jsonify({
            'status': self.status,
            'code': self.code,
            'info': self.info,
            'data': self.data
        })

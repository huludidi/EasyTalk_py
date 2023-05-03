from flask import jsonify


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

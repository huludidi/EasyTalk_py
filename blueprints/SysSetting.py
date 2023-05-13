from flask import Blueprint, request, abort
from decorators import check_params, check_admin
from exts import db
from functions import SuccessResponse, refresh_cache
from models import SysSetting
from static.globalDto import Audit, Comment, Email, Like, Post, Register

bp = Blueprint("SysSetting", __name__, url_prefix="/manageSetting")


@bp.route("/getSetting", methods=['POST'])
@check_admin
def getSetting():
    data = refresh_cache()
    return SuccessResponse(data=data)


@bp.route("/saveSetting", methods=['POST'])
@check_admin
@check_params
def saveSetting():
    registerWelcomInfo = request.values.get('registerWelcomInfo')
    emailTitle = request.values.get('emailTitle')
    emailContent = request.values.get('emailContent')
    postAudit = bool(request.values.get('postAudit'))
    commentAudit = bool(request.values.get('commentAudit'))
    dayImageUploadCount = int(request.values.get('dayImageUploadCount'))
    postDayCountThreshold = int(request.values.get('postDayCountThreshold'))
    attachmentSize = int(request.values.get('attachmentSize'))
    commentOpen = bool(request.values.get('commentOpen'))
    commentDayCountThreshold = int(request.values.get('commentDayCountThreshold'))
    likeDayCountThreshold = int(request.values.get('likeDayCountThreshold'))

    auditDto = Audit(commentAudit=commentAudit, postAudit=postAudit)
    commentDto = Comment(commentDayCountThreshold=commentDayCountThreshold, commentOpen=commentOpen)
    emailDto = Email(emailContent=emailContent, emailTitle=emailTitle)
    likeDto = Like(likeDayCountThreshold=likeDayCountThreshold)
    postDto = Post(attachmentSize=attachmentSize, dayImageUploadCount=dayImageUploadCount,
                   postDayCountThreshold=postDayCountThreshold)
    registerDto = Register(registerWelcomInfo=registerWelcomInfo)

    syssetting = SysSetting.query.all()
    for item in syssetting:
        if item.code == 'audit':
            item.json_content = auditDto.to_json()
        elif item.code == 'comment':
            item.json_content = commentDto.to_json()
        elif item.code == 'email':
            item.json_content = emailDto.to_json()
        elif item.code == 'like':
            item.json_content = likeDto.to_json()
        elif item.code == 'post':
            item.json_content = postDto.to_json()
        elif item.code == 'register':
            item.json_content = registerDto.to_json()
    try:
        db.session.commit()
        refresh_cache()  # 刷新缓存中的数据
        return SuccessResponse()
    except Exception as e:
        print(e)
        abort(422)

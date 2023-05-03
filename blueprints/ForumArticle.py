import json
from datetime import datetime

from flask import Blueprint, request, jsonify, session, abort, make_response, send_file
from functions import CustomResponse, SuccessResponse
from decorators import check_params, login_required
from exts import db
from models import ForumBoard, ForumArticle, ForumArticleAttachment, LikeRecord, UserMessage
from static.enums import globalinfoEnum, MessageTypeEnum

bp = Blueprint("ForumArticle", __name__, url_prefix="/forum")


@bp.route("/loadArticle", methods=['POST'])
def loadArticle():
    boardId = request.values.get('boardId')
    pBoardId = request.values.get('pBoardId')
    orderType = request.values.get('orderType')  # 0:点赞最多 1:评论最多
    filterType = request.values.get('filterType')  # 0:与我同校 1:与我同城
    pageNo = request.values.get('pageNo')
    userinfo = session.get('userInfo')
    forumarticle = ForumArticle()
    data = forumarticle.searchlist(userinfo=userinfo, p_board_id=pBoardId, board_id=boardId, orderType=orderType,
                                   filterType=filterType, pageNo=pageNo)
    return SuccessResponse(data=data)


@bp.route("/getArticleDetail", methods=['POST'])
@check_params
def getArticleDetail():
    try:
        articleid = request.values.get('articleId')
        article = ForumArticle.query.filter_by(article_id=articleid).first()
        # 判断是否可以访问
        if not article or (article.status != 1 and (
                session.get('userInfo') is None or json.loads(session['userInfo']).get(
            'userId') != article.author_id or not
                session['isAdmin'])):
            abort(404)
        # 打包返回结果
        article.read_count += 1
        result = {}
        result['forumArticle'] = article.to_dict()
        # 有附件
        if article.attachment_type:
            attachment = ForumArticleAttachment.query.filter_by(article_id=article.article_id).first()
            result['attachment'] = attachment.to_dict()
        # 是否已点赞
        if session.get('userInfo'):
            likerecord = LikeRecord.query.filter_by(
                object_id=article.article_id, user_id=session['userInfo'].get('userId'),
                op_type=globalinfoEnum.ARTICLE_LIKE.value).first()
            if likerecord:
                result['haveLike'] = True
        db.session.commit()
        return SuccessResponse(data=result)
    except:
        db.session.rollback()
        abort(422)


@bp.route("/doLike", methods=['POST'])
@login_required
@check_params
def doLike():
    articleid = request.values.get('articleId')
    optype = request.values.get('opType')
    userid = session['userInfo'].get('userId')
    likerecord = LikeRecord()
    likerecord.dolike(objectid=articleid,optype=optype,userid=userid)
    return SuccessResponse()


def articleLike(objid, article, userid, optype):
    likecord = LikeRecord.query.filter_by(object_id=objid, user_id=userid, op_type=optype).first()
    try:
        if not likecord:
            new_likecord = LikeRecord(op_type=optype, object_id=objid, user_id=userid, create_time=datetime.now(),
                                      author_user_id=article.author_id)
            article.good_count += 1
            db.session.add(new_likecord)
            db.session.commit()
            return None
        else:
            db.session.delete(likecord)
            article.good_count -= 1
            db.session.commit()
            return likecord
    except Exception as e:
        print(e)
        abort(422)


@bp.route("/attachmentDownload", methods=['POST'])
@login_required
@check_params
def attachmentDownload():
    fileid = request.values.get('fileId')
    # fileid = request.args.get('fileId')
    file = ForumArticleAttachment.query.filter_by(file_id=fileid).first()
    if file is None:
        abort(404, description="文件不存在")
    else:
        try:
            file.download_count += 1
            # 记录消息
            article = ForumArticle.query.filter_by(article_id=file.article_id).first()
            usermessage = UserMessage(received_user_id=file.user_id, article_id=article.article_id,
                                      article_title=article.title, send_user_id=session['userInfo'].get(
                    'userId'), send_nick_name=session['userInfo'].get(
                    'nickName'), message_type=MessageTypeEnum.ATTACHMENT_DOWNLOAD.value.get(
                    'type'), create_time=datetime.now())
            db.session.add(usermessage)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            abort(422)
        filename = file.file_name
        filename = filename.encode("utf-8").decode("latin1")  # 编码转换
        response = make_response(send_file(file.file_path))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
        return response

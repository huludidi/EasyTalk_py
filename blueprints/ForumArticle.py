import json
from datetime import datetime

from flask import Blueprint, request, jsonify, session, abort, make_response, send_file
from CustomResponse import CustomResponse, SuccessResponse
from decorators import check_params, login_required
from exts import db
from models import ForumBoard, ForumArticle, ForumArticleAttachment, LikeRecord, UserMessage
from static.enums import globalinfoEnum, MessageTypeEnum

bp = Blueprint("ForumArticle", __name__, url_prefix="/forum")


@bp.route("/loadArticle", methods=['POST'])
def loadArticle():
    boardId = request.form.get('boardId')
    pBoardId = request.form.get('pBoardId')
    orderType = request.form.get('orderType')  # 0:点赞最多 1:评论最多
    filterType = request.form.get('filterType')  # 0:与我同校 1:与我同城
    pageNo = request.form.get('pageNo')
    userinfo = session.get('userInfo')
    forumarticle = ForumArticle()
    data = forumarticle.searchlist(userinfo=userinfo, p_board_id=pBoardId, board_id=boardId, orderType=orderType,
                                   filterType=filterType, pageNo=pageNo)
    return SuccessResponse(data=data)


@bp.route("/getArticleDetail", methods=['POST'])
@check_params
def getArticleDetail():
    try:
        articleid = request.form.get('articleId')
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
        return CustomResponse(code=200, data=result).to_dict()
    except:
        db.session.rollback()
        abort(422)


@bp.route("/doLike", methods=['POST'])
@login_required
@check_params
def doLike():
    articleid = request.form.get('articleId')
    optype = request.form.get('opType')
    userid = session['userInfo'].get('userId')
    # LikeRecord.dolike(articleid,optype,userid)
    try:
        usermessage = UserMessage()
        # 文章点赞
        if int(optype) == globalinfoEnum.ARTICLE_LIKE.value:
            article = ForumArticle.query.filter_by(article_id=articleid).first()
            if not article:
                abort(500, description="文章不存在")
            likecord = articleLike(articleid, article, userid, optype)
            usermessage.article_id = articleid
            usermessage.comment_id = 0
            usermessage.article_title = article.title
            usermessage.message_type = MessageTypeEnum.ARTICLE_LIKE.value.get('type')
            usermessage.received_user_id = article.author_id
        #     评论点赞
        else:
            return
        usermessage.create_time = datetime.now()
        usermessage.send_user_id = userid
        usermessage.send_nick_name = session['userInfo'].get('nickName')
        usermessage.status = 1
        if not likecord and userid != usermessage.received_user_id:
            messageinfo = UserMessage.query.filter_by(article_id=usermessage.article_id,
                                                      comment_id=usermessage.comment_id,
                                                      send_user_id=usermessage.send_user_id,
                                                      message_type=usermessage.message_type).first()
            if not messageinfo:
                db.session.add(usermessage)
                db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(422)
    finally:
        return CustomResponse(code=200).to_dict()


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


@bp.route("/attachmentDownload", methods=[ 'POST'])
@login_required
@check_params
def attachmentDownload():
    fileid = request.form.get('fileId')
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

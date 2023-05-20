from datetime import datetime
from math import ceil
from flask import Blueprint, request, abort, make_response, send_file, session
from sqlalchemy import desc, func

import config
from decorators import check_params, check_admin
from exts import db
from functions import SuccessResponse
from models import ForumBoard, ForumArticle, UserMessage, ForumArticleAttachment, LikeRecord, ForumComment
from static.enums import globalinfoEnum, MessageTypeEnum

bp = Blueprint("ManageArticle", __name__, url_prefix="/manageForum")


# 板块校验
def resetBoardInfo(isAdmin, article):
    pboard = ForumBoard.query.filter_by(board_id=article.p_board_id).first()
    if not pboard or (pboard.post_type == 0 and not isAdmin):
        abort(400, description="一级板块不存在")
    article.p_board_name = pboard.board_name
    if article.board_id and article.board_id != 0:
        board = ForumBoard.query.filter_by(board_id=article.board_id).first()
        if not board or (board.post_type == 0 and not isAdmin):
            abort(400, description="二级板块不存在")
        article.board_name = board.board_name
    else:
        article.board_id = 0
        article.board_name = None


@bp.route("/loadArticle", methods=['GET', 'POST'])
@check_admin
def loadArticle():
    pageNo = request.values.get('pageNo')
    pageSize = request.values.get(('pageSize'))
    titleFuzzy = request.values.get('titleFuzzy')
    nickNameFuzzy = request.values.get('nickNameFuzzy')
    attachmentType = request.values.get('attachmentType')
    status = request.values.get('status')
    audit = request.values.get('audit')
    boardIds = request.values.get('boardIds')
    if pageNo:
        pageNo = int(pageNo)
    else:
        pageNo = None
    if not pageSize:
        pageSize = globalinfoEnum.PageSize.value
    else:
        pageSize = int(pageSize)
    articles = ForumArticle.query.order_by(ForumArticle.post_time.desc())
    if titleFuzzy:
        articles = articles.filter(ForumArticle.title.like(f'%{titleFuzzy}%'))
    if nickNameFuzzy:
        articles = articles.filter(ForumArticle.nick_name.like(f'%{nickNameFuzzy}%'))
    if attachmentType:
        articles = articles.filter(ForumArticle.attachment_type == int(attachmentType))
    if status:
        articles = articles.filter(ForumArticle.status == int(status))
    if audit != "":
        articles = articles.filter(ForumArticle.audit == int(audit))
    if boardIds:
        id_list = boardIds.split(",")
        if len(id_list) > 1:
            articles = articles.filter(ForumArticle.board_id == id_list[1])
        articles = articles.filter(ForumArticle.p_board_id == id_list[0])

    total = articles.count()
    articles = articles.paginate(page=pageNo, per_page=pageSize, error_out=False).items
    list = []
    for item in articles:
        item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
        item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
        list.append(item.to_dict())
    result = {
        'totalCount': total,
        'pageSize': pageSize,
        'pageNo': pageNo,
        'pageTotal': ceil(total / pageSize),
        'list': list
    }
    return SuccessResponse(data=result)


@bp.route("/delArticle", methods=['POST'])
@check_admin
@check_params
def delArticle():
    articleids = request.values.get('articleIds')
    id_list = articleids.split(",")
    for item in id_list:
        singledel(item)
    db.session.commit()
    return SuccessResponse()


def singledel(articleid):
    article = ForumArticle.query.filter_by(article_id=articleid).first()
    if not article or article.status == -1:
        return
    article.status = -1
    message = UserMessage(received_user_id=article.author_id,
                          message_type=MessageTypeEnum.SYS.value.get('type'),
                          create_time=datetime.now(),
                          status=globalinfoEnum.NO_READ.value,
                          message_content=f"您的{article.title}文章已被管理员删除")
    db.session.add(message)


@bp.route("/updateBoard", methods=['POST'])
@check_admin
@check_params
def updateBoard():
    articleid = request.values.get('articleId')
    pboardid = request.values.get('pBoardId')
    boardid = request.values.get('boardId')
    article = ForumArticle.query.filter_by(article_id=articleid).first()

    article.p_board_id = pboardid
    article.board_id = boardid
    resetBoardInfo(isAdmin=True, article=article)
    db.session.commit()
    return SuccessResponse()


@bp.route("/getAttachment", methods=['POST'])
@check_admin
@check_params
def getAttachment():
    articleid = request.values.get('articleId')
    attachment = ForumArticleAttachment.query.filter_by(article_id=articleid).first()
    if not attachment:
        abort(400, description="附件不存在")
    return SuccessResponse(data=attachment.to_dict())


@bp.route("/attachmentDownload")
@check_admin
def attachmentDownload():
    fileid = request.values.get('fileId')
    file = ForumArticleAttachment.query.filter_by(file_id=fileid).first()
    if file is None:
        abort(404, description="文件不存在")
    else:
        file.download_count += 1
        # 记录消息
        article = ForumArticle.query.filter_by(article_id=file.article_id).first()
        usermessage = UserMessage(received_user_id=file.user_id, article_id=article.article_id,
                                  article_title=article.title, send_user_id=session['userInfo'].get(
                'userId'), send_nick_name=session['userInfo'].get(
                'nickName'), message_type=MessageTypeEnum.ATTACHMENT_DOWNLOAD.value.get(
                'type'), message_content=f"管理员下载了{article.title}中的附件", create_time=datetime.now())
        db.session.add(usermessage)
        db.session.commit()
        filename = file.file_name
        filename = filename.encode("utf-8").decode("latin1")  # 编码转换
        response = make_response(send_file(config.FILE_PATH + config.ATTACHMENT_FOLDER + "/" + file.file_path))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
        return response


@bp.route("/auditArticle", methods=['POST'])
@check_admin
@check_params
def auditArticle():
    articleids = request.values.get('articleIds')
    id_list = articleids.split(",")
    for item in id_list:
        singleaudit(item)
    return SuccessResponse()


def singleaudit(articleid):
    article = ForumArticle.query.filter_by(article_id=articleid).first()
    if not article or article.status != 1:
        return
    article.status = 1
    article.audit = 1
    db.session.commit()


@bp.route("/loadComment", methods=['POST'])
@check_admin
def loadComment():
    articleid = request.values.get('articleId')
    pageno = request.values.get('pageNo')
    pageSize=request.values.get('pageSize')
    contentFuzzy = request.values.get('contentFuzzy')
    nickNameFuzzy = request.values.get('nickNameFuzzy')
    status = request.values.get('status')
    audit=request.values.get('audit')
    if not pageno:
        pageno = 1
    else:
        pageno=int(pageno)
    if not pageSize:
        pageSize=globalinfoEnum.PageSize.value
    else:
        pageSize=int(pageSize)
    userinfo = session['userInfo']
    comments = ForumComment.query.order_by(ForumComment.post_time.desc())
    if articleid:
        comments = comments.filter(ForumComment.article_id == articleid)
    if contentFuzzy:
        comments = comments.filter(ForumComment.content.like(f'%{contentFuzzy}%'))
    if nickNameFuzzy:
        comments = comments.filter(ForumComment.nick_name.like(f'%{nickNameFuzzy}%'))
    if status:
        comments = comments.filter(ForumComment.status == status)
    if audit:
        comments = comments.filter(ForumComment.audit == audit)
    totalcount = comments.count()
    comments = comments.paginate(page=pageno, per_page=pageSize, error_out=False)
    list = []
    for item in comments:
        item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
        list.append(item.to_dict())
    result = {
        'totalCount': totalcount,
        'pageSize': pageSize,
        'pageNo': pageno,
        'pageTotal': ceil(totalcount / pageSize),
        'list': list
    }
    return SuccessResponse(data=result)


@bp.route("/loadComment4Article", methods=['POST'])
@check_admin
def loadComment4Article():
    articleid = request.values.get('articleId')
    if not articleid:
        abort(400)
    ordertype = '0'
    per_page = 20  # 每页展示的评论数量
    userinfo = session['userInfo']
    # 查询数据总数
    total_count = db.session.query(func.count(ForumComment.comment_id)).filter_by(
        p_comment_id=0, article_id=articleid, audit=1).scalar()
    # 查找所有一级评论
    comments = ForumComment.query \
        .filter_by(p_comment_id=0, article_id=articleid)
    if ordertype == "0":
        comments = comments.order_by(desc(ForumComment.post_time))
    pcomment_list = []
    for item in comments:
        like = LikeRecord.query \
            .filter_by(object_id=item.comment_id, user_id=userinfo.get('userId'), op_type=1) \
            .first()
        if like:
            haveliked = 1
        else:
            haveliked = 0
        item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
        dictitem = item.to_dict()
        dictitem['haveliked'] = haveliked
        pcomment_list.append(dictitem)
    result = {
        'totalCount': total_count,
        'pageSize': per_page,
        'pageNo': 1,
        'pageTotal': ceil(total_count / per_page),
        'list': pcomment_list
    }
    return SuccessResponse(data=result)


@bp.route("/delComment", methods=['POST'])
@check_admin
def delComment():
    commentids = request.values.get('commentIds')
    id_list = commentids.split(",")
    try:
        for item in id_list:
            singledelcomment(item)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(422)
    return SuccessResponse()


def singledelcomment(commentid):
    comment = ForumComment.query.filter_by(comment_id=commentid).first()
    if not comment or comment.status != 1:
        return
    if comment.audit == globalinfoEnum.HAVE_AUDITED.value:
        article = ForumArticle.query.filter_by(article_id=comment.article_id).first()
        article.comment_count -= 1
    comment.status = -1
    message = UserMessage(received_user_id=comment.user_id,
                          message_type=MessageTypeEnum.SYS.value.get('type'),
                          create_time=datetime.now(),
                          status=globalinfoEnum.NO_READ.value,
                          message_content=f"评论‘{comment.content}’已经被管理员删除"
                          )
    db.session.add(message)


@bp.route("/auditComment", methods=['POST'])
@check_admin
def auditComment():
    commentids = request.values.get('commentIds')
    id_list = commentids.split(",")
    try:
        for item in id_list:
            singleauditcomment(item)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(422)
    return SuccessResponse()


def singleauditcomment(commentid):
    comment = ForumComment.query.filter_by(comment_id=commentid).first()
    if not comment or comment.status == -1:
        return
    comment.status = 1
    comment.audit = 1

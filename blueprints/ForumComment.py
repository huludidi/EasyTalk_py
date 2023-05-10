from datetime import datetime
from math import ceil
from pydoc import html

from flask import Blueprint, request, session, abort, g
from sqlalchemy import desc, func, asc

import config
from Audit.imageAudit import image_audit
from Audit.textAudit import textAudit
from functions import CustomResponse, SuccessResponse, uploadFile2Local
from decorators import check_params, login_required, rate_limit
from exts import db
from models import LikeRecord, UserMessage, ForumComment, ForumArticle, UserInfo
from static.enums import globalinfoEnum, MessageTypeEnum, FileUploadTypeEnum, UserOperFrequencyTypeEnum

bp = Blueprint("ForumComment", __name__, url_prefix="/comment")


@bp.route("/loadComment", methods=['POST'])
@check_params
def loadArticle():
    articleid = request.values.get('articleId')
    pageno = request.values.get('pageNo')
    ordertype = request.values.get('orderType')  # 0:最新 1:最热
    userinfo = session['userInfo']
    if not g.commentInfo.getcommentOpen():
        abort(500, description="未开启评论")

    # 查询数据总数
    total_count = db.session.query(func.count(ForumComment.comment_id)).filter_by(
        p_comment_id=0, article_id=articleid).scalar()
    # 查找所有一级评论
    per_page = 20  # 每页展示的评论数量
    comments = ForumComment.query \
        .filter_by(p_comment_id=0, article_id=articleid)
    if ordertype == "0":
        comments = comments.order_by(desc(ForumComment.post_time))
    else:
        comments = comments.order_by(desc(ForumComment.good_count))
    comments = comments.paginate(page=int(pageno), per_page=per_page, error_out=False).items
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
    # 查询二级评论并塞入一级评论中
    list = get_comments(pcomment_list, userinfo, articleid)
    result = {
        'totalCount': total_count,
        'pageSize': per_page,
        'pageNo': pageno,
        'pageTotal': ceil(total_count / per_page),
        'list': list
    }
    return CustomResponse(code=200, data=result).to_dict()


def get_comments(pcomment_list, userinfo, articleid):
    comments = ForumComment.query.filter(ForumComment.p_comment_id != 0, ForumComment.article_id == articleid).all()
    childrenlist = {}
    result = []
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
        childrenlist.setdefault(dictitem.get('p_comment_id'), []).append(dictitem)
    for item in pcomment_list:
        if childrenlist.get(item['comment_id']):
            item['chiledren'] = childrenlist.get(item['comment_id'])
        else:
            item['children'] = None
        result.append(item)
    return result


@bp.route("/doLike", methods=['POST'])
@check_params
@rate_limit(limit_type=UserOperFrequencyTypeEnum.DO_LIKE)
def dolike():
    commentid = request.values.get('commentId')

    userinfo = session['userInfo']
    likerecord = LikeRecord()
    likerecord.dolike(objectid=commentid, optype=globalinfoEnum.COMMENT_LIKE.value, userid=userinfo.get('userId'))
    comment = ForumComment.query.filter_by(comment_id=commentid).first().to_dict()
    like = LikeRecord.query.filter_by(object_id=commentid, user_id=userinfo.get('userId'),
                                      op_type=globalinfoEnum.COMMENT_LIKE.value).first()
    if like:
        comment['haveliked'] = 1
    else:
        comment['haveliked'] = 0
    comment['post_time'] = comment['post_time'].strftime('%Y-%m-%d %H:%M:%S')
    return SuccessResponse(data=comment)


@bp.route("/postComment", methods=['POST'])
@login_required
@rate_limit(limit_type=UserOperFrequencyTypeEnum.POST_COMMENT)
def postcomment():
    articleid = request.values.get('articleId')
    pcommentid = request.values.get('pCommentId')
    content = request.values.get('content')
    image = request.files.get('image')
    replyuserid = request.values.get('replyUserId')
    userinfo = session['userInfo']
    # 必须有articleid pcommentid
    if not articleid or not pcommentid:
        abort(400)
    if content and (len(content) < 5 or len(content) > 500):
        abort(400)
    if not g.commentInfo.getcommentOpen():
        abort(400)
    if not image and not content:
        abort(400)
    # 对前端传入的文本进行转义处理
    escaped_content = html.escape(content)
    comment = ForumComment(p_comment_id=int(pcommentid),
                           article_id=articleid,
                           content=escaped_content,
                           user_id=userinfo['userId'],
                           nick_name=userinfo['nickName'],
                           user_ip_address=userinfo['lastLoginIpAddress'],
                           reply_user_id=replyuserid,
                           post_time=datetime.now(),
                           )
    # 评论发布
    post(comment, image)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    # 返回参数
    if pcommentid != '0':
        comments = ForumComment.query \
            .filter_by(p_comment_id=pcommentid, article_id=articleid, status=1, audit=1) \
            .order_by(asc(ForumComment.comment_id)).all()
        children = []
        for item in comments:
            item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
            children.append(item.to_dict())
        return SuccessResponse(data=children)
    comment.post_time = comment.post_time.strftime('%Y-%m-%d %H:%M:%S')
    return SuccessResponse(data=comment.to_dict())


def post(comment, image):
    article = ForumArticle.query.filter_by(article_id=comment.article_id).first()
    # 判断参数是否正确
    pcomment = None
    if not article or article.status == globalinfoEnum.NOT_AUDIT.value:
        abort(400, description="评论的文章不存在")
    if comment.p_comment_id != 0:
        pcomment = ForumComment.query.filter_by(comment_id=comment.p_comment_id).first()
        if not pcomment:
            abort(400, description="回复的评论不存在")
    if comment.reply_user_id:
        user = UserInfo.query.filter_by(user_id=comment.reply_user_id)
        if not user:
            abort(400, description="回复的用户不存在")
        comment.nick_name = user.nick_name
    if image:
        uploaddto = uploadFile2Local(image, config.PICTURE_FOLDER, FileUploadTypeEnum.COMMENT_IMAGE)
        comment.img_path = uploaddto.getlocalPath()
    db.session.add(comment)
    if g.auditInfo.getPostAudit():
        comment.status = 1
        contentaudit = 0
        imageaudit = 0
        if comment.content:
            contentaudit = textAudit(comment.content)
        if comment.img_path:
            imageaudit = image_audit(config.IMAGE_PATH + '/' + comment.img_path)
        if contentaudit and imageaudit:
            comment.audit = globalinfoEnum.PASS.value
        else:
            comment.audit = globalinfoEnum.NO_PASS.value
            message = UserMessage(received_user_id=comment.user_id,
                                  message_type=MessageTypeEnum.SYS.value.get('type'),
                                  message_content="您的评论含不正当言论！！请注意言辞",
                                  create_time=datetime.now())
            db.session.add(message)
            return
    updateCommentInfo(comment, article, pcomment)


def updateCommentInfo(comment, article, pcomment):
    if comment.p_comment_id == 0:
        article.comment_count += 1
    # 记录消息
    usermessage = UserMessage(message_type=MessageTypeEnum.COMMENT.value.get('type'),
                              create_time=datetime.now(),
                              article_id=comment.article_id,
                              comment_id=comment.comment_id,
                              send_user_id=comment.user_id,
                              send_nick_name=comment.nick_name,
                              status=1,
                              article_title=article.title)
    if comment.p_comment_id == 0:
        usermessage.received_user_id = article.author_id
    elif comment.p_comment_id != 0 and not comment.reply_user_id:
        usermessage.received_user_id = pcomment.user_id
    elif comment.p_comment_id != 0 and comment.reply_user_id:
        usermessage.received_user_id = comment.reply_user_id
    if comment.user_id != usermessage.received_user_id:
        db.session.add(usermessage)

from datetime import datetime
from math import ceil
from pydoc import html

from flask import Blueprint, request, session, abort, make_response, send_file, g
from sqlalchemy import desc, func, asc

from functions import CustomResponse, SuccessResponse
from decorators import check_params, login_required
from exts import db
from models import LikeRecord, UserMessage, ForumComment
from static.enums import globalinfoEnum, MessageTypeEnum

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
    try:
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
    except Exception as e:
        print(e)
        abort(422)


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
    return SuccessResponse(data=comment)


@bp.route("/postComment", methods=['POST'])
@login_required
def postcomment():
    articleid = request.values.get('articleId')
    pcommentid = request.values.get('pCommentId')
    content = request.values.get('content')
    image = request.files.get('image')
    replyuserid = request.values.get('replyUserId')
    userinfo = session['userInfo']
    if not articleid or not pcommentid or (len(content) < 5 or len(content) > 500):
        abort(400)
    if not g.commentInfo.getcommentOpen():
        abort(400)
    if not image and not content:
        abort(400)
    # 对前端传入的文本进行转义处理
    escaped_content = html.escape(content)
    forumcomment = ForumComment(p_comment_id=pcommentid,
                                article_id=articleid,
                                content=escaped_content,
                                user_id=userinfo['userId'],
                                nick_name=userinfo['nickName'],
                                user_ip_address=userinfo['ipAddress'],
                                reply_user_id=replyuserid,
                                post_time=datetime.now(),
                                )

    if pcommentid != 0:
        comments = ForumComment.query\
            .filter_by(p_comment_id=pcommentid, article_id=articleid)\
            .order_by(asc(ForumComment.comment_id))
        children=[]
        for item in comments:
            children.append(item.to_dict())
        return SuccessResponse(data=children)
    return SuccessResponse(data=forumcomment)
def post(comment , image):
    return 1


import json
from datetime import datetime
from math import ceil

from flask import Blueprint, request, jsonify, session, abort, make_response, send_file, g
from sqlalchemy import desc, func

from CustomResponse import CustomResponse, SuccessResponse
from decorators import check_params, login_required
from exts import db
from models import ForumBoard, ForumArticle, ForumArticleAttachment, LikeRecord, UserMessage, ForumComment
from static.enums import globalinfoEnum, MessageTypeEnum

bp = Blueprint("ForumComment", __name__, url_prefix="/comment")


@bp.route("/loadComment", methods=['POST'])
@check_params
def loadArticle():
    articleid = request.form.get('articleId')
    pageno = request.form.get('pageNo')
    ordertype = request.form.get('orderType')#0:最新 1:最热
    userinfo = session['userInfo']
    if not g.commentInfo.getcommentOpen():
        abort(500, description="未开启评论")
    try:
        # 查询数据总数
        total_count = db.session.query(func.count(ForumComment.comment_id)).filter(
            ForumComment.p_comment_id == 0).scalar()
        # 查找所有一级评论
        per_page = 20  # 每页展示的评论数量
        comments = ForumComment.query \
            .filter_by(p_comment_id=0)
        if ordertype == "0":
            comments=comments.order_by(desc(ForumComment.post_time))
        else:
            comments=comments.order_by(desc(ForumComment.good_count))
        comments=comments.paginate(page=int(pageno), per_page=per_page, error_out=False).items
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
        list = get_comments(pcomment_list, userinfo)
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


def get_comments(pcomment_list, userinfo):
    comments = ForumComment.query.filter(ForumComment.p_comment_id != 0).all()
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

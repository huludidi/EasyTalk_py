from datetime import datetime
from math import ceil

from flask import Blueprint, request

from decorators import check_params
from exts import db
from functions import SuccessResponse
from models import ForumBoard, ForumArticle, UserMessage
from static.enums import globalinfoEnum, MessageTypeEnum

bp = Blueprint("ManageArticle", __name__, url_prefix="/manageForum")


@bp.route("/loadArticle", methods=['POST'])
def loadArticle():
    articles = ForumArticle.query.order_by(ForumArticle.post_time.desc())
    total = articles.count()
    articles = articles.paginate(page=None, per_page=globalinfoEnum.PageSize.value)
    list = []
    for item in articles:
        item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
        item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
        list.append(item.to_dict())
    result = {
        'totalCount': total,
        'pageSize': globalinfoEnum.PageSize.value,
        'pageNo': articles.page,
        'pageTotal': ceil(total / globalinfoEnum.PageSize.value),
        'list': list
    }
    return SuccessResponse(data=result)


@bp.route("/delArticle", methods=['POST'])
@check_params
def delArticle():
    articleids = request.values.get('articleIds')
    id_list = articleids.split(",")
    for item in id_list:
        singledel(item)
    return SuccessResponse()


def singledel(articleid):
    article = ForumArticle.query.filter_by(article_id=articleid).first()
    if not article or article.status == -1:
        return
    article.status = -1
    message = UserMessage(received_user_id=article.author_id,
                          message_type=MessageTypeEnum.SYS.value.get('type'),
                          create_time=datetime.now(),
                          status=globalinfoEnum.NO_READ,
                          message_content=f"您的{article.title}文章已被管理员删除")
    db.session.add(message)
    db.session.commit()

from flask import Blueprint, request, jsonify, session
from CustomResponse import CustomResponse, SuccessResponse
from decorators import check_params
from models import ForumBoard

bp = Blueprint("ForumArticle", __name__, url_prefix="/forum")


@bp.route("/loadArticle", methods=['POST'])
def loadArticle():
    boardId = request.form.get('boardId')
    pBoardId = request.form.get('pBoardId')
    orderType = request.form.get('orderType') #0:最新 1:评论最多
    filterType = request.form.get('filterType') # 0:与我同校 1:与我同城
    pageNo = request.form.get('pageNo')



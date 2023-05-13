from flask import Blueprint, request, abort

import config
from decorators import check_params, check_admin
from exts import db
from functions import SuccessResponse, convert_line_to_tree, uploadFile2Local
from models import ForumBoard, ForumArticle
from static.enums import  FileUploadTypeEnum

bp = Blueprint("ManageBoard", __name__, url_prefix="/manageBoard")


@bp.route("/loadBoard", methods=['POST'])
@check_admin
def loadBoard():
    formboardinfo = ForumBoard.query.order_by(ForumBoard.sort.asc()).all()
    formboardinfoList = []
    for item in formboardinfo:
        formboardinfoList.append(item.to_dict())

    return SuccessResponse(data=convert_line_to_tree(formboardinfoList, 0))


@bp.route("/saveBoard", methods=['POST'])
@check_admin
def saveBoard():
    boardId = request.values.get('boardId')
    pBoardId = request.values.get('pBoardId')
    boardName = request.values.get('boardName')
    boardDesc = request.values.get('boardDesc')
    cover = request.files.get('cover')
    if not pBoardId or not boardName or not boardDesc:
        abort(400)

    if boardId:  # 修改
        board = ForumBoard.query.filter_by(board_id=boardId).first()
        if not board:
            abort(400, description="板块信息不存在")
        board.p_board_id = pBoardId
        board.board_desc = boardDesc
        if board.board_name != boardName:
            board.board_name = boardName
            result = 0 if board.p_board_id == 0 else 1
            updateBoardNameBatch(boardname=boardName, boardtype=result, boardid=boardId)
    else:  # 新增
        if pBoardId == '0' and not cover:
            abort(400, description="请传入板块图片")
        board = ForumBoard(p_board_id=pBoardId, board_name=boardName, board_desc=boardDesc)
        count = ForumBoard.query.filter_by(p_board_id=board.p_board_id).count()
        board.sort = count + 1
        db.session.add(board)
    if cover:
        uploadDto = uploadFile2Local(cover, config.PICTURE_FOLDER + config.BOARD_FOLDER,
                                     FileUploadTypeEnum.ARTICLE_COVER)
        board.cover = uploadDto.getlocalPath()
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        abort(422)
    return SuccessResponse()


def updateBoardNameBatch(boardname, boardtype, boardid):
    #     boardtype :0-pboardname 1-boardname
    if boardtype == 0:
        update_stmt = (
            ForumArticle.__table__
            .update()
            .where(ForumArticle.p_board_id == boardid)
            .values(p_board_name=boardname)
        )
    else:
        update_stmt = (
            ForumArticle.__table__
            .update()
            .where(ForumArticle.board_id == boardid)
            .values(board_name=boardname)
        )
    db.session.execute(update_stmt)


@bp.route("/delBoard", methods=['POST'])
@check_admin
@check_params
def delBoard():
    boardId = request.values.get('boardId')
    article = ForumArticle.query.filter_by(board_id=boardId).first()
    if article:
        abort(400, description="此板块已有发布的内容，请勿删除")
    board = ForumBoard.query.filter_by(board_id=boardId).first()
    if board:
        db.session.delete(board)
        db.session.commit()
    return SuccessResponse()


@bp.route("/changeBoardSort", methods=['POST'])
@check_admin
@check_params
def changeSort():
    boardId = request.values.get('boardId')
    # 传入排好序的id数组
    boardId_dict = boardId.split(",")
    for index, value in enumerate(boardId_dict):
        board = ForumBoard.query.filter_by(board_id=value).first()
        board.sort = index + 1
    db.session.commit()
    return SuccessResponse()

from flask import Blueprint
from functions import SuccessResponse, convert_line_to_tree
from models import ForumBoard


bp = Blueprint("ForumBoard", __name__, url_prefix="/board")

# def convert_line_to_tree(data_list, pid):
#     children = []
#     for m in data_list:
#         if m["p_board_id"] == pid:
#             m["children"] = convert_line_to_tree(data_list, m["board_id"])
#             children.append(m)
#     return children


@bp.route("/loadBoard", methods=['POST'])
def loadBoard():
    formboardinfo = ForumBoard.query.order_by('sort').all()
    formboardinfoList = []
    for item in formboardinfo:
        formboardinfoList.append(item.to_dict())

    return SuccessResponse(data=convert_line_to_tree(formboardinfoList, 0))

from enum import Enum


class MessageTypeEnum(Enum):
    SYS = {"type": 0, "code": "sys", "desc": "系统消息"}
    COMMENT = {"type": 1, "code": "reply", "desc": "回复我的"}
    ARTICLE_LIKE = {"type": 2, "code": "likePost", "desc": "攒了我的文章"}
    COMMENT_LIKE = {"type": 3, "code": "likeComment", "desc": "赞了我的评论"}

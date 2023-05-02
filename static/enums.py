from enum import Enum


class globalinfoEnum(Enum):
    PageSize = 15,
    ARTICLE_LIKE = 2,
    COMMENT_LIKE = 3,
    NO_READ =1,
    HAVE_READ=2

class MessageTypeEnum(Enum):
    SYS = {"type": 0, "code": "sys", "desc": "系统消息"}
    COMMENT = {"type": 1, "code": "reply", "desc": "回复我的"}
    ARTICLE_LIKE = {"type": 2, "code": "likePost", "desc": "攒了我的文章"}
    COMMENT_LIKE = {"type": 3, "code": "likeComment", "desc": "赞了我的评论"}
    ATTACHMENT_DOWNLOAD = {"type": 4, "code": "attachmentdownload", "desc": "下载了附件"}


class ArticleOrderTypeEnum(Enum):
    NEW = {"type": 0, "orderSql": "desc('post_time')"}
    COMMENT = {"type": 1, "orderSql": "desc('comment_count')"}

    @classmethod
    def getByType(cls, Type):
        for item in cls:
            if item.value.get("type") == Type:
                return item
        return None

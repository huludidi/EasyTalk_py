from enum import Enum


class globalinfoEnum(Enum):
    # 审核是否通过
    NO_PASS = 0
    PASS = 1
    # 是否需要审核
    NOT_AUDIT = 0
    HAVE_AUDITED = 1
    # 分页大小
    PageSize = 15
    # 点赞类型
    ARTICLE_LIKE = 0
    COMMENT_LIKE = 1
    # 消息未读/已读
    NO_READ = 1
    HAVE_READ = 2
    # 文件类型
    VIDEO_SUFFIX = {'mp4'}
    IMAGE_SUFFIX = {'png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG', 'gif', 'GIF', 'bmp', 'BMP', }
    ATTACHMENT_SUFFIX = {'zip', 'ZIP', 'rar', 'RAR'}
    # 编辑器类型
    RICH = 0
    MARKDOWN = 1


class AttachmentTypeEnum(Enum):
    ZIP = {"type": 0, "suffix": globalinfoEnum.ATTACHMENT_SUFFIX.value}


class MessageTypeEnum(Enum):
    SYS = {"type": 0, "code": "sys", "desc": "系统消息"}
    COMMENT = {"type": 1, "code": "reply", "desc": "回复我的"}
    ARTICLE_LIKE = {"type": 2, "code": "likePost", "desc": "攒了我的文章"}
    COMMENT_LIKE = {"type": 3, "code": "likeComment", "desc": "赞了我的评论"}
    ATTACHMENT_DOWNLOAD = {"type": 4, "code": "attachmentDownload", "desc": "下载了附件"}

    @classmethod
    def getByType(cls, Type):
        for item in cls:
            if item.value.get("type") == Type:
                return item

    @classmethod
    def getByCode(cls, Code):
        for item in cls:
            if item.value.get("code") == Code:
                return item


class FileUploadTypeEnum(Enum):
    Board_COVER = {"desc": "板块封面", "suffix": globalinfoEnum.IMAGE_SUFFIX.value}
    ARTICLE_COVER = {"desc": "文章封面", "suffix": globalinfoEnum.IMAGE_SUFFIX.value}
    ARTICLE_ATTACHMENT = {"desc": "文章附件", "suffix": globalinfoEnum.ATTACHMENT_SUFFIX.value}
    COMMENT_IMAGE = {"desc": "评论图片", "suffix": globalinfoEnum.IMAGE_SUFFIX.value}
    AVATAR = {"desc": "个人头像", "suffix": globalinfoEnum.IMAGE_SUFFIX.value}


class UserOperFrequencyTypeEnum(Enum):
    NO_CHECK = 0
    POST_ARTICLE = 1
    POST_COMMENT = 2
    DO_LIKE = 3
    IMAGE_UPLOAD = 4



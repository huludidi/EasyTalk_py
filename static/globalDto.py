import json
from flask import jsonify

# 管理员账号
ADMIN_EMAIL = ["2488687107@qq.com"]


# 审核权限
class Audit:
    def __init__(self, commentAudit=None, postAudit=None):
        self.commentAudit = commentAudit
        self.postAudit = postAudit

    def to_dict(self):
        return {
            'commentAudit': self.commentAudit,
            'postAudit': self.postAudit,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getCommentAudit(self):
        return self.commentAudit

    def getPostAudit(self):
        return self.postAudit

    def setCommentAudit(self, commentaudit):
        self.commentAudit = commentaudit

    def setPostAudit(self, postaudit):
        self.postAudit = postaudit


# 评论设置
class Comment:
    def __init__(self, commentDayCountThreshold=None, commentOpen=None):
        self.commentDayCountThreshold = commentDayCountThreshold
        self.commentOpen = commentOpen

    def to_dict(self):
        return {
            'commentDayCountThreshold': self.commentDayCountThreshold,
            'commentOpen': self.commentOpen,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getcommentDayCountThreshold(self):
        return self.commentDayCountThreshold

    def getcommentOpen(self):
        return self.commentOpen

    def setcommentDayCountThreshold(self, commentDayCountThreshold):
        self.commentDayCountThreshold = commentDayCountThreshold

    def setcommentOpen(self, commentOpen):
        self.commentOpen = commentOpen


# 邮件发送设置
class Email:
    def __init__(self, emailContent=None, emailTitle=None):
        self.emailContent = emailContent
        self.emailTitle = emailTitle

    def to_dict(self):
        return {
            'emailContent': self.emailContent,
            'emailTitle': self.emailTitle,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getemailContent(self):
        return self.emailContent

    def getemailTitle(self):
        return self.emailTitle

    def setemailContent(self, emailContent):
        self.emailContent = emailContent

    def setemailTitle(self, emailTitle):
        self.emailTitle = emailTitle


# 点赞数设置
class Like:
    def __init__(self, likeDayCountThreshold=None):
        self.likeDayCountThreshold = likeDayCountThreshold

    def to_dict(self):
        return {
            'likeDayCountThreshold': self.likeDayCountThreshold,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getlikeDayCountThreshold(self):
        return self.likeDayCountThreshold

    def setlikeDayCountThreshold(self, likeDayCountThreshold):
        self.likeDayCountThreshold = likeDayCountThreshold


# 附件设置
class Post:
    def __init__(self, attachmentSize=None, dayImageUploadCount=None, postDayCountThreshold=None, postIntegral=None):
        self.attachmentSize = attachmentSize
        self.dayImageUploadCount = dayImageUploadCount
        self.postDayCountThreshold = postDayCountThreshold

    def to_dict(self):
        return {
            'attachmentSize': self.attachmentSize,
            'dayImageUploadCount': self.dayImageUploadCount,
            'postDayCountThreshold': self.postDayCountThreshold,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getattachmentSize(self):
        return self.attachmentSize

    def getdayImageUploadCount(self):
        return self.dayImageUploadCount

    def getpostDayCountThreshold(self):
        return self.postDayCountThreshold

    def setattachmentSize(self, attachmentSize):
        self.attachmentSize = attachmentSize

    def setdayImageUploadCount(self, dayImageUploadCount):
        self.dayImageUploadCount = dayImageUploadCount

    def setpostDayCountThreshold(self, postDayCountThreshold):
        self.postDayCountThreshold = postDayCountThreshold


# 注册设置
class Register:
    def __init__(self, registerWelcomInfo=None):
        self.registerWelcomInfo = registerWelcomInfo

    def to_dict(self):
        return {
            'registerWelcomInfo': self.registerWelcomInfo,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getregisterWelcomInfo(self):
        return self.registerWelcomInfo

    def setlregisterWelcomInfo(self, registerWelcomInfo):
        self.registerWelcomInfo = registerWelcomInfo


# 文件上传
class FileUpload:
    def __init__(self, localPath=None, originalFileName=None):
        self.localPath = localPath
        self.originalFileName = originalFileName

    def to_dict(self):
        return {
            'localPath': self.localPath,
            'originalFileName': self.originalFileName,

        }

    def getlocalPath(self):
        return self.localPath

    def setlocalPath(self, localPath):
        self.localPath = localPath

    def getoriginalFileName(self):
        return self.originalFileName

    def setoriginalFileName(self, originalFileName):
        self.originalFileName = originalFileName


class SysSettingDto:

    def __init__(self, audit=None, comment=None, post=None, like=None, email=None,
                 register=None):
        self.audit = audit
        self.comment = comment
        self.post = post
        self.like = like
        self.email = email
        self.register = register

    def to_dict(self):
        return {
            'audit': self.audit,
            'comment': self.comment,
            'post': self.post,
            'like': self.like,
            'email': self.email,
            'register': self.register,
        }

    def setAudit(self, audit):
        self.audit = audit

    def setComment(self, comment):
        self.comment = comment

    def setPost(self, post):
        self.post = post

    def setLike(self, like):
        self.like = like

    def setEmail(self, email):
        self.email = email

    def setRegister(self, register):
        self.register = register

    def getAudit(self):
        return self.audit

    def getComment(self):
        return self.comment

    def getPost(self):
        return self.post

    def getLike(self):
        return self.like

    def getEmail(self):
        return self.email

    def getRegister(self):
        return self.register

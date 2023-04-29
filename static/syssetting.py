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
    def __init__(self, commentDayCountThreshold=None, commentIntegral=None, commentOpen=None):
        self.commentDayCountThreshold = commentDayCountThreshold
        self.commentIntegral = commentIntegral
        self.commentOpen = commentOpen

    def to_dict(self):
        return {
            'commentDayCountThreshold': self.commentDayCountThreshold,
            'commentIntegral': self.commentIntegral,
            'commentOpen': self.commentOpen,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getcommentDayCountThreshold(self):
        return self.commentDayCountThreshold

    def getcommentIntegral(self):
        return self.commentIntegral

    def getcommentOpen(self):
        return self.commentOpen

    def setcommentDayCountThreshold(self, commentDayCountThreshold):
        self.commentDayCountThreshold = commentDayCountThreshold

    def setcommentIntegral(self, commentIntegral):
        self.commentIntegral = commentIntegral

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
        self.postIntegral = postIntegral

    def to_dict(self):
        return {
            'attachmentSize': self.attachmentSize,
            'dayImageUploadCount': self.dayImageUploadCount,
            'postDayCountThreshold': self.postDayCountThreshold,
            'postIntegral': self.postIntegral,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def getattachmentSize(self):
        return self.attachmentSize

    def getdayImageUploadCount(self):
        return self.dayImageUploadCount

    def getpostDayCountThreshold(self):
        return self.getpostDayCountThreshold

    def getpostIntegral(self):
        return self.postIntegral

    def setattachmentSize(self, attachmentSize):
        self.attachmentSize = attachmentSize

    def setdayImageUploadCount(self, dayImageUploadCount):
        self.dayImageUploadCount = dayImageUploadCount

    def setpostDayCountThreshold(self, postDayCountThreshold):
        self.postDayCountThreshold = postDayCountThreshold

    def setpostIntegral(self, postIntegral):
        self.postIntegral = postIntegral


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

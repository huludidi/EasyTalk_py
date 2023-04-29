# from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, TIMESTAMP, Text, text
# from sqlalchemy.dialects.mysql import TINYINT, VARCHAR
# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()
# metadata = Base.metadata
from datetime import datetime

from sqlalchemy import text

from exts import db


class EmailCode(db.Model):
    __tablename__ = 'email_code'
    __table_args__ = {'comment': '邮箱验证码'}

    email = db.Column(db.String(150), primary_key=True, nullable=False, comment='邮箱')
    code = db.Column(db.String(6), primary_key=True, nullable=False, comment='编号')
    create_time = db.Column(db.DateTime, comment='创建时间')
    status = db.Column(db.Boolean, comment='0:未使用  1:已使用')


class ForumArticle(db.Model):
    __tablename__ = 'forum_article'
    __table_args__ = {'comment': '文章信息'}

    article_id = db.Column(db.String(15), primary_key=True, comment='文章ID')
    board_id = db.Column(db.Integer, index=True, comment='板块ID')
    board_name = db.Column(db.String(50), comment='板块名称')
    p_board_id = db.Column(db.Integer, index=True, comment='父级板块ID')
    p_board_name = db.Column(db.String(50), comment='父板块名称')
    user_id = db.Column(db.String(15), nullable=False, index=True, comment='用户ID')
    nick_name = db.Column(db.String(20), nullable=False, comment='昵称')
    user_ip_address = db.Column(db.String(100), comment='最后登录ip地址')
    title = db.Column(db.String(150), nullable=False, index=True, comment='标题')
    cover = db.Column(db.String(100), comment='封面')
    content = db.Column(db.Text, comment='内容')
    markdown_content = db.Column(db.Text, comment='markdown内容')
    editor_type = db.Column(db.Integer, nullable=False, comment='0:富文本编辑器 1:markdown编辑器')
    summary = db.Column(db.String(200), comment='摘要')
    post_time = db.Column(db.DateTime, nullable=False, index=True, comment='发布时间')
    last_update_time = db.Column(db.TIMESTAMP)
    read_count = db.Column(db.Integer, server_default=text('0'), comment='阅读数量')
    good_count = db.Column(db.Integer, server_default=text('0'), comment='点赞数')
    comment_count = db.Column(db.Integer, server_default=text('0'), comment='评论数')
    top_type = db.Column(db.Boolean, index=True, server_default=text('0'), comment='0未置顶  1:已置顶')
    attachment_type = db.Column(db.Boolean, comment='0:没有附件  1:有附件')
    status = db.Column(db.Integer, comment='-1已删除 0:待审核  1:已审核 ')


class ForumArticleAttachment(db.Model):
    __tablename__ = 'forum_article_attachment'
    __table_args__ = {'comment': '文件信息'}

    file_id = db.Column(db.String(15), primary_key=True, comment='文件ID')
    article_id = db.Column(db.String(15), nullable=False, index=True, comment='文章ID')
    user_id = db.Column(db.String(15), index=True, comment='用户id')
    file_size = db.Column(db.BigInteger, comment='文件大小')
    file_name = db.Column(db.String(200), comment='文件名称')
    download_count = db.Column(db.Integer, comment='下载次数')
    file_path = db.Column(db.String(100), comment='文件路径')
    file_type = db.Column(db.Integer, comment='文件类型')
    integral = db.Column(db.Integer, comment='下载所需积分')


class ForumArticleAttachmentDownload(db.Model):
    __tablename__ = 'forum_article_attachment_download'
    __table_args__ = {'comment': '用户附件下载'}

    file_id = db.Column(db.String(15), primary_key=True, nullable=False, comment='文件ID')
    user_id = db.Column(db.String(15), primary_key=True, nullable=False, comment='用户id')
    article_id = db.Column(db.String(15), nullable=False, comment='文章ID')
    download_count = db.Column(db.Integer, server_default=text('1'), comment='文件下载次数')


class ForumBoard(db.Model):
    __tablename__ = 'forum_board'
    __table_args__ = {'comment': '文章板块信息'}

    board_id = db.Column(db.Integer, primary_key=True, comment='板块ID')
    p_board_id = db.Column(db.Integer, comment='父级板块ID')
    board_name = db.Column(db.String(50), comment='板块名')
    cover = db.Column(db.String(50), comment='封面')
    board_desc = db.Column(db.String(150), comment='描述')
    sort = db.Column(db.Integer, comment='排序')
    post_type = db.Column(db.Boolean, server_default=text('1'), comment='0:只允许管理员发帖 1:任何人可以发帖')

    def to_dict(self):
        return {
            "board_id": self.board_id,
            "p_board_id": self.p_board_id,
            "board_name": self.board_name,
            "cover": self.cover,
            "board_desc": self.board_desc,
            "sort": self.sort,
            "post_type": self.post_type,
        }


class ForumComment(db.Model):
    __tablename__ = 'forum_comment'
    __table_args__ = {'comment': '评论'}

    comment_id = db.Column(db.Integer, primary_key=True, comment='评论ID')
    p_comment_id = db.Column(db.Integer, index=True, comment='父级评论ID')
    article_id = db.Column(db.String(15), nullable=False, index=True, comment='文章ID')
    content = db.Column(db.String(800), comment='回复内容')
    img_path = db.Column(db.String(150), comment='图片')
    user_id = db.Column(db.String(15), nullable=False, index=True, comment='用户ID')
    nick_name = db.Column(db.String(20), comment='昵称')
    user_ip_address = db.Column(db.String(100), comment='用户ip地址')
    reply_user_id = db.Column(db.String(15), comment='回复人ID')
    reply_nick_name = db.Column(db.String(20), comment='回复人昵称')
    top_type = db.Column(db.Boolean, index=True, server_default=text('0'), comment='0:未置顶  1:置顶')
    post_time = db.Column(db.DateTime, index=True, comment='发布时间')
    good_count = db.Column(db.Integer, server_default=text('0'), comment='good数量')
    status = db.Column(db.Boolean, index=True, comment='0:待审核  1:已审核')


class LikeRecord(db.Model):
    __tablename__ = 'like_record'
    __table_args__ = (
        db.Index('idx_key', 'object_id', 'user_id', 'op_type', unique=True),
        db.Index('idx_user_id', 'user_id', 'op_type'),
        {'comment': '点赞记录'}
    )

    op_id = db.Column(db.Integer, primary_key=True, comment='自增ID')
    op_type = db.Column(db.Integer, comment='操作类型0:文章点赞 1:评论点赞')
    object_id = db.Column(db.String(15), nullable=False, comment='主体ID')
    user_id = db.Column(db.String(15), nullable=False, comment='用户ID')
    create_time = db.Column(db.DateTime, comment='发布时间')
    author_user_id = db.Column(db.String(15), comment='主体作者ID')


class SysSetting(db.Model):
    __tablename__ = 'sys_setting'
    __table_args__ = {'comment': '系统设置信息'}

    code = db.Column(db.String(10), primary_key=True, comment='编号')
    json_content = db.Column(db.String(500), comment='设置信息')


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    __table_args__ = {'comment': '用户信息'}

    user_id = db.Column(db.String(15), primary_key=True, comment='用户ID')
    nick_name = db.Column(db.String(20), unique=True, comment='昵称')
    email = db.Column(db.String(150), unique=True, comment='邮箱')
    password = db.Column(db.String(150), comment='密码')
    sex = db.Column(db.Integer, comment='0:女 1:男')
    person_description = db.Column(db.String(200), comment='个人描述')
    join_time = db.Column(db.DateTime, comment='加入时间')
    last_login_time = db.Column(db.DateTime, comment='最后登录时间')
    last_login_ip = db.Column(db.String(15), comment='最后登录IP')
    last_login_ip_address = db.Column(db.String(100), comment='最后登录ip地址')
    school = db.Column(db.String(100), comment='用户学校')
    school_email = db.Column(db.VARCHAR(150), comment='用户的学校邮箱')
    status = db.Column(db.Boolean, comment='0:禁用 1:正常')


class UserIntegralRecord(db.Model):
    __tablename__ = 'user_integral_record'
    __table_args__ = {'comment': '用户积分记录表'}

    record_id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    user_id = db.Column(db.String(15), comment='用户ID')
    oper_type = db.Column(db.Integer, comment='操作类型')
    integral = db.Column(db.Integer, comment='积分')
    create_time = db.Column(db.DateTime, comment='创建时间')


class UserMessage(db.Model):
    __tablename__ = 'user_message'
    __table_args__ = (
        db.Index('idx_key', 'article_id', 'comment_id', 'send_user_id', 'message_type', unique=True),
        {'comment': '用户消息'}
    )

    message_id = db.Column(db.Integer, primary_key=True, comment='自增ID')
    received_user_id = db.Column(db.String(15), index=True, comment='接收人用户ID')
    article_id = db.Column(db.String(15), comment='文章ID')
    article_title = db.Column(db.String(150), comment='文章标题')
    comment_id = db.Column(db.Integer, comment='评论ID')
    send_user_id = db.Column(db.String(15), comment='发送人用户ID')
    send_nick_name = db.Column(db.String(20), comment='发送人昵称')
    message_type = db.Column(db.Integer, index=True, comment='0:系统消息 1:评论 2:文章点赞  3:评论点赞 4:附件下载')
    message_content = db.Column(db.String(1000), comment='消息内容')
    status = db.Column(db.Integer, index=True, comment='1:未读 2:已读')
    create_time = db.Column(db.DateTime, comment='创建时间')

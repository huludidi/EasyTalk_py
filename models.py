import json
from datetime import datetime
from math import ceil

from flask import abort, session
from sqlalchemy import text, func

from exts import db
from static.enums import globalinfoEnum, MessageTypeEnum


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
    author_id = db.Column(db.String(15), nullable=False, index=True, comment='用户ID')
    nick_name = db.Column(db.String(20), nullable=False, comment='昵称')
    author_ip_address = db.Column(db.String(100), comment='最后登录ip地址')
    author_school = db.Column(db.String(100), comment='作者学校')
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
    audit = db.Column(db.Boolean, comment='0:未通过  1:已通过')

    __mapper_args__ = {
        'exclude_properties': []
    }

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def searchlist(self, userinfo=None, p_board_id=None, board_id=None, orderType=None, filterType=None, pageNo=None):
        # try:
        ForumArticle.__mapper_args__['exclude_properties'] = ['markdown_content', 'content']
        condition = {}
        if p_board_id:
            condition['p_board_id'] = p_board_id
        if board_id:
            condition['board_id'] = board_id

        # 查询数据
        articles = db.session.query(ForumArticle).filter_by(**condition)
        articles = articles.filter(ForumArticle.status == 1, ForumArticle.audit == 1)
        # 对内容进行排序
        if orderType:
            if orderType == '0':  # 点赞最多
                articles = articles.order_by(ForumArticle.good_count.desc())
            elif orderType == '1':  # 评论最多
                articles = articles.order_by(ForumArticle.comment_count.desc())
        else:
            articles = articles.order_by(ForumArticle.post_time.desc())
        # 对内容进行筛选
        if userinfo and filterType:
            if filterType == '0':
                if userinfo.get('school') == None:
                    abort(400, description="请用户绑定学校")
                else:
                    articles = articles.filter(ForumArticle.author_school == userinfo.get('school'))
            elif filterType == '1':
                if json.loads(userinfo.get('lastLoginIpAddress')).get('region') == '未知':
                    abort(400, description="无法定位用户位置")
                else:
                    articles = articles.filter(ForumArticle.author_ip_address == userinfo.get('lastLoginIpAddress'))
        # 查询数据总数
        total_count = articles.count()
        # 计算分页参数
        start_index = (int(pageNo) - 1) * globalinfoEnum.PageSize.value
        end_index = start_index + globalinfoEnum.PageSize.value
        # 设置分页信息
        articles = articles.slice(start_index, end_index)

        # 将内容转换为字典列表
        result = []
        for article in articles:
            result.append({
                'articleId': article.article_id,
                'boardId': article.board_id,
                'boardName': article.board_name,
                'pBoardId': article.p_board_id,
                'pBoardName': article.p_board_name,
                'authorId': article.author_id,
                'nickName': article.nick_name,
                'authorSchool': article.author_school,
                'authorIpAddress': article.author_ip_address,
                'title': article.title,
                'cover': article.cover,
                'summary': article.summary,
                'postTime': article.post_time.strftime('%Y-%m-%d %H:%M:%S'),
                'lastUpdateTime': article.last_update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'readCount': article.read_count,
                'goodCount': article.good_count,
                'commentCount': article.comment_count,
                'topType': article.top_type,
                'status': article.status,
                'audit': article.audit
            })
        return {
            'totalCount': total_count,
            'pageNo': pageNo,
            'pageSize': globalinfoEnum.PageSize.value,
            'pageTotal': ceil(total_count / globalinfoEnum.PageSize.value),
            'list': result
        }


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

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
    status = db.Column(db.Integer, server_default=text('0'), index=True, comment='0:待审核  1:已审核')
    audit = db.Column(db.Boolean, index=True, comment='0:审核通过  1:审核未通过')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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

    def dolike(self, objectid, optype, userid):
        try:
            usermessage = UserMessage()
            # 文章点赞
            if int(optype) == globalinfoEnum.ARTICLE_LIKE.value:
                article = ForumArticle.query.filter_by(article_id=objectid).first()
                if not article:
                    abort(500, description="文章不存在")
                # likecord = articleLike(articleid, article, userid, optype)
                likecord = LikeRecord.query.filter_by(object_id=objectid, user_id=userid, op_type=optype).first()
                try:
                    if not likecord:
                        new_likecord = LikeRecord(op_type=optype, object_id=objectid, user_id=userid,
                                                  create_time=datetime.now(),
                                                  author_user_id=article.author_id)
                        article.good_count += 1
                        db.session.add(new_likecord)
                        db.session.commit()
                    else:
                        db.session.delete(likecord)
                        article.good_count -= 1
                        db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    abort(422)
                usermessage.article_id = objectid
                usermessage.comment_id = 0
                usermessage.article_title = article.title
                usermessage.message_type = MessageTypeEnum.ARTICLE_LIKE.value.get('type')
                usermessage.received_user_id = article.author_id
            #     评论点赞
            else:
                comment = ForumComment.query.filter_by(comment_id=objectid).first()
                if not comment:
                    abort(500, description="评论不存在")
                likecord = LikeRecord.query.filter_by(object_id=objectid, user_id=userid, op_type=optype).first()
                try:
                    if not likecord:
                        new_likecord = LikeRecord(op_type=optype, object_id=objectid, user_id=userid,
                                                  create_time=datetime.now(),
                                                  author_user_id=comment.user_id)
                        comment.good_count += 1
                        db.session.add(new_likecord)
                        db.session.commit()
                    else:
                        db.session.delete(likecord)
                        comment.good_count -= 1
                        db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    abort(422)
                usermessage.article_id = 0
                usermessage.comment_id = comment.comment_id
                usermessage.article_title = 0
                usermessage.message_type = MessageTypeEnum.COMMENT_LIKE.value.get('type')
                usermessage.received_user_id = comment.user_id
            usermessage.create_time = datetime.now()
            usermessage.send_user_id = userid
            usermessage.send_nick_name = session['userInfo'].get('nickName')
            usermessage.status = 1
            if not likecord and userid != usermessage.received_user_id:
                messageinfo = UserMessage.query.filter_by(article_id=usermessage.article_id,
                                                          comment_id=usermessage.comment_id,
                                                          send_user_id=usermessage.send_user_id,
                                                          message_type=usermessage.message_type).first()
                if not messageinfo:
                    db.session.add(usermessage)
                    db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            abort(422)


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

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
    status = db.Column(db.Integer, index=True, server_default=text('1'), comment='1:未读 2:已读')
    create_time = db.Column(db.DateTime, comment='创建时间')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SchoolInfo(db.Model):
    __tablename__ = 'school_info'

    id = db.Column(db.Integer, primary_key=True)
    ch_name = db.Column(db.String(255))
    en_name = db.Column(db.String(255))
    longitude = db.Column(db.String(255))
    latitude = db.Column(db.String(255))
    cover = db.Column(db.String(255))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

import html
import json
import os
from math import ceil

from PIL import Image

import config

from datetime import datetime
from flask import Blueprint, request, session, abort, make_response, send_file, g

from Audit.imageAudit import image_audit
from Audit.textAudit import textAudit
from functions import SuccessResponse, convert_line_to_tree, generate_random_string, \
    uploadFile2Local, generate_random_number, getImageList
from decorators import check_params, login_required, rate_limit
from exts import db
from models import ForumBoard, ForumArticle, ForumArticleAttachment, LikeRecord, UserMessage
from static.enums import globalinfoEnum, MessageTypeEnum, FileUploadTypeEnum, AttachmentTypeEnum, \
    UserOperFrequencyTypeEnum

bp = Blueprint("ForumArticle", __name__, url_prefix="/forum")


# 板块校验
def resetBoardInfo(isAdmin, article):
    pboard = ForumBoard.query.filter_by(board_id=article.p_board_id).first()
    if not pboard or (pboard.post_type == 0 and not isAdmin):
        abort(400, description="一级板块不存在")
    article.p_board_name = pboard.board_name
    if article.board_id and article.board_id != 0:
        board = ForumBoard.query.filter_by(board_id=article.board_id).first()
        if not board or (board.post_type == 0 and not isAdmin):
            abort(400, description="二级板块不存在")
        article.board_name = board.board_name
    else:
        article.board_id = 0
        article.board_name = None


# 附件上传
def uploadAttachment(article, forumattachment, file, isupload):
    allowsizeMb = g.postInfo.getattachmentSize()
    allowsize = allowsizeMb * 1024 * 1024
    filesize = len(file.read())
    if filesize > allowsize:
        abort(400, description="附件最大只能上传" + str(allowsizeMb) + "MB")

    # 修改
    new_attachment = None
    if isupload:
        attachment = ForumArticleAttachment.query.filter_by(article_id=article.article_id).first()
        # 若修改了附件，先删除原文件
        if attachment:
            try:
                new_attachment = attachment
                os.remove(config.FILE_PATH + '/' + config.ATTACHMENT_FOLDER + '/' + attachment.file_path)
            except Exception as e:
                print(e)
                abort(500)

    fileuploadDto = uploadFile2Local(file, config.ATTACHMENT_FOLDER, FileUploadTypeEnum.ARTICLE_ATTACHMENT)
    if not new_attachment:
        forumattachment.file_id = generate_random_number(15)
        forumattachment.article_id = article.article_id
        forumattachment.file_name = fileuploadDto.getoriginalFileName()
        forumattachment.file_path = fileuploadDto.getlocalPath()
        forumattachment.file_size = filesize
        forumattachment.download_count = 0
        forumattachment.file_type = AttachmentTypeEnum.ZIP.value.get('type')
        db.session.add(forumattachment)
    else:
        attachment.file_name = fileuploadDto.getoriginalFileName()
        attachment.file_size = filesize
        attachment.file_path = fileuploadDto.getlocalPath()


@bp.route("/loadArticle", methods=['POST'])
def loadArticle():
    boardId = request.values.get('boardId')
    pBoardId = request.values.get('pBoardId')
    orderType = request.values.get('orderType')  # 0:点赞最多 1:评论最多
    filterType = request.values.get('filterType')  # 0:与我同校 1:与我同城
    pageNo = request.values.get('pageNo')
    userinfo = session.get('userInfo')
    if boardId == '':
        boardId = None
    if pBoardId == '':
        pBoardId = None
    if orderType == '':
        orderType = None
    if filterType == '':
        filterType = None
    if not pageNo:
        pageNo = 1
    forumarticle = ForumArticle()
    data = forumarticle.searchlist(userinfo=userinfo, p_board_id=pBoardId, board_id=boardId, orderType=orderType,
                                   filterType=filterType, pageNo=pageNo)
    return SuccessResponse(data=data)


@bp.route("/getArticleDetail", methods=['POST'])
@check_params
def getArticleDetail():
    articleid = request.values.get('articleId')
    article = ForumArticle.query.filter_by(article_id=articleid).first()
    # 判断是否可以访问
    if not article or (article.status != 1 and (
            session.get('userInfo') is None or json.loads(session['userInfo']).get(
        'userId') != article.author_id or not
            session['isAdmin'])):
        abort(404)
    # 打包返回结果
    article.read_count += 1
    result = {}
    # 有附件
    if article.attachment_type:
        attachment = ForumArticleAttachment.query.filter_by(article_id=article.article_id).first()
        result['attachment'] = attachment.to_dict()
    else:
        result['attachment'] = None
    # 是否已点赞
    if session.get('userInfo'):
        likerecord = LikeRecord.query.filter_by(
            object_id=article.article_id, user_id=session['userInfo'].get('userId'),
            op_type=globalinfoEnum.ARTICLE_LIKE.value).first()
        if likerecord:
            result['haveLike'] = True
        else:
            result['haveLike'] = False
    db.session.commit()
    article.post_time = article.post_time.strftime('%Y-%m-%d %H:%M:%S')
    article.last_update_time = article.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
    result['forumArticle'] = article.to_dict()
    return SuccessResponse(data=result)


@bp.route("/doLike", methods=['POST'])
@login_required
@check_params
@rate_limit(limit_type=UserOperFrequencyTypeEnum.DO_LIKE)
def doLike():
    articleid = request.values.get('articleId')
    optype = request.values.get('opType')
    userid = session['userInfo'].get('userId')
    likerecord = LikeRecord()
    likerecord.dolike(objectid=articleid, optype=optype, userid=userid)
    return SuccessResponse()


@bp.route("/attachmentDownload")
@login_required
@check_params
def attachmentDownload():
    fileid = request.values.get('fileId')
    userinfo = session['userInfo']
    file = ForumArticleAttachment.query.filter_by(file_id=fileid).first()
    if file is None:
        abort(404, description="文件不存在")
    else:
        file.download_count += 1
        # 记录消息
        article = ForumArticle.query.filter_by(article_id=file.article_id).first()
        usermessage = UserMessage(received_user_id=file.user_id, article_id=article.article_id,
                                  article_title=article.title, send_user_id=session['userInfo'].get(
                'userId'), send_nick_name=session['userInfo'].get(
                'nickName'), message_type=MessageTypeEnum.ATTACHMENT_DOWNLOAD.value.get(
                'type'), message_content=f"用户{userinfo['userId']}下载了{article.title}中的附件",
                                  create_time=datetime.now())
        db.session.add(usermessage)
        db.session.commit()
        filename = file.file_name
        filename = filename.encode("utf-8").decode("latin1")  # 编码转换
        response = make_response(send_file(config.FILE_PATH + '/' + config.ATTACHMENT_FOLDER + '/' + file.file_path))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
        return response


@bp.route("/loadBoard4Post", methods=['POST'])
@login_required
def loadBoard4Post():
    userinfo = session['userInfo']
    formboardinfo = ForumBoard.query.order_by('sort').all()
    if not userinfo.get('isAdmin'):
        formboardinfo = formboardinfo.filter_by(post_type=1)
    formboardinfoList = []
    for item in formboardinfo:
        formboardinfoList.append(item.to_dict())
    return SuccessResponse(data=convert_line_to_tree(formboardinfoList, 0))


@bp.route("/postArticle", methods=['POST'])
@login_required
@rate_limit(limit_type=UserOperFrequencyTypeEnum.POST_ARTICLE)
def postArticle():
    cover = request.files.get('cover')  # 封面
    attachment = request.files.get('attachment')  # 附件
    title = request.values.get('title')  # 标题
    pboardid = request.values.get('p_board_id')
    boardid = request.values.get('board_id')
    summary = request.values.get('summary')  # 摘要
    editortype = request.values.get('editor_type')
    content = request.values.get('content')
    markdowncontent = request.values.get('markdown_content')
    userinfo = session['userInfo']
    # 参数判断
    if not title or len(title) > 150:
        abort(400)
    if not pboardid or not editortype or not content:
        abort(400)
    if len(summary) > 200:
        abort(400)
    if int(editortype) != globalinfoEnum.RICH.value and int(editortype) != globalinfoEnum.MARKDOWN.value:
        abort(400)
    # 去html
    title = html.escape(title)
    forumarticle = ForumArticle(p_board_id=pboardid,
                                board_id=boardid,
                                title=title,
                                summary=summary,
                                content=content,
                                )
    if int(editortype) == globalinfoEnum.MARKDOWN.value and not markdowncontent:
        abort(400)
    forumarticle.markdown_content = markdowncontent
    forumarticle.editor_type = editortype
    forumarticle.author_id = userinfo.get('userId')
    forumarticle.nick_name = userinfo.get('nickName')
    forumarticle.author_school = userinfo.get('school')
    forumarticle.author_ip_address = userinfo.get('lastLoginIpAddress')
    # 附件信息
    forumattachment = ForumArticleAttachment(user_id=userinfo.get('userId'))
    contentaudit, imageaudit = post(forumarticle, forumattachment, cover, attachment, userinfo.get('isAdmin'))
    db.session.commit()
    result = {
        "contentaudit": contentaudit,
        "imageaudit": imageaudit,
        "audit": forumarticle.audit,
        "article_id": forumarticle.article_id
    }
    return SuccessResponse(data=result)


# 文章上传
def post(forumarticle, forumattachment, cover, attachment, isadmin):
    try:
        # 检查板块信息
        resetBoardInfo(isadmin, forumarticle)
        curdate = datetime.now()
        forumarticle.article_id = generate_random_string(15)
        forumarticle.post_time = curdate
        forumarticle.last_update_time = curdate
        # 如果有封面则上传封面
        if not cover:
            # 上传默认封面
            board = ForumBoard.query.filter_by(p_board_id=0, board_id=forumarticle.p_board_id).first()
            if not board:
                abort(400)
            forumarticle.cover = board.cover
        else:
            fileuploaddto = uploadFile2Local(cover, config.PICTURE_FOLDER, FileUploadTypeEnum.ARTICLE_COVER)
            forumarticle.cover = fileuploaddto.getlocalPath()
        # 如果有附件则上传
        if attachment:
            uploadAttachment(forumarticle, forumattachment, attachment, False)
            forumarticle.attachment_type = 1
        else:
            forumarticle.attachment_type = 0
        # 文章审核
        forumarticle.status = 1
        contentaudit = True
        imageaudit = True
        if g.auditInfo.getPostAudit():
            contentaudit = textAudit(forumarticle.content)
            if cover:
                imageaudit = image_audit(config.IMAGE_PATH + '/' + forumarticle.cover)
            if contentaudit and imageaudit:
                forumarticle.audit = 1
            else:
                forumarticle.audit = 0
        else:
            forumarticle.audit = 1

        # 替换图片
        content = forumarticle.content
        # 替换文本中的/temp/
        if content:
            # 从temp中移走图片
            month = resetimage(content)
            replacemonth = '/' + month + '/'
            content = content.replace('/temp/', replacemonth)
            forumarticle.content = content
            markdowncontent = forumarticle.markdown_content
            if markdowncontent:
                markdowncontent = markdowncontent.replace('/temp/', replacemonth)
                forumarticle.markdown_content = markdowncontent
        db.session.add(forumarticle)
        return contentaudit, imageaudit
    except Exception as e:
        print(e)
        abort(422)


# 从html解析image，并将image从temp文件中移入picture文件夹
def resetimage(html):
    month = datetime.now().strftime("%Y%m")
    imagelist = getImageList(html)
    for img in imagelist:
        if img and 'temp' in img:
            imagepath = img.replace('/api/file/getImage/', '')
            imagefilename = month + '/' + img.split("/")[-1]
            # 如果没有文件夹则创建
            if not os.path.exists(config.IMAGE_PATH + '/' + month):
                os.mkdir(config.IMAGE_PATH + month)
            #     取出temp中的照片放入202305等文件夹
            image = Image.open(config.IMAGE_PATH + '/' + imagepath)
            image.save(config.IMAGE_PATH + '/' + imagefilename)
    return month


@bp.route("/articleDetail4Update", methods=['POST'])
@login_required
@check_params
def articleDetail4Update():
    articleid = request.values.get('articleId')
    userinfo = session['userInfo']
    article = ForumArticle.query.filter_by(article_id=articleid).first()
    attachment = None
    if not article or userinfo.get('userId') != article.author_id:
        abort(400, description="只有作者可以编辑文章")
    if article.attachment_type == 1:
        attachment = ForumArticleAttachment.query.filter_by(article_id=article.article_id).first()
    result = {}
    article.post_time = article.post_time.strftime('%Y-%m-%d %H:%M:%S')
    result['forumArticle'] = article.to_dict()
    if attachment:
        result['attachment'] = attachment.to_dict()
    else:
        result['attachment'] = None

    return SuccessResponse(data=result)


@bp.route("/updateArticle", methods=['POST'])
def updateArticle():
    articleid = request.values.get('article_id')
    attachmenttype = request.values.get('attachment_type')
    cover = request.files.get('cover')  # 封面
    attachment = request.files.get('attachment')  # 附件
    title = request.values.get('title')  # 标题
    pboardid = request.values.get('p_board_id')
    boardid = request.values.get('board_id')
    summary = request.values.get('summary')  # 摘要
    editortype = request.values.get('editor_type')
    content = request.values.get('content')
    markdowncontent = request.values.get('markdown_content')
    userinfo = session['userInfo']
    # 参数判断
    if not title or len(title) > 150:
        abort(400)
    if not pboardid or not editortype or not content or not articleid or not attachmenttype:
        abort(400)
    if len(summary) > 200:
        abort(400)
    if int(editortype) != globalinfoEnum.RICH.value and int(editortype) != globalinfoEnum.MARKDOWN.value:
        abort(400)
    if int(editortype) == globalinfoEnum.MARKDOWN.value and not markdowncontent:
        abort(400)
    # 去html
    title = html.escape(title)
    # 查找需要修改的文章
    forumarticle = ForumArticle.query.filter_by(article_id=articleid).first()
    if not forumarticle or (not userinfo.get('isAdmin') and forumarticle.author_id != userinfo.get('userId')):
        abort(400)
    #  修改信息
    forumarticle.p_board_id = pboardid
    forumarticle.board_id = boardid
    forumarticle.title = title
    forumarticle.summary = summary
    forumarticle.content = content
    forumarticle.attachment_type = int(attachmenttype)
    forumarticle.markdown_content = markdowncontent
    forumarticle.editor_type = int(editortype)
    forumarticle.author_id = userinfo.get('userId')
    forumarticle.nick_name = userinfo.get('nickName')
    forumarticle.author_school = userinfo.get('school')
    forumarticle.author_ip_address = userinfo.get('lastLoginIpAddress')
    # 附件信息
    forumattachment = ForumArticleAttachment()

    update(forumarticle, forumattachment, cover, attachment, userinfo.get('isAdmin'))
    db.session.commit()
    return SuccessResponse(data=forumarticle.article_id)


def update(forumarticle, forumattachment, cover, attachment, isadmin):
    forumarticle.last_update_time = datetime.now()
    resetBoardInfo(isadmin, forumarticle)
    # 如果有封面则上传封面
    if cover:
        os.remove(config.IMAGE_PATH + '/' + forumarticle.cover)
        fileuploaddto = uploadFile2Local(cover, config.PICTURE_FOLDER, FileUploadTypeEnum.ARTICLE_COVER)
        forumarticle.cover = fileuploaddto.getlocalPath()
    # 文章审核
    forumarticle.status = 1
    if g.auditInfo.getPostAudit():
        textaudit = textAudit(forumarticle.content)
        imageaudit = False
        if cover:
            imageaudit = image_audit(config.IMAGE_PATH + '/' + forumarticle.cover)
        if textaudit and imageaudit:
            forumarticle.audit = 1
        else:
            forumarticle.audit = 0
    # 如果有附件则更新
    if attachment:
        uploadAttachment(forumarticle, forumattachment, attachment, True)
    else:
        dbattachment = ForumArticleAttachment.query.filter_by(article_id=forumarticle.article_id).first()
        if dbattachment and forumarticle.attachment_type == 0:
            os.remove(config.FILE_PATH + '/' + config.ATTACHMENT_FOLDER + '/' + dbattachment.file_path)
            db.session.delete(dbattachment)

    # 替换图片
    content = forumarticle.content
    # 替换文本中的/temp/
    if content:
        # 从temp中移走图片
        month = resetimage(content)
        replacemonth = '/' + month + '/'
        content = content.replace('/temp/', replacemonth)
        forumarticle.content = content
        markdowncontent = forumarticle.markdown_content
        if markdowncontent:
            markdowncontent = markdowncontent.replace('/temp/', replacemonth)
            forumarticle.markdown_content = markdowncontent


@bp.route("/search", methods=['POST'])
def search():
    keyword = request.values.get('keyword')
    pageNo = request.values.get('pageNo')
    if not pageNo:
        pageNo = 1
    else:
        pageNo = int(pageNo)
    if len(keyword) < 2:
        abort(400, description="请求参数过短")
    result = {
        'totalCount': 0,
        'pageNo': 1,
        'pageSize': 7,
        'pageTotal': 0,
        'list': []
    }
    # 根据标题模糊查询文章
    articles = ForumArticle.query \
        .filter(ForumArticle.title.like(f'%{keyword}%'), ForumArticle.audit == 1)
    total = articles.count()
    articles = articles.paginate(page=pageNo, per_page=7).items
    for item in articles:
        item.post_time = item.post_time.strftime('%Y-%m-%d %H:%M:%S')
        item.last_update_time = item.last_update_time.strftime('%Y-%m-%d %H:%M:%S')
        result['list'].append(item.to_dict())
    result['totalCount'] = total
    result['pageTotal'] = ceil(total / 7)
    return SuccessResponse(data=result)

AK = "TlmqzUKYCMAtfm9txrMq9nXBtGGEYkou"
SECRET_KEY = "xiaoxiong"
CACHE_TYPE = 'simple'

# 数据库配置信息
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'easytalk'
USERNAME = 'root'
PASSWORD = '1234'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI

# 配置邮箱

# AIL_SERVER = 'smtp.qq.com'
MAIL_SERVER = 'smtp.qq.com'
MAIL_USE_SSL = False
MAIL_USE_TLS = False
MAIL_PORT = 25
MAIL_USERNAME = "2488687107@qq.com"
MAIL_PASSWORD = "oujctwcvgovqeacj"
MAIL_DEFAULT_SENDER = "2488687107@qq.com"

FILE_PATH = "E:/stdio/毕设/file"
# 上传图片地址
IMAGE_PATH = "E:/stdio/毕设/file/picture"
BOARD_FOLDER = "/board"
PICTURE_FOLDER = "/picture"
VIDEO_FOLDER = "/videos"
TEMP_FOLDER = "/temp"
AVATAR_FOLDER = "/avatar"
# 上传附件地址
ATTACHMENT_FOLDER = "/attachment"

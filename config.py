
SECRET_KEY = "xiaoxiong"

# 数据库配置信息
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'easytalk'
USERNAME = 'root'
PASSWORD = '1234'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI

# 配置邮箱
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_PORT = 465
MAIL_USERNAME = "1398471354@qq.com"
MAIL_PASSWORD = "bpsgwtwvwnxriahi"
MAIL_DEFAULT_SENDER = "1398471354@qq.com"


# ziefppvnudayfhda

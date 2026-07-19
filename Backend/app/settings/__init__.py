import os
from dotenv import load_dotenv
load_dotenv()

# 数据库
DB_URI = os.environ["DB_URI"]

# oauth2
SECRET_KEY = "496263e899ac2881a1565aa368c546ad4a35a548cc921811156396d3155b5873"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 超过多少分钟重新验证

# ip
url = "http://127.0.0.1:8000"

# 邮箱相关配置
MAIL_USERNAME = os.environ["MAIL_USERNAME"]
MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_PORT = int(os.environ.get("MAIL_PORT", "465"))
MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.qq.com")
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "AI-Name")
MAIL_STARTTLS = os.environ.get("MAIL_STARTTLS", "False").lower() == "true"
MAIL_SSL_TLS = os.environ.get("MAIL_SSL_TLS", "True").lower() == "true"
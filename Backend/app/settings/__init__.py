import os
from dotenv import load_dotenv
load_dotenv()

# 数据库
DB_URI = os.environ["DB_URI"]
TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

# oauth2
SECRET_KEY = "496263e899ac2881a1565aa368c546ad4a35a548cc921811156396d3155b5873"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 超过多少分钟重新验证

# 前端地址（注册/邀请链接发往的页面，生产环境可用环境变量覆盖）
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# 邮箱相关配置
MAIL_USERNAME = os.environ["MAIL_USERNAME"]
MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_PORT = int(os.environ.get("MAIL_PORT", "465"))
MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.qq.com")
MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "AI-Name")
MAIL_STARTTLS = os.environ.get("MAIL_STARTTLS", "False").lower() == "true"
MAIL_SSL_TLS = os.environ.get("MAIL_SSL_TLS", "True").lower() == "true"

# 个人知识库数量限制
PERSONAL_KB_LIMIT = 5

# sqladmin 后台独立账号(运维侧使用,不与用户表耦合)
# 未配置时启动会直接报错,防止 /admin 裸奔
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
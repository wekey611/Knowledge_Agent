import os
from dotenv import load_dotenv
load_dotenv()

# 数据库
DB_URI = os.environ["DB_URI"]

# oauth2
SECRET_KEY = "496263e899ac2881a1565aa368c546ad4a35a548cc921811156396d3155b5873"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 超过多少分钟重新验证
from  sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import DB_URI


# DB_URI = "mysql+pymysql://root:whj687898@127.0.0.1:3306/test?charset=utf8mb4"
# DB_URI = "mysql+pymysql://ka:123456@117.72.34.236:3306/ka"

engine = create_engine(DB_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class User_request(Base):
    __tablename__ = "users_request"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), nullable=False)
    reason = Column(String(1000))
    status = Column(String(20))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    approved_at = Column(TIMESTAMP(timezone=True))
    token = Column(String(50))
    # expire_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("(now() + interval 3 day)"))
    expire_at = Column(TIMESTAMP(timezone=True))

    status:
    {
        pending:待定
        approved：批准
        registered：已注册
        rejected：已拒绝
        null：空
    }
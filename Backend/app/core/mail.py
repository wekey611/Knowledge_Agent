from functools import lru_cache
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from pydantic import SecretStr
from app import settings


@lru_cache
def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )


mail_client = FastMail(get_mail_config())  # 全局单例


async def send_approve_email(email: str, register_url: str):
    """发送审批通过通知邮件"""
    message = MessageSchema(
        subject="注册邀请 - 您的申请已通过审批",
        recipients=[email],
        body=f"您的注册申请已通过审核，请在3天内点击以下链接完成注册：\n\n{register_url}\n\n链接有效期：3天",
        subtype="plain",
    )
    await mail_client.send_message(message)
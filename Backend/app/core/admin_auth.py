"""sqladmin 后台认证:独立账号密码,不与用户表耦合。

为什么独立账号:
- sqladmin 默认完全无鉴权,任何人访问 /admin 就能改库;
- 复用用户表 admin 角色会把"业务用户登录态"和"管理员登录态"耦合,
  一旦泄露一个 JWT,等于把 admin 后台拱手让人;
- 独立账号密码只在运维侧用,泄露面更小。

密码通过环境变量配置,不在仓库留痕。
"""
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app import settings


class AdminAuth(AuthenticationBackend):
    """sqladmin 认证后端:校验 ADMIN_USERNAME / ADMIN_PASSWORD。"""

    def __init__(self, secret_key: str):
        super().__init__(secret_key=secret_key)
        # 启动时校验环境变量,缺失直接报错,防止部署后裸奔。
        if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
            raise RuntimeError(
                "ADMIN_USERNAME / ADMIN_PASSWORD 必须配置,否则 /admin 不可用。"
            )

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")

        # 用恒定时间比较防时序攻击
        import hmac

        user_ok = hmac.compare_digest(
            str(username), str(settings.ADMIN_USERNAME)
        )
        pass_ok = hmac.compare_digest(
            str(password), str(settings.ADMIN_PASSWORD)
        )

        if user_ok and pass_ok:
            request.session.update({"admin": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        if not request.session.get("admin"):
            return RedirectResponse(
                request.url_for("admin:login"), status_code=302
            )
        return True

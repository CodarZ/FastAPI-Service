from typing import TYPE_CHECKING, Any, Mapping

from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError, BaseUser

from backend.common.exception.errors import TokenError
from backend.common.log import log
from backend.common.request.context import ctx
from backend.common.response.code import StandardResponseStatus
from backend.common.security.jwt import jwt_authentication
from backend.common.security.permission import permission_service
from backend.core.config import settings
from backend.utils.serializers import MsgSpecJSONResponse

if TYPE_CHECKING:
    from fastapi import Response
    from starlette.requests import HTTPConnection

    from backend.app.admin.schema.sys_user import SysUserDetail


class _AuthenticationError(AuthenticationError):
    """重写内部认证错误类"""

    def __init__(
        self,
        *,
        code: int = StandardResponseStatus.HTTP_401.code,
        msg: str = StandardResponseStatus.HTTP_401.msg,
        headers: dict[str, Any] | Mapping[str, str] | None = None,
    ) -> None:
        """初始化认证错误"""
        self.code = code
        self.msg = msg
        self.headers = headers


class _UserInfo(BaseUser):
    """用户信息包装类，用于满足 Starlette 的 BaseUser 接口要求"""

    def __init__(self, user_detail: 'SysUserDetail') -> None:
        self._user_detail = user_detail

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self._user_detail.username

    @property
    def identity(self) -> str:
        return str(self._user_detail.id)

    def __getattr__(self, name: str) -> Any:
        """代理所有属性访问到 SysUserDetail 实例"""
        return getattr(self._user_detail, name)


class JWTAuthMiddleware(AuthenticationBackend):
    """JWT 认证中间件"""

    @staticmethod
    def auth_exception_handler(conn: HTTPConnection, exc: AuthenticationError) -> Response:
        """覆盖内部认证错误处理方法"""

        if isinstance(exc, _AuthenticationError):
            content = {'code': exc.code, 'msg': exc.msg, 'data': None}
            return MsgSpecJSONResponse(content=content, status_code=exc.code)

        # 处理标准 AuthenticationError
        content = {'code': StandardResponseStatus.HTTP_401.code, 'msg': str(exc), 'data': None}
        return MsgSpecJSONResponse(content=content, status_code=StandardResponseStatus.HTTP_401.code)

    @staticmethod
    def extract_token(conn: HTTPConnection):
        """提取 Bearer Token"""

        authorization = conn.headers.get('Authorization')
        if not authorization:
            return None

        path = conn.url.path

        if path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
            return None

        schema, token = get_authorization_scheme_param(authorization)
        if schema.lower() != 'bearer':
            return None

        return token

    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, BaseUser] | None:
        """认证请求"""
        token = self.extract_token(conn)
        if not token:
            return None

        try:
            user_detail = await jwt_authentication(token)
            user = _UserInfo(user_detail)

            # 预加载用户权限到 ctx，供后续 RBAC 校验使用
            permissions = await permission_service.get_user_permissions(user_detail.id)
            ctx.permissions = permissions

        except TokenError as exc:
            raise _AuthenticationError(code=exc.code, msg=exc.detail, headers=exc.headers) from exc

        except Exception as e:
            log.exception('认证过程中出现未知错误: %s', str(e))
            # 确保 code 是整数类型，避免类型错误
            code = getattr(e, 'code', StandardResponseStatus.HTTP_500.code)
            if not isinstance(code, int):
                code = StandardResponseStatus.HTTP_500.code
            raise _AuthenticationError(
                code=code,
                msg=getattr(e, 'msg', StandardResponseStatus.HTTP_500.msg),
            ) from e

        return AuthCredentials(['authenticated']), user

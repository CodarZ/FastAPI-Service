from typing import TYPE_CHECKING, Any

from fastapi import HTTPException, status

from backend.common.response.code import CustomResponseCode, StandardResponseStatus

if TYPE_CHECKING:
    from starlette.background import BackgroundTask


class HTTPError(HTTPException):
    """自定义 HTTP 异常"""

    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None):
        super().__init__(status_code=code, detail=msg, headers=headers)


class ExceptionBase(Exception):
    """自定义异常基类，提供统一的结构：
    - code: 错误码（子类定义具体值）
    - msg: 错误信息（可选）
    - data: 附加数据（可选）
    - background: 后台任务（可选，用于在异常触发时执行异步任务）.
    """

    code: int

    def __init__(self, *, msg: str | None = None, data: Any = None, background: BackgroundTask | None = None):
        self.msg = msg
        self.data = data
        self.background = background


class RequestError(ExceptionBase):
    """请求错误：400（Bad Request）"""

    code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        *,
        msg: str | None = StandardResponseStatus.HTTP_400.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class AuthorizationError(ExceptionBase):
    """授权异常：401（Unauthorized）"""

    code = status.HTTP_401_UNAUTHORIZED

    def __init__(
        self,
        *,
        msg: str | None = StandardResponseStatus.HTTP_401.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class ForbiddenError(ExceptionBase):
    """禁止访问：403（Forbidden）"""

    code = status.HTTP_403_FORBIDDEN

    def __init__(
        self,
        *,
        msg: str | None = StandardResponseStatus.HTTP_403.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class NotFoundError(ExceptionBase):
    """资源未找到：404（Not Found）"""

    code = status.HTTP_404_NOT_FOUND

    def __init__(
        self,
        *,
        msg: str | None = StandardResponseStatus.HTTP_404.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class ConflictError(ExceptionBase):
    """资源冲突：409（Conflict）"""

    code = status.HTTP_409_CONFLICT

    def __init__(
        self,
        *,
        msg: str | None = StandardResponseStatus.HTTP_409.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class ServerError(ExceptionBase):
    """服务器内部错误：500（Internal Server Error）"""

    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *,
        msg: str | None = StandardResponseStatus.HTTP_500.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class GatewayError(ExceptionBase):
    """网关错误：502（Bad Gateway）"""

    code = status.HTTP_502_BAD_GATEWAY

    def __init__(
        self,
        *,
        msg: str | None = StandardResponseStatus.HTTP_502.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class CustomError(ExceptionBase):
    """自定义状态的异常"""

    def __init__(self, *, status: CustomResponseCode, data: Any = None, background: BackgroundTask | None = None):
        self.code = status.code
        super().__init__(msg=status.msg, data=data, background=background)


class TokenError(HTTPError):
    """Token 认证异常：401（Unauthorized）"""

    code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, msg: str = '用户身份认证失败', headers: dict[str, Any] | None = None):
        super().__init__(code=self.code, msg=msg, headers=headers or {'WWW-Authenticate': 'Bearer'})

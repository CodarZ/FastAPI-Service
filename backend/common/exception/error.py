from typing import TYPE_CHECKING, Any

from fastapi import HTTPException
from starlette import status

from backend.common.response import ResponseCode, ResponseStatus

if TYPE_CHECKING:
    from starlette.background import BackgroundTask


class HTTPError(HTTPException):
    """自定义 HTTP 异常."""

    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, str] | None = None) -> None:
        super().__init__(status_code=code, detail=msg, headers=headers)


class ExceptionBase(Exception):
    """自定义异常基类.

    提供统一的结构:
    - `code`: 异常码
    - `msg`:  异常信息（可选）
    - `data`: 附加数据（可选）
    - `background`: 后台任务（可选，用于在异常触发时执行异步任务）.
    """

    code: int

    def __init__(self, *, msg: str | None = None, data: Any = None, background: BackgroundTask | None = None) -> None:
        self.msg = msg
        self.data = data
        self.background = background


class CustomError(ExceptionBase):
    """自定义状态的异常.

    适用于需要自定义状态码和消息的场景，通过传入 `ResponseStatus` 来创建异常实例.
    """

    def __init__(
        self,
        *,
        status: ResponseStatus,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        self.code = status.code
        super().__init__(msg=status.msg, data=data, background=background)


class RequestError(ExceptionBase):
    """请求异常：400."""

    def __init__(
        self,
        *,
        code: int = status.HTTP_400_BAD_REQUEST,
        msg: str = ResponseCode.HTTP_400.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        self.code = code
        super().__init__(msg=msg, data=data, background=background)


class TokenError(HTTPError):
    """Token 认证异常."""

    code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, *, msg: str = ResponseCode.HTTP_401.msg, headers: dict[str, Any] | None = None):
        super().__init__(code=self.code, msg=msg, headers=headers or {'WWW-Authenticate': 'Bearer'})


class AuthorizationError(ExceptionBase):
    """授权异常：403.

    已经授权了，但是访问了不该访问的东西，返回禁止访问。
    """

    code = status.HTTP_403_FORBIDDEN

    def __init__(
        self,
        *,
        msg: str | None = ResponseCode.HTTP_403.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class ForbiddenError(ExceptionBase):
    """禁止访问：403."""

    code = status.HTTP_403_FORBIDDEN

    def __init__(
        self,
        *,
        msg: str | None = ResponseCode.HTTP_403.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class NotFoundError(ExceptionBase):
    """资源不存在：404."""

    code = status.HTTP_404_NOT_FOUND

    def __init__(
        self,
        *,
        msg: str = ResponseCode.HTTP_404.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class ConflictError(ExceptionBase):
    """资源冲突：409."""

    code = status.HTTP_409_CONFLICT

    def __init__(
        self,
        *,
        msg: str | None = ResponseCode.HTTP_409.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class ServerError(ExceptionBase):
    """服务器内部异常：500."""

    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *,
        msg: str | None = ResponseCode.HTTP_500.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)


class GatewayError(ExceptionBase):
    """网关异常：502."""

    code = status.HTTP_502_BAD_GATEWAY

    def __init__(
        self,
        *,
        msg: str | None = ResponseCode.HTTP_502.msg,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        super().__init__(msg=msg, data=data, background=background)

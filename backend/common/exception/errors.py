#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局业务内部异常类

业务代码执行异常时, 可以使用 raise xxxError 触发内部错误, 它尽可能实现带有后台任务的异常, 不适用于 自定义响应状态码
如果要求使用 自定义响应状态码 , 使用 return response_base.fail(res=CustomResponseCode.xxx) 直接返回
"""

from typing import Any

from fastapi import HTTPException
from starlette.background import BackgroundTask

from backend.common.response.code import (  # 支持在异常处理时执行异步任务
    CustomErrorCode,
    CustomResponseCode,
    StandardResponseCode,
)


class BaseExceptionMixin(Exception):
    """基础异常类, 供其他异常类使用"""

    code: int

    def __init__(self, *, msg: str | None = None, data: Any = None, background: BackgroundTask | None = None):
        self.msg = msg
        self.data = data
        self.background = background


class HTTPError(HTTPException):
    """自定义 HTTP 异常"""

    def __init__(
        self,
        *,
        code: int,
        msg: Any = None,
        headers: dict[str, Any] | None = None,
    ):
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseExceptionMixin):
    """自定义业务异常

    当下面的异常类不满足需求时, 可以使用该异常类自定义状态码和信息。
    """

    def __init__(
        self,
        *,
        error: CustomErrorCode | CustomResponseCode,
        data: Any = None,
        background: BackgroundTask | None = None,
    ):
        self.code = error.code  # 错误码
        super().__init__(msg=error.msg, data=data, background=background)


class RequestError(BaseExceptionMixin):
    """请求错误异常：400（Bad Request）"""

    code = StandardResponseCode.HTTP_400

    def __init__(
        self, *, msg: str = CustomResponseCode.HTTP_400.msg, data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class ForbiddenError(BaseExceptionMixin):
    """禁止访问异常：403（Forbidden）"""

    code = StandardResponseCode.HTTP_403

    def __init__(
        self, *, msg: str = CustomResponseCode.HTTP_403.msg, data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class NotFoundError(BaseExceptionMixin):
    """资源未找到异常：404（Not Found）"""

    code = StandardResponseCode.HTTP_404

    def __init__(
        self, *, msg: str = CustomResponseCode.HTTP_404.msg, data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class ValidationError(BaseExceptionMixin):
    """校验字段异常：422（Unprocessable Entity）"""

    code = StandardResponseCode.HTTP_422

    def __init__(
        self, *, msg: str = CustomResponseCode.HTTP_422.msg, data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class ServerError(BaseExceptionMixin):
    """服务器内部错误异常：500（Internal Server Error）"""

    code = StandardResponseCode.HTTP_500

    def __init__(
        self, *, msg: str = CustomResponseCode.HTTP_500.msg, data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class GatewayError(BaseExceptionMixin):
    """网关错误异常：502（Bad Gateway）"""

    code = StandardResponseCode.HTTP_502

    def __init__(
        self, *, msg: str = CustomResponseCode.HTTP_502.msg, data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class PermissionDeniedError(BaseExceptionMixin):
    """授权失败异常：401（Permission Denied）

    有 Token 但权限不足
    """

    code = StandardResponseCode.HTTP_401

    def __init__(
        self, *, msg: str = CustomResponseCode.HTTP_401.msg, data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class TokenError(HTTPError):
    """Token 无效异常：401（Unauthorized）"""

    code = StandardResponseCode.HTTP_401

    def __init__(self, *, msg: str = '身份验证失败', headers: dict[str, Any] | None = None):
        super().__init__(code=self.code, msg=msg, headers=headers or {'WWW-Authenticate': 'Bearer'})

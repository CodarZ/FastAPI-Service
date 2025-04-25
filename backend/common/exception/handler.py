#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import PydanticUserError, ValidationError
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from backend.common.exception.errors import BaseExceptionMixin
from backend.common.exception.message import USAGE_ERROR_MESSAGES, VALIDATION_ERROR_MESSAGES
from backend.common.request.trace_id import get_request_trace_id
from backend.common.response.base import response_base
from backend.common.response.code import CustomResponseCode, StandardResponseCode
from backend.core.config import settings
from backend.utils.serializers import MsgSpecJSONResponse


def register_exception(app: FastAPI):
    """注册异常处理器"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """全局 HTTP 异常处理器"""

        content = (
            {
                'code': exc.status_code,
                'msg': exc.detail,
                'data': None,
            }
            if settings.ENVIRONMENT == 'development'
            else response_base.fail(res=CustomResponseCode.HTTP_400).model_dump()
        )

        request.state.__request_http_exception__ = content  # 自定义字段，存储异常信息，用于在中间件中获取异常
        return MsgSpecJSONResponse(
            status_code=_get_validate_status_code(exc.status_code),
            content=content,
            headers=exc.headers,  # 确保 FastAPI 中 HTTP 自定义的异常响应头能正确透传
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        """请求参数校验

        如：Query、Path、Body 等参数校验异常处理器
        """
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: ValidationError,
    ):
        """数据模型校验

        如：Pydantic 模型 用 `.parse_obj()`、 `.validate()` 等方法时会抛出异常
        """
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(PydanticUserError)
    async def pydantic_user_error_handler(request: Request, exc: PydanticUserError):
        """Pydantic 使用方式异常处理器"""
        content = (
            {
                'code': StandardResponseCode.HTTP_500,
                'msg': (USAGE_ERROR_MESSAGES.get(exc.code) if exc.code else 'Pydantic 使用异常'),
                'data': None,
            }
            if settings.ENVIRONMENT == 'development'
            else response_base.fail(res=CustomResponseCode.HTTP_500).model_dump()
        )
        request.state.__request_pydantic_user_error__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(
            status_code=StandardResponseCode.HTTP_500,
            content=content,
        )

    @app.exception_handler(AssertionError)
    async def assertion_exception_handler(
        request: Request,
        exc: AssertionError,
    ):
        """断言异常处理器"""
        content = (
            {
                'code': StandardResponseCode.HTTP_500,
                'msg': str(''.join(exc.args) if exc.args else exc.__doc__),
                'data': None,
            }
            if settings.ENVIRONMENT == 'development'
            else response_base.fail(res=CustomResponseCode.HTTP_500).model_dump()
        )

        request.state.__request_http_exception__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(
            status_code=_get_validate_status_code(StandardResponseCode.HTTP_500),
            content=content,
        )

    @app.exception_handler(BaseExceptionMixin)
    async def base_exception_handler(
        request: Request,
        exc: BaseExceptionMixin,
    ):
        """自定义异常处理器"""
        content = {
            'code': exc.code,
            'msg': str(exc.msg),
            'data': exc.data if exc.data else None,
        }

        request.state.__request_http_exception__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(
            status_code=_get_validate_status_code(exc.code),
            content=content,
            background=exc.background,
        )

    @app.exception_handler(Exception)
    async def exception_handler(
        request: Request,
        exc: Exception,
    ):
        """全局异常处理器"""
        content = (
            {
                'code': StandardResponseCode.HTTP_500,
                'msg': str(exc),
                'data': None,
            }
            if settings.ENVIRONMENT == 'development'
            else response_base.fail(res=CustomResponseCode.HTTP_500).model_dump()
        )

        request.state.__request_http_exception__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(
            status_code=_get_validate_status_code(StandardResponseCode.HTTP_500),
            content=content,
        )

    if settings.MIDDLEWARE_CORS:

        @app.exception_handler(StandardResponseCode.HTTP_500)
        def cors_code_500_exception_handler(
            request: Request,
            exc,
        ):
            """CORS 异常处理器


            `Related issue <https://github.com/encode/starlette/issues/1175>`_

            `Solution <https://github.com/fastapi/fastapi/discussions/7847#discussioncomment-5144709>`_

            """
            if isinstance(exc, BaseExceptionMixin):
                content = {
                    'code': exc.code,
                    'msg': str(exc.msg),
                    'data': exc.data if exc.data else None,
                }
            else:
                content = (
                    {
                        'code': StandardResponseCode.HTTP_500,
                        'msg': str(exc),
                        'data': None,
                    }
                    if settings.ENVIRONMENT == 'development'
                    else response_base.fail(res=CustomResponseCode.HTTP_500).model_dump()
                )
            request.state.__request_http_exception__ = content
            request.state.__request_cors_500_exception__ = content
            content.update(trace_id=get_request_trace_id(request))

            response = MsgSpecJSONResponse(
                status_code=content.get('code', StandardResponseCode.HTTP_500),
                content=content,
                background=exc.background if isinstance(exc, BaseExceptionMixin) else None,
            )
            origin = request.headers.get('origin')
            if origin:
                cors = CORSMiddleware(
                    app=app,
                    allow_origins=settings.CORS_ALLOWED_ORIGINS,
                    allow_credentials=True,
                    allow_methods=['*'],
                    allow_headers=['*'],
                    expose_headers=settings.CORS_EXPOSE_HEADERS,
                )
                response.headers.update(cors.simple_headers)
                if cors.allow_all_origins and 'cookie' in request.headers:
                    response.headers['Access-Control-Allow-Origin'] = origin
                elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers.add_vary_header('Origin')

            return response


def _get_validate_status_code(status_code: int):
    """获取返回状态码（可用状态码基于 RFC 定义）

    `python 状态码标准支持 <https://github.com/python/cpython/blob/6e3cc72afeaee2532b4327776501eb8234ac787b/Lib/http/__init__.py#L7>`__

    `IANA 状态码注册表 <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>`__
    """
    try:
        STATUS_PHRASES[status_code]  # 校验是否是合法的状态码
    except Exception:
        code = CustomResponseCode.HTTP_400.code
    else:
        code = status_code
    return code


async def _validation_exception_handler(
    request: Request,
    exc: RequestValidationError | ValidationError,
):
    """数据字段验证异常处理"""
    errors = []
    for error in exc.errors():
        # 提取错误类型, 根据配置文件获取定制的错误消息
        custom_message = VALIDATION_ERROR_MESSAGES.get(error['type'])
        if custom_message:
            ctx = error.get('ctx')
            if not ctx:
                error['msg'] = custom_message
            else:
                error['msg'] = custom_message.format(**ctx)
                ctx_error = ctx.get('error')
                if ctx_error:
                    ctx['error'] = ctx_error.__str__().replace("'", '"') if isinstance(ctx_error, Exception) else None
        errors.append(error)

    error = errors[0]
    if error.get('type') == 'json_invalid':
        message = 'json解析失败'
    else:
        error_msg = error.get('msg')
        error_input = error.get('input')
        field = str(error.get('loc')[-1])
        message = f'{field} {error_msg}，输入：{error_input}'

    content = {
        'code': CustomResponseCode.HTTP_422.code,
        'msg': f'{CustomResponseCode.HTTP_422.msg}: {message}',
        'data': {'errors': errors} if settings.ENVIRONMENT == 'development' else None,
    }

    request.state.__request_validation_exception__ = content  # 自定义字段，存储异常信息，用于在中间件中获取异常

    content.update(trace_id=get_request_trace_id(request))
    return MsgSpecJSONResponse(status_code=CustomResponseCode.HTTP_422.code, content=content)

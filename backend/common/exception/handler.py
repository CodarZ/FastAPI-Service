from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import PydanticUserError, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from backend.common.exception.errors import BaseExceptionMixin
from backend.common.exception.message import USAGE_ERROR_MESSAGES, VALIDATION_ERROR_MESSAGES
from backend.common.request.trace_id import get_request_trace_id
from backend.common.response.base import response_base
from backend.common.response.code import CustomResponseCode, StandardResponseCode
from backend.core.config import settings
from backend.utils.serializers import MsgSpecJSONResponse


def _get_exception_code(status_code: int):
    """获取返回状态码

    `python 状态码标准支持 <https://github.com/python/cpython/blob/6e3cc72afeaee2532b4327776501eb8234ac787b/Lib/http/__init__.py#L7>`__

    `IANA 状态码注册表 <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>`__
    """
    try:
        STATUS_PHRASES[status_code]
        return status_code
    except Exception:
        return StandardResponseCode.HTTP_400


async def _validation_exception_handler(request: Request, e: RequestValidationError | ValidationError):
    """数据验证异常处理，返回统一的响应结构。"""

    errors = []
    for error in e.errors():
        message = VALIDATION_ERROR_MESSAGES.get(error['type'])
        if message:
            ctx = error.get('ctx')
            if not ctx:
                error['msg'] = message
            else:
                error['msg'] = message.format(**ctx)
                ctx_error = ctx.get('error')
                if ctx_error:
                    error['ctx']['error'] = (  # type: ignore
                        ctx_error.__str__().replace("'", '"') if isinstance(ctx_error, Exception) else None
                    )
        errors.append(error)

    error = errors[0]  # 只返回第一个错误信息

    if error.get('type') == 'json_invalid':
        message = 'json 解析失败'
    else:
        error_input = error.get('input')
        field = str(error.get('loc')[-1])
        error_msg = error.get('msg')
        message = f'{field} {error_msg}，输入：{error_input}' if settings.ENVIRONMENT == 'dev' else error_msg
    # msg = f'请求参数非法: {message}'

    data = {'errors': errors} if settings.ENVIRONMENT == 'dev' else None
    content = {
        'code': StandardResponseCode.HTTP_422,
        'msg': message,
        'data': data,
    }
    request.state.__request_validation_exception__ = content  # 用于在中间件中获取异常信息
    content.update(trace_id=get_request_trace_id(request))
    return MsgSpecJSONResponse(content, StandardResponseCode.HTTP_500)


def register_exception(app: FastAPI):
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """SQLAlchemy 数据库异常处理"""
        if settings.ENVIRONMENT == 'development':
            # 开发环境显示详细错误信息
            content = {
                'code': StandardResponseCode.HTTP_500,
                'msg': f'数据库错误: {str(exc)}',
                'data': None,
            }
        else:
            # 生产环境隐藏详细错误信息
            res = response_base.fail(res=CustomResponseCode.HTTP_500)
            content = res.model_dump()
        request.state.__request_sqlalchemy_exception__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(content, StandardResponseCode.HTTP_500)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """全局HTTP异常处理"""
        if settings.ENVIRONMENT == 'development':
            content = {
                'code': exc.status_code,
                'msg': exc.detail,
                'data': None,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_400)
            content = res.model_dump()
        request.state.__request_http_exception__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(
            status_code=_get_exception_code(exc.status_code),
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """Fastapi 数据验证异常处理"""
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """pydantic 数据验证异常处理"""
        return await _validation_exception_handler(request, exc)

    @app.exception_handler(PydanticUserError)
    async def pydantic_user_error_handler(request: Request, exc: PydanticUserError):
        """Pydantic 用户异常处理"""
        content = {
            'code': StandardResponseCode.HTTP_500,
            'msg': (USAGE_ERROR_MESSAGES.get(exc.code) if exc.code else '用户处理异常'),
            'data': None,
        }
        request.state.__request_pydantic_user_error__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(content, StandardResponseCode.HTTP_500)

    @app.exception_handler(AssertionError)
    async def assertion_error_handler(request: Request, exc: AssertionError):
        """断言错误处理"""
        if settings.ENVIRONMENT == 'development':
            content = {
                'code': StandardResponseCode.HTTP_500,
                'msg': str(''.join(exc.args) if exc.args else exc.__doc__),
                'data': None,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_500)
            content = res.model_dump()
        request.state.__request_assertion_error__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(content, StandardResponseCode.HTTP_500)

    @app.exception_handler(BaseExceptionMixin)
    async def custom_exception_handler(request: Request, exc: BaseExceptionMixin):
        """全局自定义异常处理"""
        content = {
            'code': exc.code,
            'msg': str(exc.msg),
            'data': exc.data if exc.data else None,
        }
        request.state.__request_custom_exception__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(content, StandardResponseCode.HTTP_500, background=exc.background)

    @app.exception_handler(Exception)
    async def all_unknown_exception_handler(request: Request, exc: Exception):
        """全局未知异常处理"""
        if settings.ENVIRONMENT == 'development':
            content = {
                'code': StandardResponseCode.HTTP_500,
                'msg': str(exc),
                'data': None,
            }
        else:
            res = response_base.fail(res=CustomResponseCode.HTTP_500)
            content = res.model_dump()
        request.state.__request_all_unknown_exception__ = content
        content.update(trace_id=get_request_trace_id(request))
        return MsgSpecJSONResponse(content, StandardResponseCode.HTTP_500)

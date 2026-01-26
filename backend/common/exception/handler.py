from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import PydanticUserError, ValidationError
from uvicorn.protocols.http.h11_impl import STATUS_PHRASES

from backend.common.exception.errors import ExceptionBase
from backend.common.exception.message import USAGE_ERROR_MESSAGES, VALIDATION_ERROR_MESSAGES
from backend.common.request.context import ctx
from backend.common.request.trace_id import get_request_trace_id
from backend.common.response.base import response_base
from backend.common.response.code import StandardResponseStatus
from backend.core.config import settings
from backend.utils.serializers import MsgSpecJSONResponse


def register_exception(app: FastAPI):
    """异常处理器注册
    =============================
    重要：异常处理器按 **最后注册的优先** 进行匹配

    优化后的顺序（从一般到特殊）：
    1. Exception - 全局兜底异常
    2. ExceptionBase - 自定义异常基类
    3. AssertionError - 断言异常
    4. PydanticUserError - Pydantic 用户错误
    5. ValidationError - Pydantic 数据验证异常
    6. RequestValidationError - FastAPI 请求验证异常
    7. HTTPException - HTTP 异常
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """全局 HTTP 异常"""

        content = _extract_content(exc, StandardResponseStatus.HTTP_400)
        return MsgSpecJSONResponse(content, _get_exception_code(exc.status_code), exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """FastAPI 请求验证异常"""

        return await _validation_exception_handler(exc)

    @app.exception_handler(PydanticUserError)
    async def pydantic_user_error_handler(request: Request, exc: PydanticUserError):
        """Pydantic 用户异常处理
        - 模型定义错误
        - 字段缺少类型注解
        - 装饰器用法错误
        - 验证器签名错误
        """

        content = _extract_content(exc, StandardResponseStatus.HTTP_500)
        return MsgSpecJSONResponse(content, StandardResponseStatus.HTTP_500.code)

    @app.exception_handler(AssertionError)
    async def assert_exception_handler(request: Request, exc: AssertionError):
        """断言异常"""

        content = _extract_content(exc, StandardResponseStatus.HTTP_500)
        return MsgSpecJSONResponse(content, StandardResponseStatus.HTTP_500.code)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Pydantic 数据验证异常"""

        return await _validation_exception_handler(exc)

    @app.exception_handler(ExceptionBase)
    async def custom_exception_handler(request: Request, exc: ExceptionBase):
        """继承 ExceptionBase 的自定义异常
        - RequestError
        - AuthorizationError
        - NotFoundError
        - ConflictError
        - ... ...
        """

        content = _extract_content(exc, StandardResponseStatus.HTTP_500)
        return MsgSpecJSONResponse(content, exc.code, background=exc.background)

    @app.exception_handler(Exception)
    async def unknown_exception_handler(request: Request, exc: Exception):
        """全局其他未知异常"""

        content = _extract_content(exc, StandardResponseStatus.HTTP_500)
        return MsgSpecJSONResponse(content, StandardResponseStatus.HTTP_500.code)


def _get_exception_code(status_code: int):
    """获取返回状态码.

    `python 状态码标准支持 <https://github.com/python/cpython/blob/6e3cc72afeaee2532b4327776501eb8234ac787b/Lib/http
    /__init__.py#L7>`__

    `IANA 状态码注册表 <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>`__
    """
    try:
        STATUS_PHRASES[status_code]
        return status_code
    except Exception:
        return status.HTTP_400_BAD_REQUEST


def _extract_content(exc: Exception, status: StandardResponseStatus):
    """提取异常消息内容
    - 开发环境: 详细信息
    - 生产环境: 通用信息

    异常检查顺序与 register_exception 一致
    """

    ctx_name = '__request_unknown_exception__'
    code = status.code

    # ExceptionBase - 自定义异常（不区分环境，始终返回完整信息）
    if isinstance(exc, ExceptionBase):
        content = {'code': exc.code, 'msg': exc.msg, 'data': exc.data}
        ctx_name = '__request_custom_exception__'
    # 开发环境 - 返回详细错误信息
    elif settings.ENVIRONMENT == 'development':
        if isinstance(exc, HTTPException):
            code = exc.status_code
            msg = exc.detail
            ctx_name = '__request_http_exception__'
        elif isinstance(exc, PydanticUserError):
            msg = USAGE_ERROR_MESSAGES.get(exc.code) if exc.code else exc.message or 'Pydantic User Error'
            ctx_name = '__request_pydantic_user_error__'
        elif isinstance(exc, AssertionError):
            msg = str(' | ').join(map(str, exc.args)) or exc.__doc__ or status.msg
            ctx_name = '__request_assertion_error__'
        else:
            msg = str(exc)

        content = {'code': code, 'msg': msg, 'data': None}
    # 生产环境 - 返回通用错误信息（隐藏细节）
    else:
        res = response_base.fail(res=status)
        content = res.model_dump()

    content.update(error_type=type(exc).__name__)
    content.update(trace_id=get_request_trace_id())
    ctx.__setattr__(ctx_name, content)

    return content


async def _validation_exception_handler(exc: RequestValidationError | ValidationError):
    """数据验证异常处理器"""

    errors = []
    for error in exc.errors():
        message = VALIDATION_ERROR_MESSAGES.get(error['type'])
        if message:
            ctx_error = error.get('ctx')

            if not ctx_error:
                # message 应该去掉无法赋值的占位符（如有）
                error['msg'] = message
            else:
                try:
                    error['msg'] = message.format(**ctx_error)
                except Exception:
                    error['msg'] = error.get('msg', message)
        errors.append(error)

    error = errors[0]
    message = error.get('msg')
    if error.get('type') != 'json_invalid':
        err_input = error.get('input')
        field = str(error.get('loc')[-1])
        message = f'{field} {message}, 输入的是：{err_input}' if settings.ENVIRONMENT == 'development' else message

    content = {
        'code': StandardResponseStatus.HTTP_422.code,
        'msg': message,
        'data': None,
    }
    content.update(error_type=type(exc).__name__)
    content.update(trace_id=get_request_trace_id())
    ctx.__setattr__('__request_validation_exception__', content)

    return MsgSpecJSONResponse(content, StandardResponseStatus.HTTP_422.code)

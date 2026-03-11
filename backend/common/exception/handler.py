from http import HTTPStatus
from typing import TYPE_CHECKING

from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from pydantic import ValidationError
from pydantic_core import to_json
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.common.exception.error import ExceptionBase
from backend.common.request import ctx, get_request_trace_id
from backend.common.response import ResponseCode
from backend.core.config import settings

if TYPE_CHECKING:
    from fastapi import FastAPI, Request

# 缓存所有合法的 HTTP 状态码
_VALID_HTTP_CODES = {status.value for status in HTTPStatus}


def _get_status_code(status_code: int) -> int:
    """获取返回状态码（可用状态码基于 RFC 定义）.

    `python 状态码标准支持 <https://docs.python.org/3/library/http.html#http.HTTPStatus>`__

    `IANA 状态码注册表 <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml>`__
    """
    if status_code in _VALID_HTTP_CODES:
        return status_code
    return ResponseCode.HTTP_400.code


def _apply_cors_headers(request: Request, response: Response) -> Response:
    """为 Exception 兜底异常响应手动附加跨域头.

    **仅用于** `all_unknown_exception_handler`。

    Starlette 的 `build_middleware_stack` 将 `Exception` / `500` 处理器注册到最外层的
    `ServerErrorMiddleware.handler`；其产生的响应在 `ServerErrorMiddleware` 层即被返回，
    **不会** 流经内层的 `CORSMiddleware`，因此必须在此处手动附加跨域头。

    其余 5 个异常处理器均注册在 `ExceptionMiddleware`，跨域头由中间件自动附加，**无需调用本函数**。

    `Starlette build_middleware_stack 源码参考`
    `<https://github.com/encode/starlette/blob/master/starlette/applications.py>`__
    """
    if not settings.MIDDLEWARE_CORS:
        return response

    origin = request.headers.get('origin')
    if not origin:
        return response

    allow_all = '*' in settings.CORS_ALLOWED_ORIGINS
    has_cookie = 'cookie' in request.headers

    if allow_all:
        # 携带 Cookie 时不能使用通配符，需返回具体 origin 并声明 credentials
        response.headers['Access-Control-Allow-Origin'] = origin if has_cookie else '*'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    elif origin in settings.CORS_ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        # 告知缓存：响应因 Origin 不同而不同
        response.headers.add_vary_header('Origin')

    return response


def _validation_exception_handler(exc: RequestValidationError | ValidationError) -> Response:
    """数据验证异常处理."""
    errors = exc.errors()
    error = errors[0]

    if error.get('type') == 'json_invalid':
        msg = 'JSON 数据解析异常'
    else:
        input = error['input']
        message = error['msg']
        loc = error.get('loc')
        field = str(loc[-1]) if loc else ''

        msg = f'请求参数异常: {field} {message}，输入：{input}' if settings.ENVIRONMENT == 'development' else message

    res_code = ResponseCode.HTTP_422
    content = {
        'code': res_code.code,
        'msg': msg,
        'data': {'errors': errors} if settings.ENVIRONMENT == 'development' else None,
    }

    ctx['__request_validation_exception__'] = content
    content.update(trace_id=get_request_trace_id())

    return Response(
        content=to_json(content),
        status_code=res_code.code,
        media_type='application/json',
    )


def register_exception(app: FastAPI):
    """注册异常处理器.

    1. HTTPException - HTTP 异常
    2. RequestValidationError - FastAPI 请求验证异常
    3. ValidationError - Pydantic 数据验证异常
    4. AssertionError - 断言异常
    5. ExceptionBase - 自定义异常（业务）
    6. Exception - 未知异常兜底
    """

    @app.exception_handler(StarletteHTTPException)
    def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """HTTP 异常处理."""
        if settings.ENVIRONMENT == 'development':
            code = exc.status_code
            msg = getattr(exc, 'detail', str(exc))
        else:
            # 生产环境隐藏具体错误详情，并匹配标准状态码对应的消息
            res = getattr(ResponseCode, f'HTTP_{exc.status_code}', ResponseCode.HTTP_400)
            code = res.code
            msg = res.msg

        content = {
            'code': code,
            'msg': msg,
            'data': None,
        }

        ctx['__request_http_exception__'] = content
        content.update(trace_id=get_request_trace_id())

        return Response(
            content=to_json(content),
            status_code=exc.status_code,
            headers=exc.headers,
            media_type='application/json',
        )

    @app.exception_handler(RequestValidationError)
    def fastapi_validation_exception_handler(request: Request, exc: RequestValidationError):
        """FastAPI 数据验证异常处理."""
        return _validation_exception_handler(exc)

    @app.exception_handler(ValidationError)
    def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Pydantic 数据验证异常处理."""
        return _validation_exception_handler(exc)

    @app.exception_handler(AssertionError)
    def assertion_error_handler(request: Request, exc: AssertionError):
        """断言错误处理."""
        if settings.ENVIRONMENT == 'development':
            msg = str(''.join(exc.args) if exc.args else exc.__doc__)
        else:
            msg = ResponseCode.HTTP_500.msg

        content = {
            'code': ResponseCode.HTTP_500.code,
            'msg': msg,
            'data': None,
        }

        ctx['__request_assertion_error__'] = content
        content.update(trace_id=get_request_trace_id())

        return Response(
            content=to_json(content),
            status_code=ResponseCode.HTTP_500.code,
            media_type='application/json',
        )

    @app.exception_handler(ExceptionBase)
    def custom_exception_handler(request: Request, exc: ExceptionBase):
        """自定义异常处理."""
        content = {
            'code': exc.code,
            'msg': str(exc.msg),
            'data': exc.data,
        }

        ctx['__request_custom_exception__'] = content
        content.update(trace_id=get_request_trace_id())

        return Response(
            content=to_json(content),
            status_code=_get_status_code(exc.code),
            background=exc.background,
            media_type='application/json',
        )

    @app.exception_handler(Exception)
    def all_unknown_exception_handler(request: Request, exc: Exception):
        """未知异常处理."""
        msg = str(exc) if settings.ENVIRONMENT == 'development' else ResponseCode.HTTP_500.msg

        content = {
            'code': ResponseCode.HTTP_500.code,
            'msg': msg,
            'data': None,
        }

        ctx['__request_unknown_exception__'] = content
        content.update(trace_id=get_request_trace_id())

        response = Response(
            content=to_json(content),
            status_code=ResponseCode.HTTP_500.code,
            media_type='application/json',
        )
        return _apply_cors_headers(request, response)

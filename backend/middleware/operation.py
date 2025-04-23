#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

from asgiref.sync import sync_to_async
from fastapi import Request, Response
from starlette.datastructures import UploadFile
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.admin.schema.operation_log import OperationLogCreate
from backend.common.dataclasses import RequestCallNext
from backend.common.enum.custom import OperationLogCipherEnum, StatusEnum
from backend.common.logger import log
from backend.common.request.trace_id import get_request_trace_id
from backend.core.config import settings
from backend.utils.encrypt import AESCipher, ItsmCipher, MD5Cipher
from backend.utils.timezone import timezone


class OperationLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件"""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        path = request.url.path
        if path in settings.OPERATION_LOG_PATH_EXCLUDE or not path.startswith(settings.API_ROUTE_PREFIX):
            return await call_next(request)

        username = (
            request.user.username
            if hasattr(
                request.user,
                'username',
            )
            else 'Unknown Username'
        )
        method = request.method
        args = await self.get_request_args(request)
        args = await self.desensitization(args)

        # 执行请求
        start_time = timezone.now()
        request_next = await self.execute_request(request, call_next)
        end_time = timezone.now()
        cost_time = round((end_time - start_time).total_seconds() * 1000.0, 3)

        _route = request.scope.get('route')
        summary = getattr(_route, 'summary', None) or ''

        opera_create = OperationLogCreate(
            trace_id=get_request_trace_id(request),
            username=username,
            method=method,
            title=summary,
            path=path,
            ip=request.state.ip,
            country=request.state.country,
            region=request.state.region,
            city=request.state.city,
            user_agent=request.state.user_agent,
            os=request.state.os,
            browser=request.state.browser,
            device=request.state.device,
            args=args,
            status=request_next.status,
            code=request_next.code,
            msg=request_next.msg,
            cost_time=cost_time,
            operate_time=start_time,
        )

        # TODO 存入数据库
        print(opera_create.model_dump_json())

        if request_next.err:
            log.error(f'操作日志中间件, 执行请求异常: {request_next.err}')
            raise request_next.err from None
        return request_next.response

    @staticmethod
    async def get_request_args(request: Request) -> dict[str, Any]:
        """获取请求参数"""
        args = dict(request.query_params)
        args.update(request.path_params)

        # Tip: .body() 必须在 .form() 之前获取
        # https://github.com/encode/starlette/discussions/1933
        body_data = await request.body()
        form_data = await request.form()

        if len(form_data) > 0:
            form_dict = {}
            for k, v in form_data.items():
                if isinstance(v, UploadFile):
                    form_dict[k] = v.filename
                else:
                    form_dict[k] = v
            args.update(form_dict)
        elif body_data:
            content_type = request.headers.get('Content-Type', '').split(';')
            if 'application/json' in content_type:
                json_data = await request.json()
                if isinstance(json_data, dict):
                    args.update(json_data)
                else:
                    args.update({'body': str(body_data)})  # 注意：非字典数据默认使用 body 作为键
            else:
                args.update({'body': str(body_data)})
        return args

    @staticmethod
    @sync_to_async
    def desensitization(args: dict[str, Any]) -> dict[str, Any] | None:
        """脱敏处理"""
        if not args:
            return None
        type = settings.OPERATION_LOG_ENCRYPT_TYPE
        secret = settings.OPERATION_LOG_ENCRYPT_SECRET_KEY.get_secret_value()
        keys = settings.OPERATION_LOG_ENCRYPT_KEY_INCLUDE

        for key, value in args.items():
            if key in keys:
                match type:
                    case OperationLogCipherEnum.aes:
                        args[key] = (AESCipher(secret).encrypt(value)).hex()
                    case OperationLogCipherEnum.md5:
                        args[key] = MD5Cipher.encrypt(value)
                    case OperationLogCipherEnum.itsdangerous:
                        args[key] = ItsmCipher(secret).encrypt(value)
                    case OperationLogCipherEnum.plan:
                        pass
                    case _:
                        args[key] = '******'
        return args

    async def execute_request(self, request: Request, call_next: Any) -> RequestCallNext:
        """执行请求, 并处理异常"""
        code = 200
        msg = 'Success'
        status = StatusEnum.YES
        err = None
        response = None

        try:
            response = await call_next(request)
            code, msg = self.request_exception_handler(request, code, msg)
        except Exception as e:
            log.error(f'请求异常: {str(e)}')
            code = getattr(e, 'code', code)
            msg = getattr(e, 'msg', msg)
            status = StatusEnum.NO
            err = e
        return RequestCallNext(code=str(code), msg=msg, status=status, err=err, response=response)  # type: ignore[return-value]

    @staticmethod
    def request_exception_handler(request: Request, code: int, msg: str) -> tuple[int, str]:
        """请求异常处理"""
        exception_states = [
            '__request_http_exception__',
            '__request_validation_exception__',
            '__request_assertion_error__',
            '__request_custom_exception__',
            '__request_all_unknown_exception__',
            '__request_cors_500_exception__',
        ]
        for state in exception_states:
            exception = getattr(request.state, state, None)
            if exception:
                code = exception.get('code')
                msg = exception.get('msg')
                log.error(f'操作日志中间件, 处理请求异常: {msg}')
                break
        return code, msg

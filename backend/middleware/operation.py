#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from asyncio import Queue
from typing import Any, Awaitable, Callable

from asgiref.sync import sync_to_async
from fastapi import Request, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.app.admin.schema.operation_log import OperationLogCreateParams
from backend.app.admin.service.operation_log import operation_log_service
from backend.common.enum.custom import OperationLogCipherEnum, StatusEnum
from backend.common.log import log
from backend.common.queue import batch_dequeue
from backend.common.request.trace_id import get_request_trace_id
from backend.common.response.code import CustomResponseCode, StandardResponseCode
from backend.core.config import settings
from backend.utils.encrypt import AESCipher, ItsDCipher, MD5Cipher
from backend.utils.serializers import MsgSpecJSONResponse


class OperationLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件"""

    log_queue = Queue(maxsize=100000)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        path = request.url.path
        trace_id = get_request_trace_id(request)

        # if path in settings.OPERATION_LOG_PATH_EXCLUDE or not path.startswith(f'{settings.FASTAPI_API_ROUTE_PREFIX}'):
        if path in settings.OPERATION_LOG_PATH_EXCLUDE:
            response = await call_next(request)
            return response

        # 处理需要记录操作日志的请求
        method = request.method
        args = await self.get_request_args(request)

        code = CustomResponseCode.HTTP_200.code
        msg = CustomResponseCode.HTTP_200.msg
        status = StatusEnum.ENABLE
        error = None

        try:
            response = await call_next(request)
            elapsed = (time.perf_counter() - request.state.perf_time) * 1000

            for state in [
                # '__request_sqlalchemy_exception__',
                '__request_http_exception__',
                '__request_validation_exception__',
                # '__request_pydantic_user_error__',
                '__request_assertion_error__',
                '__request_custom_exception__',
                # '__request_all_unknown_exception__',
            ]:
                exception = getattr(request.state, state, None)
                if exception:
                    code = exception.get('code')
                    msg = exception.get('msg')
                    log.error(f'{path} | {msg}')
                    break

        except Exception as e:
            elapsed = (time.perf_counter() - request.state.perf_time) * 1000
            code = getattr(e, 'code', StandardResponseCode.HTTP_500)
            msg = getattr(e, 'msg', str(e))  # 不建议使用 traceback 模块获取错误信息，会暴漏代码信息
            status = StatusEnum.DISABLE
            error = e
            log.error(f'{path} | {msg}')

            # 在异常情况下，我们需要创建一个错误响应
            response = MsgSpecJSONResponse({'code': code, 'msg': msg, 'data': None}, StandardResponseCode.HTTP_500)

        # 此信息只能在请求后获取
        _route = request.scope.get('route')
        summary = getattr(_route, 'summary', '') if _route else ''

        # 日志记录
        log.debug(f'接口摘要：[{summary}]')
        log.debug(f'请求参数：{args}')

        # 创建日志
        operation_log = OperationLogCreateParams(
            trace_id=trace_id,
            username='暂无',
            method=method,
            moudle=summary,
            path=path,
            ip='暂无',
            country='暂无',
            region='暂无',
            city='暂无',
            user_agent=request.state.user_agent,
            os=request.state.os,
            browser=request.state.browser,
            device=request.state.device,
            args=args,
            status=status,
            code=str(code),
            msg=msg,
            cost_time=elapsed,  # 可能和日志存在微小差异（可忽略）
            operated_time=request.state.start_time,
        )

        await self.log_queue.put(operation_log)

        # 重新抛出错误记录
        if error:
            raise error from None

        return response

    async def get_request_args(self, request: Request):
        """获取请求参数"""
        args = {}

        # 查询参数
        query_params = dict(request.query_params)
        if query_params:
            args['query_params'] = await self.desensitization(query_params)

        # 路径参数
        path_params = request.path_params
        if path_params:
            args['path_params'] = await self.desensitization(path_params)

        # Tip: .body() 必须在 .form() 之前获取
        # https://github.com/encode/starlette/discussions/1933
        content_type = request.headers.get('Content-Type', '').split(';')

        # 请求体
        body_data = await request.body()
        if body_data:
            # 注意：非 json 数据默认使用 data 作为键
            if 'application/json' not in content_type:
                args['data'] = str(body_data)
            else:
                json_data = await request.json()
                if isinstance(json_data, dict):
                    args['json'] = await self.desensitization(json_data)
                else:
                    args['data'] = str(body_data)

        # 表单参数
        form_data = await request.form()
        if len(form_data) > 0:
            # 将 FormData 转换为普通字典
            form_dict = {}
            for k, v in form_data.items():
                if isinstance(v, UploadFile):
                    form_dict[k] = v.filename
                else:
                    form_dict[k] = v

            if 'multipart/form-data' not in content_type:
                args['x-www-form-urlencoded'] = await self.desensitization(form_dict)
            else:
                args['form-data'] = await self.desensitization(form_dict)

        return None if not args else args

    @staticmethod
    @sync_to_async
    def desensitization(args: dict[str, Any]):
        """脱敏处理"""

        for key, value in args.items():
            if key in settings.OPERATION_LOG_ENCRYPT_KEY_INCLUDE:
                match settings.OPERATION_LOG_ENCRYPT_TYPE:
                    case OperationLogCipherEnum.AES:
                        args[key] = (
                            AESCipher(settings.OPERATION_LOG_ENCRYPT_SECRET_KEY.get_secret_value()).encrypt(value)
                        ).hex()
                    case OperationLogCipherEnum.MD5:
                        args[key] = MD5Cipher.encrypt(value)
                    case OperationLogCipherEnum.ITS_DANGEROUS:
                        args[key] = ItsDCipher(settings.OPERATION_LOG_ENCRYPT_SECRET_KEY.get_secret_value()).encrypt(
                            value
                        )
                    case OperationLogCipherEnum.PLAN:
                        pass
                    case _:
                        args[key] = '*' * len(str(value))

        return args

    @classmethod
    async def consumer(cls) -> None:
        """创建任务"""
        while True:
            logs = await batch_dequeue(
                cls.log_queue,
                max_items=settings.OPERATION_LOG_QUEUE_BATCH_CONSUME_SIZE,
                timeout=settings.OPERATION_LOG_QUEUE_TIMEOUT,
            )
            if logs:
                try:
                    log.info('自动执行【操作日志批量创建】任务...')
                    await operation_log_service.bulk_create(objs=logs)
                finally:
                    if not cls.log_queue.empty():
                        cls.log_queue.task_done()
                    else:
                        log.info('完成执行【操作日志批量创建】任务...')

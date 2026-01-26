import json
import time

from asyncio import Queue
from typing import TYPE_CHECKING, Any

from fastapi import status
from starlette.datastructures import UploadFile
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.app.admin.schema.sys_operation_log import SysOperationLogCreate
from backend.app.admin.service import sys_operation_log_service
from backend.common.enum.custom import StatusEnum
from backend.common.log import log
from backend.common.queue import batch_dequeue
from backend.common.request.context import ctx
from backend.common.request.trace_id import get_request_trace_id
from backend.common.response.code import StandardResponseStatus
from backend.core.config import settings
from backend.database.postgresql import async_session

if TYPE_CHECKING:
    from fastapi import Request, Response


class OperationLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件"""

    _queue: Queue = Queue(maxsize=100000)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:

        path = request.url.path
        if path in settings.OPERATION_LOG_PATH_EXCLUDE or not path.startswith(f'{settings.FASTAPI_API_ROUTE_PREFIX}'):
            response = await call_next(request)
        else:
            method = request.method
            args = await self._get_request_args(request)

            # 执行请求
            code = StandardResponseStatus.HTTP_200.code
            msg = StandardResponseStatus.HTTP_200.msg
            _status = StatusEnum.ENABLE
            error = None

            try:
                response = await call_next(request)
                code = response.status_code
                elapsed = round((time.perf_counter() - ctx.perf_time) * 1000, 3)

                # 检查 ctx 中的异常信息
                for e in [
                    '__request_custom_exception__',
                    '__request_unknown_exception__',
                    '__request_http_exception__',
                    '__request_pydantic_user_error__',
                    '__request_assertion_error__',
                    '__request_validation_exception__',
                ]:
                    exception = ctx.get(e)
                    if exception:
                        code = exception.get('code')
                        msg = exception.get('msg')
                        log.error(f'{msg}')
                        _status = StatusEnum.DISABLE
                        break

            except Exception as e:
                error = e
                elapsed = round((time.perf_counter() - ctx.perf_time) * 1000, 3)
                code = getattr(e, 'code', status.HTTP_500_INTERNAL_SERVER_ERROR)
                _status = StatusEnum.DISABLE
                msg = getattr(e, 'msg', str(e))
                log.error(f'{e!s}')

            # 此信息只能在请求后获取
            route = request.scope.get('route')
            summary = route.summary or '' if route else ''

            # TODO JWT 认证中间件 的 user 信息

            # 日志记录
            log.debug(f'接口摘要：{summary}')
            log.debug(f'请求参数：{args}')
            log.info(f'{ctx.ip: <15} | {request.method: <8} | {elapsed:.3f}ms | {code!s: <6} | {path}')

            if request.method != 'OPTIONS':
                log.debug('<-- 请求结束')

            operation_log = SysOperationLogCreate(
                trace_id=get_request_trace_id(),
                username=None,
                module=summary,
                path=path,
                method=method,
                code=str(code),
                msg=msg,
                args=args,
                status=_status,
                ip=ctx.ip,
                country=ctx.country,
                region=ctx.region,
                city=ctx.city,
                user_agent=ctx.user_agent,
                os=ctx.os,
                browser=ctx.browser,
                device=ctx.device,
                cost_time=elapsed,  # 可能和日志存在微小差异（可忽略）
                operated_time=ctx.start_time,
            )

            await self._queue.put(operation_log)

            # 错误抛出
            if error:
                raise error from None

        return response  # type: ignore[possibly-unbound]

    async def _get_request_args(self, request: Request) -> dict[str, Any] | None:
        """获取请求参数"""
        args = {}
        sensitive_keys = frozenset(settings.OPERATION_LOG_ENCRYPT_KEY_INCLUDE)

        # 查询参数
        if request.query_params:
            args['query'] = self._desensitize_dict(dict(request.query_params), sensitive_keys)

        # 路径参数
        if request.path_params:
            args['path'] = self._desensitize_dict(request.path_params, sensitive_keys)

        # Tip: .body() 必须在 .form() 之前获取
        # https://github.com/encode/starlette/discussions/1933
        content_type = request.headers.get('content-type', '').split(';')[0].strip().lower()

        # 请求体
        body_data = await request.body()
        if body_data:
            if content_type == 'application/json' or content_type.endswith('+json'):
                try:
                    args['json'] = self._desensitize_nested(json.loads(body_data), sensitive_keys)
                except Exception:
                    args['data'] = body_data.decode('utf-8', 'ignore')
            else:
                args['data'] = body_data.decode('utf-8', 'ignore')

        # 表单参数
        form = await request.form()
        if form:
            form_dict = {}
            for key, value in form.items():
                # 文件上传 记录元数据
                if isinstance(value, UploadFile):
                    form_dict[key] = {
                        'filename': getattr(value, 'filename', ''),
                        'content_type': getattr(value, 'content_type', ''),
                        'size': getattr(value, 'size', 0),
                    }
                else:
                    form_dict[key] = value

            if form_dict:
                form_type = 'multipart_form-data' if content_type == 'multipart/form-data' else 'x-www-form-urlencoded'
                args[form_type] = self._desensitize_nested(form_dict, sensitive_keys)

        return self._truncate(args) if args else None

    @staticmethod
    def _truncate(args: dict[str, Any]) -> dict[str, Any]:
        """请求参数字典截断处理

        注意:
            - 最大限制 10KB, 超出部分将被截断
            - PostgreSQL JSON 字段虽然支持大数据, 但过大会影响查询性能
            - 保留所有键名, 仅截断过长的值
        """
        import json

        def _truncate_value(value_str: str, original_value: Any) -> Any:
            """截断单个值"""
            if len(value_str.encode('utf-8')) > 1024:
                return value_str[:200] + '...[truncated]'
            return original_value

        _max_size = 10240  # 数据最大大小（字节）10KB

        if not args:
            return args

        # 序列化并检查大小
        json_str = json.dumps(args, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')

        if len(json_bytes) <= _max_size:
            return args

        # 超出限制, 需要截断
        truncated_args = {}
        for key, value in args.items():
            if isinstance(value, (str, bytes)):
                value_str = str(value)
                truncated_args[key] = _truncate_value(value_str, value)
            elif isinstance(value, (list, dict)):
                value_str = json.dumps(value, ensure_ascii=False)
                truncated_args[key] = _truncate_value(value_str, value)
            else:
                truncated_args[key] = value

        final_json = json.dumps(truncated_args, ensure_ascii=False)
        if len(final_json.encode('utf-8')) > _max_size:
            # 如果还是太大, 添加警告标记并强制截断
            truncated_args['_truncated'] = True
            truncated_args['_original_size'] = len(json_bytes)

        return truncated_args

    @staticmethod
    def _desensitize_dict(data: dict[str, Any], keys: frozenset[str]) -> dict[str, Any]:
        """脱敏字典（一层）"""
        return {key: ' [***] ' if key in keys else value for key, value in data.items()}

    @staticmethod
    def _desensitize_nested(data: Any, keys: frozenset[str]) -> Any:
        """递归脱敏嵌套结构 - 支持多层字典和列表"""
        if isinstance(data, dict):
            return {
                key: (' [***] ' if key in keys else OperationLogMiddleware._desensitize_nested(value, keys))
                for key, value in data.items()
            }
        if isinstance(data, list):
            return [OperationLogMiddleware._desensitize_nested(item, keys) for item in data]
        return data

    @classmethod
    async def task(cls) -> None:
        """操作日志 任务

        使用 asyncio 的 create_task 启动后台任务, 持续从队列中获取日志并入库

        TODO 优化, 并注册到应用生命周期中
        ”"""
        while True:
            logs = await batch_dequeue(
                cls._queue,
                max_items=settings.OPERATION_LOG_QUEUE_BATCH_CONSUME_SIZE,
                time=settings.OPERATION_LOG_QUEUE_TIMEOUT,
            )
            if logs:
                try:
                    log.info('自动执行【操作日志批量创建】任务...')
                    async with async_session.begin() as db:
                        await sys_operation_log_service.batch_create(db=db, params_list=logs)
                except Exception as e:
                    log.error(f'操作日志入库失败, 丢失 {len(logs)} 条日志: {e}')
                finally:
                    for _ in range(len(logs)):
                        cls._queue.task_done()
                    else:
                        log.info('完成执行【操作日志批量创建】任务...')

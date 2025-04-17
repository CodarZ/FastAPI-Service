#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import Request

from backend.core.config import settings


def get_request_trace_id(request: Request) -> str:
    """从请求中提取 Trace ID

    常用于日志追踪、分布式链路追踪等场景，确保每个请求都能关联唯一的 Trace ID。
    """
    return request.headers.get(settings.TRACE_ID_REQUEST_HEADER_KEY) or settings.LOG_CID_DEFAULT_VALUE

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses

from enum import Enum
from typing import Final


@dataclasses.dataclass
class CustomResponse:
    """
    通用响应结果结构体, 自定义或标准响应封装。

    属性：
        code (int): 状态码, 如 200 表示成功, 400 表示错误
        msg (str): 提示信息, 描述当前响应的语义
    """

    code: int
    msg: str


class CustomCodeBase(Enum):
    """
    自定义状态码基类, 枚举成员应为包含 (code, msg) 的元组。

    示例：
        ```python
          class StatusCode(CustomCodeBase):
              SUCCESS = (200, "请求成功")
              ERROR = (500, "服务器内部错误")

          StatusCode.SUCCESS.code  # 输出: 200
          StatusCode.SUCCESS.msg   # 输出: "请求成功"
        ```
    """

    @property
    def code(self) -> int:
        """获取状态码"""
        return self.value[0]

    @property
    def msg(self) -> str:
        """获取状态码信息"""
        return self.value[1]


class CustomResponseCode(CustomCodeBase):
    """自定义响应状态码，提供更详细的错误信息。"""

    HTTP_200 = (200, '请求成功')
    HTTP_201 = (201, '新建请求成功')
    HTTP_202 = (202, '请求已接受，但处理尚未完成')
    HTTP_204 = (204, '请求成功，但没有返回内容')
    HTTP_400 = (400, '请求错误')
    HTTP_401 = (401, '未经授权')
    HTTP_403 = (403, '禁止访问')
    HTTP_404 = (404, '请求的资源不存在')
    HTTP_410 = (410, '请求的资源已永久删除')
    HTTP_422 = (422, '请求参数非法')
    HTTP_425 = (425, '无法执行请求，由于服务器无法满足要求')
    HTTP_429 = (429, '请求过于频繁，请稍后重试')
    HTTP_500 = (500, '服务器内部错误')
    HTTP_502 = (502, '网关错误')
    HTTP_503 = (503, '服务器暂时无法处理请求')
    HTTP_504 = (504, '网关超时')

    WS_1000 = (1000, '正常关闭')
    WS_1001 = (1001, '正在离开')
    WS_1002 = (1002, '协议错误')
    WS_1003 = (1003, '不支持的数据类型')
    WS_1006 = (1006, '异常关闭')
    WS_1011 = (1011, '内部错误')
    WS_1012 = (1012, '服务重启')
    WS_3000 = (3000, '未经授权')


class CustomErrorCode(CustomCodeBase):
    """
    自定义错误状态码，用于扩充系统错误码。
    例如：验证码错误、参数错误等。
    """

    CAPTCHA_ERROR = (40001, '验证码错误')


class StandardResponseCode:
    """
    HTTP codes
    See HTTP Status Code Registry:
    https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml

    And RFC 2324 - https://tools.ietf.org/html/rfc2324
    """

    HTTP_102: Final[int] = 102  # PROCESSING: 处理中
    HTTP_103: Final[int] = 103  # EARLY_HINTS: 提示信息
    HTTP_200: Final[int] = 200  # OK: 请求成功
    HTTP_201: Final[int] = 201  # CREATED: 已创建
    HTTP_202: Final[int] = 202  # ACCEPTED: 已接受
    HTTP_203: Final[int] = 203  # NON_AUTHORITATIVE_INFORMATION: 非权威信息
    HTTP_204: Final[int] = 204  # NO_CONTENT: 无内容
    HTTP_205: Final[int] = 205  # RESET_CONTENT: 重置内容
    HTTP_206: Final[int] = 206  # PARTIAL_CONTENT: 部分内容
    HTTP_207: Final[int] = 207  # MULTI_STATUS: 多状态
    HTTP_208: Final[int] = 208  # ALREADY_REPORTED: 已报告
    HTTP_226: Final[int] = 226  # IM_USED: 使用了
    HTTP_300: Final[int] = 300  # MULTIPLE_CHOICES: 多种选择
    HTTP_301: Final[int] = 301  # MOVED_PERMANENTLY: 永久移动
    HTTP_302: Final[int] = 302  # FOUND: 临时移动
    HTTP_303: Final[int] = 303  # SEE_OTHER: 查看其他位置
    HTTP_304: Final[int] = 304  # NOT_MODIFIED: 未修改
    HTTP_305: Final[int] = 305  # USE_PROXY: 使用代理
    HTTP_307: Final[int] = 307  # TEMPORARY_REDIRECT: 临时重定向
    HTTP_308: Final[int] = 308  # PERMANENT_REDIRECT: 永久重定向
    HTTP_400: Final[int] = 400  # BAD_REQUEST: 请求错误
    HTTP_401: Final[int] = 401  # UNAUTHORIZED: 未授权
    HTTP_402: Final[int] = 402  # PAYMENT_REQUIRED: 需要付款
    HTTP_403: Final[int] = 403  # FORBIDDEN: 禁止访问
    HTTP_404: Final[int] = 404  # NOT_FOUND: 未找到
    HTTP_405: Final[int] = 405  # METHOD_NOT_ALLOWED: 方法不允许
    HTTP_406: Final[int] = 406  # NOT_ACCEPTABLE: 不可接受
    HTTP_407: Final[int] = 407  # PROXY_AUTHENTICATION_REQUIRED: 需要代理身份验证
    HTTP_408: Final[int] = 408  # REQUEST_TIMEOUT: 请求超时
    HTTP_409: Final[int] = 409  # CONFLICT: 冲突
    HTTP_410: Final[int] = 410  # GONE: 已删除
    HTTP_411: Final[int] = 411  # LENGTH_REQUIRED: 需要内容长度
    HTTP_412: Final[int] = 412  # PRECONDITION_FAILED: 先决条件失败
    HTTP_413: Final[int] = 413  # REQUEST_ENTITY_TOO_LARGE: 请求实体过大
    HTTP_414: Final[int] = 414  # REQUEST_URI_TOO_LONG: 请求 URI 过长
    HTTP_415: Final[int] = 415  # UNSUPPORTED_MEDIA_TYPE: 不支持的媒体类型
    HTTP_416: Final[int] = 416  # REQUESTED_RANGE_NOT_SATISFIABLE: 请求范围不符合要求
    HTTP_417: Final[int] = 417  # EXPECTATION_FAILED: 期望失败
    HTTP_418: Final[int] = 418  # UNUSED: 闲置
    HTTP_421: Final[int] = 421  # MISDIRECTED_REQUEST: 被错导的请求
    HTTP_422: Final[int] = 422  # UNPROCESSABLE_CONTENT: 无法处理的实体
    HTTP_423: Final[int] = 423  # LOCKED: 已锁定
    HTTP_424: Final[int] = 424  # FAILED_DEPENDENCY: 依赖失败
    HTTP_425: Final[int] = 425  # TOO_EARLY: 太早
    HTTP_426: Final[int] = 426  # UPGRADE_REQUIRED: 需要升级
    HTTP_427: Final[int] = 427  # UNASSIGNED: 未分配
    HTTP_428: Final[int] = 428  # PRECONDITION_REQUIRED: 需要先决条件
    HTTP_429: Final[int] = 429  # TOO_MANY_REQUESTS: 请求过多
    HTTP_430: Final[int] = 430  # Unassigned: 未分配
    HTTP_431: Final[int] = 431  # REQUEST_HEADER_FIELDS_TOO_LARGE: 请求头字段太大
    HTTP_451: Final[int] = 451  # UNAVAILABLE_FOR_LEGAL_REASONS: 由于法律原因不可用
    HTTP_500: Final[int] = 500  # INTERNAL_SERVER_ERROR: 服务器内部错误
    HTTP_501: Final[int] = 501  # NOT_IMPLEMENTED: 未实现
    HTTP_502: Final[int] = 502  # BAD_GATEWAY: 错误的网关
    HTTP_503: Final[int] = 503  # SERVICE_UNAVAILABLE: 服务不可用
    HTTP_504: Final[int] = 504  # GATEWAY_TIMEOUT: 网关超时
    HTTP_505: Final[int] = 505  # HTTP_VERSION_NOT_SUPPORTED: HTTP 版本不支持
    HTTP_506: Final[int] = 506  # VARIANT_ALSO_NEGOTIATES: 变体也会协商
    HTTP_507: Final[int] = 507  # INSUFFICIENT_STORAGE: 存储空间不足
    HTTP_508: Final[int] = 508  # LOOP_DETECTED: 检测到循环
    HTTP_509: Final[int] = 509  # UNASSIGNED: 未分配
    HTTP_510: Final[int] = 510  # NOT_EXTENDED: 未扩展
    HTTP_511: Final[int] = 511  # NETWORK_AUTHENTICATION_REQUIRED: 需要网络身份验证

    """
    WebSocket codes
    https://www.iana.org/assignments/websocket/websocket.xml#close-code-number
    https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent
    """
    WS_1000: Final[int] = 1000  # NORMAL_CLOSURE: 正常闭合
    WS_1001: Final[int] = 1001  # GOING_AWAY: 正在离开
    WS_1002: Final[int] = 1002  # PROTOCOL_ERROR: 协议错误
    WS_1003: Final[int] = 1003  # UNSUPPORTED_DATA: 不支持的数据类型
    WS_1005: Final[int] = 1005  # NO_STATUS_RCVD: 没有接收到状态
    WS_1006: Final[int] = 1006  # ABNORMAL_CLOSURE: 异常关闭
    WS_1007: Final[int] = 1007  # INVALID_FRAME_PAYLOAD_DATA: 无效的帧负载数据
    WS_1008: Final[int] = 1008  # POLICY_VIOLATION: 策略违规
    WS_1009: Final[int] = 1009  # MESSAGE_TOO_BIG: 消息太大
    WS_1010: Final[int] = 1010  # MANDATORY_EXT: 必需的扩展
    WS_1011: Final[int] = 1011  # INTERNAL_ERROR: 内部错误
    WS_1012: Final[int] = 1012  # SERVICE_RESTART: 服务重启
    WS_1013: Final[int] = 1013  # TRY_AGAIN_LATER: 请稍后重试
    WS_1014: Final[int] = 1014  # BAD_GATEWAY: 错误的网关
    WS_1015: Final[int] = 1015  # TLS_HANDSHAKE: TLS握手错误
    WS_3000: Final[int] = 3000  # UNAUTHORIZED: 未经授权
    WS_3003: Final[int] = 3003  # FORBIDDEN: 禁止访问

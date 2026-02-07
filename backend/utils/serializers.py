from typing import Any

from msgspec import json
from starlette.responses import JSONResponse


class MsgSpecJSONResponse(JSONResponse):
    """基于 msgspec 的高性能 JSON 响应类"""

    def render(self, content: Any) -> bytes:
        """将内容编码为 JSON 字节串"""
        return json.encode(content)

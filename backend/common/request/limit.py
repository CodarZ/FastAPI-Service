from math import ceil
from typing import TYPE_CHECKING

from backend.common.exception import errors
from backend.common.response.code import StandardResponseStatus

if TYPE_CHECKING:
    from fastapi import Request, Response


async def http_callback_limit(_: Request, __: Response, expire: int):
    """限制 `expire` （毫秒）请求限制回调函数"""

    # 将毫秒转换为秒，并向上取整
    expires = ceil(expire / 1000)
    raise errors.HTTPError(
        code=StandardResponseStatus.HTTP_429.code,
        msg=StandardResponseStatus.HTTP_429.msg,
        headers={'Retry-After': str(expires)},
    )

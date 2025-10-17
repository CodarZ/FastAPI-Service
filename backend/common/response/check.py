from math import ceil

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute

from backend.common.exception import errors
from backend.common.response.code import CustomResponseCode


def ensure_unique_route_names(app: FastAPI) -> None:
    """检查路由名称是否唯一"""
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f'路由名称重复: {route.name}')
            temp_routes.add(route.name)


async def http_limit_callback(_: Request, __: Response, expire: int):
    """限制 `expire` （毫秒）请求限制回调函数"""
    # 将毫秒转换为秒，并向上取整
    expires = ceil(expire / 1000)
    raise errors.HTTPError(
        code=CustomResponseCode.HTTP_429.code,
        msg=CustomResponseCode.HTTP_429.msg,
        headers={'Retry-After': str(expires)},
    )

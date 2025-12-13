from typing import TYPE_CHECKING

from fastapi.routing import APIRoute

if TYPE_CHECKING:
    from fastapi import FastAPI


def ensure_unique_route_name(app: FastAPI) -> None:
    """检查路由名称是否唯一"""
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f'路由名称重复: {route.name}')
            temp_routes.add(route.name)


def simplify_operation_id(app: FastAPI) -> None:
    """简化 API 函数名称"""
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name

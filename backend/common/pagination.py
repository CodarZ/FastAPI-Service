from collections.abc import Sequence
from math import ceil
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar, cast

from fastapi import Depends, Query
from fastapi_pagination import pagination_ctx
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_pagination.links.bases import create_links
from pydantic import BaseModel, Field

from backend.common.schema import SchemaBase

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar('T')
SchemaT = TypeVar('SchemaT')


class _PageParams(SchemaBase, AbstractParams):
    """分页参数模型"""

    page: int = Query(default=1, ge=1, description='页码, 从 1 开始')
    size: int = Query(default=20, ge=1, le=100, description='每页数量, 默认 20, 最大 100')

    def to_raw_params(self) -> RawParams:
        return RawParams(limit=self.size, offset=self.size * (self.page - 1))


class _Links(BaseModel):
    first: str = Field(description='首页链接')
    prev: str | None = Field(None, description='上一页链接')
    self: str = Field(description='当前页链接')
    next: str | None = Field(None, description='下一页链接')
    last: str = Field(description='尾页链接')


class _PageDetail(BaseModel):
    """分页详情"""

    items: Sequence = Field([], description='当前页数据')
    page: int = Field(description='当前页码')
    size: int = Field(description='每页数量')
    total: int = Field(description='总数量')
    total_pages: int = Field(description='总页数')
    links: _Links = Field(description='分页链接')


class _CustomPage(_PageDetail, AbstractPage[T], Generic[T]):
    """自定义分页响应模型"""

    __params_type__ = _PageParams

    @classmethod
    def create(cls, items: Sequence[T], params: AbstractParams, total: int = 0, **kwargs: Any) -> Self:

        params = cast('_PageParams', params)

        page = params.page
        size = params.size
        total_pages = ceil(total / size)

        links = create_links(
            first={'page': 1, 'size': size},
            prev={'page': page - 1, 'size': size} if (page - 1) >= 1 else None,
            next={'page': page + 1, 'size': size} if (page + 1) <= total_pages else None,
            last={'page': total_pages, 'size': size} if total > 0 else {'page': 1, 'size': size},
        ).model_dump()

        return cls(items=list(items), page=page, size=size, total=total, total_pages=total_pages, links=_Links(**links))


class PageList[SchemaT](_PageDetail):
    """分页数据响应模型，用于 API 响应类型提示"""

    items: Sequence[SchemaT]


async def paging_data(db: AsyncSession, select: Select, **kwargs) -> dict[str, Any]:
    """基于 SQLAlchemy 分页器"""

    page_data = await apaginate(db, select, **kwargs)

    return page_data.model_dump()


# 分页依赖注入
DependsPagination = Depends(pagination_ctx(_CustomPage))

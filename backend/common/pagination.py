from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING, Any, Generic, Optional, Sequence, TypeVar

from fastapi import Depends, Query
from fastapi_pagination import pagination_ctx
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links.bases import create_links
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')
SchemaT = TypeVar('SchemaT')


class _CustomPageParams(BaseModel, AbstractParams):
    current: int = Query(1, ge=1, description='页码, 从 1 开始')
    pageSize: int = Query(20, ge=1, le=100, description='每页大小, 默认 20 条记录')

    def to_raw_params(self) -> RawParams:
        return RawParams(limit=self.pageSize, offset=self.pageSize * (self.current - 1))


class _Links(BaseModel):
    """分页链接"""

    first: str = Field(description='首页链接')
    last: str = Field(description='尾页链接')
    self: str = Field(description='当前页链接')
    next: Optional[str] = Field(description='下一页链接')
    prev: Optional[str] = Field(description='上一页链接')


class _PageDetails(BaseModel):
    """分页详情"""

    items: list = Field([], description='当前页 数据列表')
    current: int = Field(description='当前页码')
    pageSize: int = Field(description='每页数量')
    total: int = Field(description='数据总条数')
    totalPages: int = Field(description='总页数')
    links: _Links = Field(description='分页链接')


class _CustomPage(_PageDetails, AbstractPage[T], Generic[T]):
    """自定义分页响应类，用于封装分页查询结果"""

    __params_type__ = _CustomPageParams

    @classmethod
    def create(cls, items: Sequence[T], params: AbstractParams, **kwargs: Any):
        """创建分页响应对象"""

        if not isinstance(params, _CustomPageParams):
            raise TypeError('缺少分页必要的参数')

        total = kwargs.get('total', 0)
        create_links_func = kwargs.get('create_links', create_links)

        current = params.current
        pageSize = params.pageSize
        totalPages = ceil(total / pageSize) if pageSize else 0

        links = create_links_func(
            first={'current': 1, 'pageSize': pageSize},
            last=({'current': totalPages, 'pageSize': pageSize} if total > 0 else {'current': 1, 'pageSize': pageSize}),
            prev={'current': f'{current - 1}', 'pageSize': pageSize} if (current - 1) >= 1 else None,
            next=({'current': f'{current + 1}', 'pageSize': pageSize} if (current + 1) <= totalPages else None),
        ).model_dump()

        return cls(
            items=list(items), total=total, current=current, pageSize=pageSize, totalPages=totalPages, links=links
        )


class PageData(_PageDetails, Generic[SchemaT]):
    """通用分页数据模型, 用于API响应接口

    Example

      ```
        @router.get('/list', response_model=ResponseSchemaModel[PageData[UserDetail]])
        def user_list():
            return response_base.success(data=UserDetail(...))
      ```
    """

    items: list[SchemaT] = Field(..., description='当前页数据列表')


async def paging_data(db: AsyncSession, select: Select):
    """基于 SQLAlchemy 创建分页数据

    执行 SQLAlchemy 查询并应用分页，返回符合 _CustomPage 格式的分页结果
    """

    paginated_data: _CustomPage = await paginate(db, select)
    page_data = paginated_data.model_dump()
    return page_data


# 分页依赖注入
DependsPagination = Depends(pagination_ctx(_CustomPage))

from typing import TYPE_CHECKING, Any, TypeVar, overload

from pydantic import BaseModel, Field

from backend.common.response.code import StandardResponseStatus
from backend.utils.serializers import MsgSpecJSONResponse

if TYPE_CHECKING:
    from fastapi import Response

    from backend.common.response.code import ResponseStatus

SchemaT = TypeVar('SchemaT')


class ResponseModel(BaseModel):
    """不包含返回数据 schema 的通用型统一返回模型"""

    code: int = Field(default=StandardResponseStatus.HTTP_200.code, description='状态码')
    msg: str = Field(default=StandardResponseStatus.HTTP_200.msg, description='状态信息')
    data: Any = Field(None, description='返回数据')


class ResponseSchemaModel[SchemaT](ResponseModel):
    """包含返回数据 schema 的通用型统一返回模型"""

    data: SchemaT


class ResponseBase:
    """统一返回方法, 快速生成标准化的响应模型"""

    @overload
    @staticmethod
    def __response(
        *,
        res: StandardResponseStatus | ResponseStatus,
        data: None = None,
    ) -> ResponseModel: ...

    @overload
    @staticmethod
    def __response(
        *,
        res: StandardResponseStatus | ResponseStatus,
        data: SchemaT,
    ) -> ResponseSchemaModel[SchemaT]: ...

    @staticmethod
    def __response(
        *,
        res: StandardResponseStatus | ResponseStatus,
        data: SchemaT | None = None,
    ) -> ResponseModel | ResponseSchemaModel[SchemaT]:
        kwargs = {'code': res.code, 'msg': res.msg, 'data': data}
        return ResponseSchemaModel(**kwargs) if data is not None else ResponseModel(**kwargs)

    def success(
        self,
        *,
        res: StandardResponseStatus | ResponseStatus = StandardResponseStatus.HTTP_200,
        data: SchemaT | None = None,
    ) -> ResponseModel | ResponseSchemaModel[SchemaT]:
        """成功响应"""
        return self.__response(res=res, data=data)

    def fail(
        self,
        *,
        res: StandardResponseStatus | ResponseStatus = StandardResponseStatus.HTTP_400,
        data: SchemaT | None = None,
    ) -> ResponseModel | ResponseSchemaModel[SchemaT]:
        """失败响应"""
        return self.__response(res=res, data=data)

    @staticmethod
    def fast(
        *,
        res: StandardResponseStatus | ResponseStatus = StandardResponseStatus.HTTP_200,
        data: Any = None,
    ) -> Response:
        """此方法是为了提高接口响应速度而创建的，在解析较大 json 时有显著性能提升，但将丢失 pydantic 解析和验证"""
        return MsgSpecJSONResponse({'code': res.code, 'msg': res.msg, 'data': data})


response_base = ResponseBase()

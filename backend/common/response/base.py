#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from backend.common.response.code import CustomResponse, CustomResponseCode
from backend.utils.serializers import MsgSpecJSONResponse

SchemaT = TypeVar('SchemaT')
__all__ = ['ResponseModel', 'ResponseSchemaModel', 'response_base']


class ResponseModel(BaseModel):
    """不包含返回数据 schema 的通用型统一返回模型

    通过 Pydantic 定义的数据模型，用于返回统一格式的接口响应。

    示例用法::

        # 示例 1：直接返回 ResponseModel
        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})


        # 示例 2：方法返回类型为 ResponseModel
        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})


        # 示例 3：自定义返回码和消息
        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """

    code: int = Field(CustomResponseCode.HTTP_200.code, description='响应状态码')
    msg: str = Field(CustomResponseCode.HTTP_200.msg, description='响应消息')
    data: Any | None = Field(None, description='响应数据')


class ResponseSchemaModel(ResponseModel, Generic[SchemaT]):
    """包含 data schema 的统一返回模型，适用于非分页接口

    示例用法::

        # 示例 1：
        @router.get('/test', response_model=ResponseSchemaModel[ApiDetail])
        def test():
            return ResponseSchemaModel[ApiDetail](data=ApiDetail(...))


        # 示例 2：
        @router.get('/test')
        def test() -> ResponseSchemaModel[ApiDetail]:
            return ResponseSchemaModel[ApiDetail](data=ApiDetail(...))


        # 示例 3：
        @router.get('/test')
        def test() -> ResponseSchemaModel[ApiDetail]:
            res = CustomResponseCode.HTTP_200
            return ResponseSchemaModel[ApiDetail](code=res.code, msg=res.msg, data=GetApiDetail(...))
    """

    data: SchemaT


class ResponseBase:
    """统一返回方法，快速生成标准化的响应模型。"""

    @staticmethod
    def __response(
        *,
        res: CustomResponseCode | CustomResponse,
        data: Any | None = None,
    ):
        return ResponseModel(code=res.code, msg=res.msg, data=data)

    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ):
        return self.__response(res=res, data=data)

    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any | None = None,
    ):
        return self.__response(res=res, data=data)

    @staticmethod
    def fast_response(
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ):
        """提高接口响应速度

        解析较大 json 时提高性能。不会被 pydantic 解析和验证

        ⚠️ 使用此返回方法时，不能指定接口参数 response_model 和箭头返回类型

        示例用法::
            ```python
                @router.get('/test')
                def test():
                    return response_base.fast_response(data={'test': 'test'})
            ```

        """
        return MsgSpecJSONResponse({'code': res.code, 'msg': res.msg, 'data': data})


response_base = ResponseBase()

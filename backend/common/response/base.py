#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Generic, Optional, TypeVar

from fastapi import Response
from pydantic import BaseModel, Field

from backend.common.response.code import CustomResponse, CustomResponseCode
from backend.utils.serializers import MsgSpecJSONResponse

SchemaT = TypeVar('SchemaT')


class ResponseModel(BaseModel):
    """
    不包含返回数据 schema 的通用型统一返回模型

    示例::

        @router.get('/test', response_model=ResponseModel)
        def test():
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            return ResponseModel(data={'test': 'test'})


        @router.get('/test')
        def test() -> ResponseModel:
            res = CustomResponseCode.HTTP_200
            return ResponseModel(code=res.code, msg=res.msg, data={'test': 'test'})
    """

    code: int = Field(CustomResponseCode.HTTP_200.code, description='返回状态码')
    msg: str = Field(CustomResponseCode.HTTP_200.msg, description='返回信息')
    data: Any | None = Field(None, description='返回数据')


class ResponseSchemaModel(ResponseModel, Generic[SchemaT]):
    """
    包含 data schema 的统一返回模型，适用于非分页接口

    示例用法::

        # 示例 1：
        @router.get('/test', response_model=ResponseSchemaModel[GetUserInfo])
        def test():
            return ResponseSchemaModel[GetUserInfo](data=GetUserInfo(...))


        # 示例 2：
        @router.get('/test')
        def test() -> ResponseSchemaModel[GetUserInfo]:
            return ResponseSchemaModel[GetUserInfo](data=GetUserInfo(...))


        # 示例 3：
        @router.get('/test')
        def test() -> ResponseSchemaModel[GetUserInfo]:
            res = CustomResponseCode.HTTP_200
            return ResponseSchemaModel[GetUserInfo](code=res.code, msg=res.msg, data=GetUserInfo(...))
    """

    data: Optional[SchemaT] = None


class ResponseBase:
    """
    统一返回方法，快速生成标准化的响应模型。
    """

    @staticmethod
    def __response(
        *,
        res: CustomResponseCode | CustomResponse,
        data: Any | None = None,
    ) -> ResponseModel | ResponseSchemaModel:
        return ResponseModel(code=res.code, msg=res.msg, data=data)

    def success(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> ResponseModel | ResponseSchemaModel:
        """
        快捷方法，用于生成成功响应。

        :param res: 成功状态码及信息（默认为 HTTP_200）（CustomResponseCode 或 CustomResponse 实例）
        :param data: 成功返回的数据（可选）
        :return: 统一格式的成功响应 ResponseModel 模型
        """
        return self.__response(res=res, data=data)

    def fail(
        self,
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_400,
        data: Any = None,
    ) -> ResponseModel | ResponseSchemaModel:
        """
        快捷方法，用于生成失败响应。

        :param res: 失败状态码及信息（默认为 HTTP_400）（CustomResponseCode 或 CustomResponse 实例）
        :param data: 失败返回的数据（可选）
        :return: 统一格式的失败响应 ResponseModel 模型
        """
        return self.__response(res=res, data=data)

    @staticmethod
    def fast(
        *,
        res: CustomResponseCode | CustomResponse = CustomResponseCode.HTTP_200,
        data: Any | None = None,
    ) -> Response:
        """
        此方法是为了提高接口响应速度而创建的，在解析较大 json 时有显著性能提升，但将丢失 pydantic 解析和验证

        .. 注意::

            使用此返回方法时，不能指定接口参数 response_model 和箭头返回类型

        示例用法::

            @router.get('/test')
            def test():
                return response_base.fast(data={'test': 'test'})

        :param res: 成功状态码及信息（默认为 HTTP_200）
        :param data: 返回的数据（可选）
        :return: 直接返回序列化后的 JSON 数据
        """
        return MsgSpecJSONResponse({'code': res.code, 'msg': res.msg, 'data': data})


response_base: ResponseBase = ResponseBase()

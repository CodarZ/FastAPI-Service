from pydantic import BaseModel, Field

from .code import ResponseCode, ResponseStatus


class ResponseModel[T](BaseModel):
    """统一返回模型."""

    code: int = Field(default=ResponseCode.HTTP_200.code, description='状态码')
    msg: str = Field(default=ResponseCode.HTTP_200.msg, description='状态信息')
    data: T | None = Field(default=None, description='返回数据')


class ResponseBase:
    """统一返回方法."""

    @staticmethod
    def _response[T](
        *,
        res: ResponseCode | ResponseStatus,
        data: T | None = None,
    ) -> ResponseModel[T]:
        return ResponseModel[T](code=res.code, msg=res.msg, data=data)

    @classmethod
    def success[T](
        cls,
        *,
        res: ResponseCode | ResponseStatus = ResponseCode.HTTP_200,
        data: T | None = None,
    ) -> ResponseModel[T]:
        """成功响应."""
        return cls._response(res=res, data=data)

    @classmethod
    def fail[T](
        cls,
        *,
        res: ResponseCode | ResponseStatus = ResponseCode.HTTP_400,
        data: T | None = None,
    ) -> ResponseModel[T]:
        """失败响应."""
        return cls._response(res=res, data=data)

import inspect

from typing import Any, Callable, TypeVar

from fastapi import Query

from backend.common.schema import SchemaBase

T = TypeVar('T', bound=SchemaBase)


def create_dependency(schema_class: type[T]) -> Callable[..., T]:
    """
    为给定的 Pydantic Schema 创建一个通用的查询参数依赖函数

    Args:
        schema_class: Pydantic BaseModel 类

    Returns:
        一个可以用于 FastAPI Depends 的函数
    """

    # 获取 schema 的字段信息
    schema_fields = schema_class.model_fields

    # 构建依赖函数的参数列表
    params = []
    annotations = {}

    for field_name, field_info in schema_fields.items():
        # 获取字段类型
        field_type = field_info.annotation

        # 获取字段描述
        description = getattr(field_info, 'description', None) or field_name

        # 获取默认值
        default_value = field_info.default if field_info.default is not None else None

        # 添加参数注解
        annotations[field_name] = field_type

        # 构建参数定义
        if default_value is not None:
            param = inspect.Parameter(
                field_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Query(default=default_value, description=description),
                annotation=field_type,
            )
        else:
            param = inspect.Parameter(
                field_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Query(default=None, description=description),
                annotation=field_type,
            )
        params.append(param)

    # 创建动态函数
    def dependency_func(**kwargs: Any) -> T:
        """动态生成的查询参数依赖函数"""
        return schema_class(**kwargs)

    # 设置函数签名
    sig = inspect.Signature(parameters=params, return_annotation=schema_class)
    dependency_func.__signature__ = sig  # type: ignore
    dependency_func.__annotations__ = {**annotations, 'return': schema_class}
    dependency_func.__name__ = f'get_{schema_class.__name__.lower()}_params'
    dependency_func.__doc__ = f'构造 {schema_class.__name__} 查询参数'

    return dependency_func

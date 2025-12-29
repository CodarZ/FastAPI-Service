import importlib
import pkgutil

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from backend.common.log import log
from backend.core.path import BASE_PATH
from backend.utils.timezone import timezone

if TYPE_CHECKING:
    from types import ModuleType

# 延迟初始化, 避免循环引用
_EXCLUDED_SCHEMA_BASES: frozenset[type] = frozenset()
# 记录 schema 是否已重建
_schemas_rebuilt: bool = False


class SchemaBase(BaseModel):
    """所有业务 Schema 的基类

    统一配置：
    - use_enum_values: 自动将枚举转为其值
    - extra='forbid': 禁止传入未定义的额外字段
    - str_strip_whitespace: 自动去除字符串首尾空白
    - json_encoders: datetime 统一使用本地时区格式化
    """

    model_config = ConfigDict(
        use_enum_values=True,
        extra='forbid',
        str_strip_whitespace=True,
        json_encoders={
            datetime: lambda x: timezone.to_str(timezone.to_timezone(x)),
        },
    )


def auto_rebuild_all_schemas() -> None:
    """自动 rebuild 所有 schema

    扫描 backend/app/*/schema/ 下所有模块, 收集全部 Pydantic Schema,
    并在统一的命名空间中执行 model_rebuild, 解决跨模块前向引用问题。

    注意:
        - 此函数应在应用启动时调用一次
        - 必须在路由注册前执行
        - 确保只执行一次
    """
    # 单例检查：确保只执行一次
    global _schemas_rebuilt
    if _schemas_rebuilt:
        return
    _schemas_rebuilt = True

    app_dir = BASE_PATH / 'app'
    all_schemas: dict[str, type[BaseModel]] = {}

    # 遍历 app 目录下的所有子模块
    for module in pkgutil.iter_modules([str(app_dir)]):
        if not module.ispkg:
            continue

        # 检查 app 下所有模块下的 schema 子包子文件夹
        schema_path = app_dir / module.name / 'schema'
        if not schema_path.exists():
            continue

        # 动态导入并收集 Schema
        schema_pkg_name = f'backend.app.{module.name}.schema'
        try:
            schema_pkg = importlib.import_module(schema_pkg_name)
        except ImportError:
            log.warning(f'Schema 模块导入失败: {schema_pkg_name}')
            continue

        all_schemas.update(_collect_schemas_from_module(schema_pkg))

    # 在统一命名空间中重建所有 Schema, 解决前向引用
    for schema_cls in all_schemas.values():
        schema_cls.model_rebuild(_types_namespace=all_schemas)

    log.success(f'✅ Schema 自动重建完成, 共处理 {len(all_schemas)} 个 Schema')


def _get_excluded_bases() -> frozenset[type]:
    """获取需排除的 Schema 基类集合"""
    global _EXCLUDED_SCHEMA_BASES
    if not _EXCLUDED_SCHEMA_BASES:
        _EXCLUDED_SCHEMA_BASES = frozenset({BaseModel, SchemaBase})
    return _EXCLUDED_SCHEMA_BASES


def _is_valid_schema(name: str, obj: object) -> bool:
    """判断对象是否为有效的业务 Schema 类"""
    return (
        isinstance(obj, type)
        and issubclass(obj, BaseModel)
        and obj not in _get_excluded_bases()
        and not name.startswith('_')
    )


def _collect_schemas_from_module(schema_pkg: 'ModuleType') -> dict[str, type[BaseModel]]:
    """从模块中收集所有有效的 Schema 类"""
    return {name: obj for name, obj in vars(schema_pkg).items() if _is_valid_schema(name, obj)}

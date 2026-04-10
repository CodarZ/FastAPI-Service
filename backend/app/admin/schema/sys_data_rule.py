from pydantic import ConfigDict, Field

from backend.common.enum import DataRuleExpressionEnum, RBACLogicalEnum, StatusEnum
from backend.common.schema import SchemaBase
from backend.common.schema.type import IdsListInt


# ==================== 基础 Schema ====================
class SysDataRuleBase(SchemaBase):
    """数据权限规则核心复用字段."""

    name: str = Field(..., max_length=64, description='规则名称')
    code: str | None = Field(default=None, max_length=64, description='规则编码')
    model_name: str = Field(..., max_length=64, description='模型名称（SQLAlchemy 模型类名）')
    column_name: str = Field(..., max_length=64, description='字段名称（模型中的列名）')
    operator: RBACLogicalEnum = Field(..., description='运算符（规则间连接逻辑）')
    expression: DataRuleExpressionEnum = Field(..., description='表达式（字段与值的比较关系）')
    value: str | None = Field(default=None, max_length=255, description='规则值（支持变量占位符如 ${dept_ids}）')
    remark: str | None = Field(default=None, max_length=500, description='备注')


# ==================== 输入 Schema ====================
class SysDataRuleCreate(SysDataRuleBase):
    """数据权限规则创建请求."""

    status: StatusEnum = Field(default=StatusEnum.ENABLE, description='状态')


class SysDataRuleUpdate(SysDataRuleBase):
    """数据权限规则全量更新请求."""

    status: StatusEnum = Field(..., description='状态')


class SysDataRulePatchStatus(SchemaBase):
    """数据权限规则状态局部更新请求."""

    status: StatusEnum = Field(..., description='状态')


class SysDataRuleBatchDelete(SchemaBase):
    """数据权限规则批量删除请求."""

    ids: IdsListInt = Field(..., min_length=1, description='数据规则 ID 列表')


class SysDataRuleBatchPatchStatus(SchemaBase):
    """数据权限规则批量状态更新."""

    ids: IdsListInt = Field(..., min_length=1, description='数据规则 ID 列表')
    status: StatusEnum = Field(..., description='状态')


# ==================== 输出 Schema ====================
class SysDataRuleInfoBase(SysDataRuleBase):
    """数据权限规则核心输出基类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='数据规则 ID')
    status: StatusEnum = Field(..., description='状态')


class SysDataRuleInfo(SysDataRuleInfoBase):
    """数据权限规则通用预览信息."""

    pass


class SysDataRuleDetail(SysDataRuleInfoBase):
    """数据权限规则详情."""

    pass


class SysDataRuleListItem(SysDataRuleInfoBase):
    """数据权限规则分页列表结构."""

    pass


class SysDataRuleSimple(SchemaBase):
    """数据权限规则嵌套用压缩微型类."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description='数据规则 ID')
    name: str = Field(..., description='规则名称')


class SysDataRuleOption(SchemaBase):
    """数据权限规则下拉选项."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    value: int = Field(alias='id', description='选项值')
    label: str = Field(alias='name', description='选项标签')


# ==================== 查询 Schema ====================
class SysDataRuleFilter(SchemaBase):
    """数据权限规则查询过滤条件."""

    name: str | None = Field(default=None, max_length=64, description='按规则名称过滤')
    code: str | None = Field(default=None, max_length=64, description='按规则编码过滤')
    model_name: str | None = Field(default=None, max_length=64, description='按模型名称过滤')
    status: StatusEnum | None = Field(default=None, description='按状态过滤')

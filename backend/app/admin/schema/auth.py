from datetime import datetime

from pydantic import Field
from backend.app.admin.schema.sys_user import SysUserDetail
from backend.common.schema import SchemaBase


# ==================== Token Schema ====================
class AccessTokenBase(SchemaBase):
    """令牌"""

    access_token: str = Field(description='令牌')
    expire_time: datetime = Field(description='过期时间(datetime 类型)')
    session_uuid: str = Field(description='会话 UUID')


class AccessTokenCreate(AccessTokenBase):
    """创建令牌"""


# ==================== Login Schema ====================
class LoginRequest(SchemaBase):
    """登录请求"""

    username: str = Field(description='用户名')
    password: str = Field(description='密码')


class LoginResponse(AccessTokenBase):
    """登录响应"""

    user: SysUserDetail = Field(description='用户信息')


class SwaggerLoginResponse(SchemaBase):
    """Swagger 认证令牌"""

    access_token: str = Field(description='访问令牌')
    token_type: str = Field('Bearer', description='令牌类型')
    user: SysUserDetail = Field(description='用户信息')

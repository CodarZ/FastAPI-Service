from typing import TYPE_CHECKING

from pydantic import Field

from backend.common.schema import SchemaBase

if TYPE_CHECKING:
    from backend.app.admin.schema.sys_user import SysUserInfo


class LoginRequest(SchemaBase):
    """登录请求"""

    username: str = Field(min_length=4, max_length=20, description='用户名')
    password: str = Field(min_length=8, max_length=128, description='密码')
    captcha: str | None = Field(default=None, max_length=10, description='验证码')


class LoginResponse(SchemaBase):
    """登录响应"""

    access_token: str = Field(description='访问令牌')
    token_type: str = Field(default='Bearer', description='令牌类型')
    expires_in: int = Field(description='过期时间(秒)')
    user: SysUserInfo = Field(description='用户信息')

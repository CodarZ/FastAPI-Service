# 数据验证规范

## Pydantic 模型验证

- 使用 Pydantic 模型进行数据验证
- 定义清晰的请求和响应模型
- 不要新增字段验证器
- 提供有意义的验证错误信息

## Schema 设计原则

- 保持 Schema 简洁明了
- 使用适当的字段类型和约束
- 为复杂字段添加 Field 描述
- 区分输入和输出 Schema

## 验证最佳实践

- 在 API 层进行输入验证
- 使用类型提示增强代码可读性
- 避免重复的验证逻辑
- 统一验证错误消息格式

## 示例

```python
from pydantic import BaseModel, Field

class UserCreateSchema(BaseModel):
    """用户创建"""
    name: str = Field(..., min_length=1, max_length=50, description="用户姓名")
    email: str = Field(..., description="邮箱地址")
    age: int = Field(..., ge=0, le=120, description="年龄")

class UserResponseSchema(BaseModel):
    """用户响应"""
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户姓名")
    email: str = Field(..., description="邮箱地址")
    created_at: str = Field(..., description="创建时间")
```

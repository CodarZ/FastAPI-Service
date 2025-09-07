# 代码逻辑规范

## 核心原则

- 在保证逻辑清晰的情况下，尽量避免使用多元表达式（如三元运算符）
- 保持代码的可读性和可维护性
- 使用提前返回模式简化代码

## 代码组织

- 移除不必要的中间变量
- 添加适当的空行，提高代码可读性
- 优先处理错误和边缘案例

## 错误处理

- 只在必要时添加 try-except
- 对错误条件使用提前返回，以避免嵌套较深的 if 语句
- 避免不必要的 else 语句，而应使用 if-return 模式
- 实施适当的错误记录和用户友好型错误信息
- 使用自定义错误类型或错误工厂进行一致的错误处理

## 示例

```python
# 推荐：提前返回模式
def validate_user_data(data: dict[str, Any]) -> dict[str, Any]:
    if not data:
        return {"error": "数据为空"}

    if "name" not in data:
        return {"error": "缺少姓名字段"}

    return {"status": "success", "data": data}

# 不推荐：嵌套 if 语句
def validate_user_data_bad(data: dict[str, Any]) -> dict[str, Any]:
    if data:
        if "name" in data:
            return {"status": "success", "data": data}
        else:
            return {"error": "缺少姓名字段"}
    else:
        return {"error": "数据为空"}
```

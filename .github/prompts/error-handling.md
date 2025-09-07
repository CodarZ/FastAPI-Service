# 错误处理规范

## FastAPI 异常处理

- 使用 FastAPI 的异常处理机制
- 统一错误响应格式
- 根据错误工厂 @backend\common\exception\errors.py 提供清晰的错误信息和错误码

## 日志记录

- 记录关键错误信息到日志系统 @backend\common\log.py
- 区分不同级别的日志（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- 包含足够的上下文信息便于调试

## 错误响应格式

- 保持一致的错误响应结构
- 提供用户友好的错误信息
- 避免暴露内部实现细节

## 示例

```python
from backend.common.exception.errors import BusinessError
from backend.common.log import logger

async def process_user_data(user_id: int) -> dict[str, Any]:
    """处理用户数据"""
    try:
        # 业务逻辑处理
        data = await get_user_data(user_id)
        if not data:
            raise BusinessError("用户不存在")
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"处理用户数据失败: {e}", extra={"user_id": user_id})
        raise
```

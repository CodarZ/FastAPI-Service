# 性能优化规范

## 异步处理原则

- 接口函数内的阻塞型事件使用 run_in_threadpool 处理
- 尽量减少阻塞 I/O 操作
- 在所有数据库调用和外部 API 请求中使用异步操作

## 缓存策略

- 使用 Redis 工具 @backend\database\redis.py
- 对静态数据和频繁访问的数据实施缓存
- 合理设置缓存过期时间

## 性能指标

- 优先考虑 API 性能指标（响应时间、延迟、吞吐量）
- 监控数据库查询性能
- 避免 N+1 查询问题

## 示例

```python
from fastapi.concurrency import run_in_threadpool

async def process_heavy_task(data: dict) -> dict:
    """处理重计算任务"""
    # 将阻塞操作移到线程池
    result = await run_in_threadpool(heavy_computation, data)
    return result
```

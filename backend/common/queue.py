import asyncio
import time as time_module

from asyncio import Queue

from backend.common.log import log


async def batch_dequeue(queue: Queue, max_items: int, time: float) -> list:
    """
    从异步队列中获取多个任务

    :param queue: 用于获取任务的 `asyncio.Queue` 队列
    :param max_items: 从队列中获取的最大任务数量
    :param time: 总的等待超时时间（秒）
    :return:
    """
    items = []
    start_time = time_module.time()

    try:
        # 第一阶段: 非阻塞快速获取队列中已有的任务
        while len(items) < max_items:
            try:
                item = queue.get_nowait()
                items.append(item)
            except asyncio.QueueEmpty:
                break

        # 第二阶段: 如果还需要更多任务且未超时, 则等待获取
        while len(items) < max_items:
            elapsed = time_module.time() - start_time
            remaining_time = time - elapsed

            if remaining_time <= 0:
                break

            try:
                item = await asyncio.wait_for(queue.get(), timeout=remaining_time)
                items.append(item)
            except asyncio.TimeoutError:
                break

    except Exception as e:
        log.error(f'队列批量获取失败: {e}')

    return items

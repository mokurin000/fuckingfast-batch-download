from asyncio import Queue
from collections.abc import Coroutine


async def consume_tasks(tasks: Queue[Coroutine]):
    while True:
        co = await tasks.get()
        if co is None:
            break
        tasks.task_done()

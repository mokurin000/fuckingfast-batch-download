from asyncio import Queue
from collections.abc import Coroutine


async def consume_tasks(tasks: Queue[Coroutine]):
    while True:
        await tasks.get()
        tasks.task_done()

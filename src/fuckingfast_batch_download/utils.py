import urllib.parse
from asyncio import Queue
from collections.abc import Coroutine

from playwright.async_api import Page

from fuckingfast_batch_download.log import logger


async def consume_tasks(tasks: Queue[Coroutine], worker_name):
    while True:
        payload = await tasks.get()
        tasks.task_done()

        if payload is None:
            break


def on_page(page: Page):
    url = page.url
    parsed = urllib.parse.urlparse(url)

    if parsed.hostname is None:
        return
    if parsed.hostname != "fuckingfast.co":
        return page.close()

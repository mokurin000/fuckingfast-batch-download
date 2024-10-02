import urllib.parse
from asyncio import Queue
from collections.abc import Coroutine

from playwright.async_api import Page, Playwright, Error as PlaywrightError

from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.config import SKIP_EDGE


HEADLESS = True


async def launch_browser(playwright: Playwright):
    if not SKIP_EDGE:
        try:
            browser = await playwright.chromium.launch(
                headless=HEADLESS, channel="msedge"
            )
        except PlaywrightError:
            logger.warning("Edge was not found, fallback to Chromium")
            browser = await playwright.chromium.launch(headless=HEADLESS)
    else:
        browser = await playwright.chromium.launch(headless=HEADLESS)

    return browser


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

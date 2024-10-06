import urllib.parse
from asyncio import Queue
from collections.abc import Coroutine

from playwright.async_api import Page, Playwright, Error as PlaywrightError

from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download import config


async def launch_browser(playwright: Playwright):
    logger.info(
        f"Starting browser with headless {config.HEADLESS}, skip-edge {config.SKIP_EDGE}"
    )
    if not config.SKIP_EDGE:
        try:
            browser = await playwright.chromium.launch(
                headless=config.HEADLESS, channel="msedge"
            )
        except PlaywrightError:
            logger.warning("Edge was not found, fallback to Chromium")
            browser = await playwright.chromium.launch(headless=config.HEADLESS)
    else:
        browser = await playwright.chromium.launch(headless=config.HEADLESS)

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

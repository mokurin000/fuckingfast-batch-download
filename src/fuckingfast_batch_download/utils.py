import urllib.parse
from pathlib import Path
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


def export_to_file(results: list[tuple[str, str]], output: Path | str):
    def pair_to_str(pair: tuple[str, str]):
        uri = pair[0]
        filename = pair[1]
        indent = " " * 4
        return f"{uri}\n{indent}out={filename}\n{indent}continue=true"

    with open(output, "a", encoding="utf-8") as out:
        out.write(
            "\n".join(map(pair_to_str, sorted(results, key=lambda pair: pair[1])))
            + "\n"
        )

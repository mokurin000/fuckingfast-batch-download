import urllib.parse
from asyncio import Queue
from io import TextIOWrapper
from collections.abc import Coroutine

from playwright.async_api import Playwright, Error as PlaywrightError

from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download import config


async def launch_browser(playwright: Playwright):
    logger.info(f"Starting browser with headless {config.HEADLESS}")

    try:
        browser = await playwright.chromium.launch(
            headless=config.HEADLESS, channel="msedge"
        )
    except PlaywrightError:
        logger.warning("Edge was not found, fallback to Chromium")
        browser = await playwright.chromium.launch(headless=config.HEADLESS)

    return browser


async def consume_tasks(tasks: Queue[Coroutine]):
    while True:
        payload = await tasks.get()
        tasks.task_done()

        if payload is None:
            break


def export_to_file(results: list[tuple[str, str]], output: TextIOWrapper):
    def pair_to_str(pair: tuple[str, str]):
        uri, filename = pair
        indent = " " * 4
        return f"{uri}\n{indent}out={filename}\n{indent}continue=true"

    output.write(
        "\n".join(map(pair_to_str, sorted(results, key=lambda pair: pair[1]))) + "\n"
    )
    output.flush()

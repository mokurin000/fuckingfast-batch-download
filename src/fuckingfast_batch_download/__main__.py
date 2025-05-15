import asyncio
import argparse
from asyncio import Queue
from argparse import Namespace
from collections.abc import Coroutine

from tqdm.asyncio import tqdm_asyncio
from tqdm.contrib.logging import logging_redirect_tqdm
from playwright.async_api import async_playwright, Browser

import fuckingfast_batch_download.config as config
from fuckingfast_batch_download.exceptions import FileNotFound, RateLimited
from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.scrape import extract_url_page
from fuckingfast_batch_download.utils import (
    consume_tasks,
    launch_browser,
    export_to_file,
)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"


async def worker_func(
    tasks: Queue[Coroutine],
    tqdm: tqdm_asyncio,
    browser: Browser,
    results: list[tuple[str, str]],
):
    worker_name = asyncio.current_task().get_name()

    ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
    if config.SAVE_TRACE:
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")
    page = await ctx.new_page()

    while True:
        payload = await tasks.get()
        if payload is None:
            tasks.task_done()
            break

        try:
            url = payload
            result = await extract_url_page(page, url)
            results.append(result)
        except RateLimited:
            logger.error("rate limit! exiting")

            tasks.task_done()
            await consume_tasks(tasks)
            break
        except FileNotFound as e:
            logger.warning(f"{e.filename} not found!")
        except TimeoutError as e:
            logger.warning(f"Timeout: {e.__cause__}")

        tqdm.update()
        tasks.task_done()
    logger.info(f"Worker {worker_name} exiting...")
    if config.SAVE_TRACE:
        await ctx.tracing.stop(path=f"trace-{worker_name}.zip")
    await ctx.close()


def run_with_args(args: Namespace):
    config.TIMEOUT_PER_PAGE = int(args.timeout)
    config.MAX_WORKERS = int(args.max_workers)
    config.URLS_INPUT = args.urls_file
    config.ARIA2_OUTPUT = args.aria2c_file
    config.SAVE_TRACE = bool(args.save_trace)
    config.HEADLESS = not bool(args.no_headless)

    with logging_redirect_tqdm():
        asyncio.run(run())


async def concurrent_start(urls: list[str], browser: Browser):
    tasks = Queue()
    tqdm = tqdm_asyncio(total=len(urls))
    results = []
    workers = [
        asyncio.create_task(
            worker_func(tasks, tqdm, browser, results), name=f"worker_{i + 1}"
        )
        for i in range(config.MAX_WORKERS)
    ]

    for url in urls:
        await tasks.put(url)
    await tasks.join()

    if config.ARIA2_OUTPUT is not None:
        export_to_file(results, config.ARIA2_OUTPUT)

    for _ in workers:
        await tasks.put(None)
    for worker in workers:
        while not worker.done():
            await asyncio.sleep(0.5)


async def start(urls: list[str], browser: Browser):
    ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
    if config.SAVE_TRACE:
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")

    page = await ctx.new_page()

    results = []
    for url in tqdm_asyncio(urls):
        try:
            result = await extract_url_page(page, url)
            results.append(result)
        except RateLimited:
            logger.error("rate limit! exiting")
            break
        except FileNotFound as e:
            logger.warning(f"{e.filename} not found!")

    if config.ARIA2_OUTPUT is not None:
        export_to_file(results, config.ARIA2_OUTPUT)
    if config.SAVE_TRACE:
        await ctx.tracing.stop(path="trace.zip")
    await ctx.close()


async def run():
    urls = [url for url in config.URLS_INPUT.read().split("\n") if url]

    enable_concurrent = config.MAX_WORKERS > 1
    async with async_playwright() as playwright:
        logger.info("Launching browser...")
        browser = await launch_browser(playwright)

        if enable_concurrent:
            await concurrent_start(urls=urls, browser=browser)
        else:
            await start(urls=urls, browser=browser)

        await browser.close()
        logger.info("Browser closed.")


# The main function can be used as a CLI entrypoint
def main():
    parser = argparse.ArgumentParser(description="Web scraper with aria2c output")
    parser.add_argument(
        "urls_file",
        help="Input file containing URLs",
        type=argparse.FileType("r", encoding="utf-8"),
    )
    parser.add_argument(
        "aria2c_file",
        help="Output file for aria2c download links",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    parser.add_argument(
        "--timeout", type=int, default=5000, help="Timeout per page (ms)"
    )
    parser.add_argument(
        "--max-workers", type=int, default=2, help="Maximum number of workers"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Don't start browser as headless",
    )
    parser.add_argument(
        "--save-trace",
        action="store_true",
        help="Save trace files (for debugging only)",
    )
    args = parser.parse_args()
    run_with_args(args)


if __name__ == "__main__":
    main()

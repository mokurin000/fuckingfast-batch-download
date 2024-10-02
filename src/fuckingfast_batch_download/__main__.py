import asyncio
import argparse
import logging
from asyncio import Queue
from argparse import Namespace
from collections.abc import Coroutine

from tqdm.asyncio import tqdm_asyncio
from tqdm.contrib.logging import logging_redirect_tqdm
from playwright.async_api import async_playwright, Browser

import fuckingfast_batch_download.config as config
from fuckingfast_batch_download.exceptions import FileNotFound, RateLimited
from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.scrap import extract_url_page
from fuckingfast_batch_download.utils import consume_tasks, on_page, launch_browser

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"


async def worker_func(tasks: Queue[Coroutine], tqdm: tqdm_asyncio, browser: Browser):
    worker_name = asyncio.current_task().get_name()

    ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
    ctx.on("page", on_page)
    if config.SAVE_TRACE:
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")
    page = await ctx.new_page()

    while True:
        payload = await tasks.get()
        if payload is None:
            tasks.task_done()
            break

        try:
            url, outfile = payload
            await extract_url_page(page, url, outfile, close_page=False)
        except RateLimited:
            tasks.task_done()

            logging.error("rate limit! exiting")
            await consume_tasks(tasks)
            break
        except FileNotFound as e:
            logging.error(f"{e.filename} not found!")

        tqdm.update()
        tasks.task_done()
    logger.info(f"Worker {worker_name} exiting...")
    if config.SAVE_TRACE:
        await ctx.tracing.stop(path=f"trace-{worker_name}.zip")
    await ctx.close()


def blocking_run(args: Namespace):
    with logging_redirect_tqdm():
        asyncio.run(run(args))


async def concurrent_start(urls: list[str], browser: Browser):
    tasks = Queue()
    tqdm = tqdm_asyncio(total=len(urls))
    workers = [
        asyncio.create_task(worker_func(tasks, tqdm, browser), name=f"worker_{i+1}")
        for i in range(config.MAX_WORKERS)
    ]

    for url in urls:
        await tasks.put((url, config.ARIA2_OUTPUT))
    await tasks.join()

    for _ in workers:
        await tasks.put(None)
    for worker in workers:
        while not worker.done():
            await asyncio.sleep(0.5)


async def start(urls: list[str], browser: Browser):
    ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
    ctx.on("page", on_page)
    if config.SAVE_TRACE:
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")

    page = await ctx.new_page()
    for url in tqdm_asyncio(urls):
        await extract_url_page(page, url, config.ARIA2_OUTPUT)

    if config.SAVE_TRACE:
        await ctx.tracing.stop(path="trace.zip")
    await ctx.close()


async def run(args: Namespace):
    config.TIMEOUT_PER_PAGE = int(args.timeout)
    config.MAX_WORKERS = int(args.max_workers)
    config.URLS_INPUT = args.urls_file
    config.ARIA2_OUTPUT = args.aria2c_file
    config.SAVE_TRACE = bool(args.save_trace)
    config.HEADLESS = not bool(args.no_headless)
    config.SKIP_EDGE = bool(args.skip_edge)

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
        type=argparse.FileType("r"),
    )
    parser.add_argument(
        "aria2c_file",
        help="Output file for aria2c download links",
        type=argparse.FileType("w"),
    )
    parser.add_argument(
        "--timeout", type=int, default=5000, help="Timeout per page (ms)"
    )
    parser.add_argument(
        "--max-workers", type=int, default=2, help="Maximum number of workers"
    )
    parser.add_argument(
        "--save-trace",
        action="store_true",
        help="Save trace files (for debugging only)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Start headless browser",
    )
    parser.add_argument(
        "--skip-edge",
        action="store_true",
        help="Don't use Edge",
    )
    args = parser.parse_args()
    blocking_run(args)


if __name__ == "__main__":
    main()

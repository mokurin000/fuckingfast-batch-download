import asyncio
import argparse
import logging
import urllib.parse
from pathlib import Path
from asyncio import Queue
from collections.abc import Coroutine

from aiofile import async_open
from tqdm.asyncio import tqdm_asyncio
from tqdm.contrib.logging import logging_redirect_tqdm
from playwright.async_api import async_playwright, Page

import fuckingfast_batch_download.config as config
from fuckingfast_batch_download.exceptions import FileNotFound, RateLimited
from fuckingfast_batch_download.utils import consume_tasks
from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.scrap import extract_url_ctx, extract_url_page

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"


async def worker_func(tasks: Queue[Coroutine], tqdm: tqdm_asyncio):
    while True:
        coro = await tasks.get()
        if coro is None:
            logger.info(f"Worker {asyncio.current_task().get_name()} exiting...")
            break

        try:
            await coro
        except RateLimited:
            tasks.task_done()

            logging.error("rate limit! exiting")
            await consume_tasks(tasks)
        except FileNotFound as e:
            logging.error(f"{e.filename} not found!")

        tqdm.update()
        tasks.task_done()


def blocking_run(args):
    with logging_redirect_tqdm():
        asyncio.run(run(args))


async def run(args):
    config.TIMEOUT_PER_PAGE = int(args.timeout)
    config.MAX_WORKERS = int(args.max_workers)
    config.URLS_FILE = args.urls_file
    config.ARIA2C_FILE = args.aria2c_file

    with open(config.URLS_FILE, "r", encoding="utf-8") as urls:
        urls = [url for url in urls.read().split("\n") if url]

    async with async_playwright() as playwright:

        def on_page(page: Page):
            url = page.url
            parsed = urllib.parse.urlparse(url)

            if parsed.hostname is None:
                return
            if parsed.hostname != "fuckingfast.co":
                return page.close()

        logger.info("Launching browser...")
        browser = await playwright.chromium.launch(headless=False)
        ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
        ctx.on("page", on_page)
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")

        if config.MAX_WORKERS > 1:
            tasks = Queue()
            tqdm = tqdm_asyncio(total=len(urls))
            workers = [
                asyncio.create_task(worker_func(tasks, tqdm), name=f"worker_{i+1}")
                for i in range(config.MAX_WORKERS)
            ]

            async with async_open(config.ARIA2C_FILE, "a", encoding="utf-8") as f:
                for url in urls:
                    await tasks.put(extract_url_ctx(ctx, url, f))
                await tasks.join()

            for _ in workers:
                await tasks.put(None)
        else:
            async with async_open(config.ARIA2C_FILE, "a", encoding="utf-8") as f:
                page = await ctx.new_page()
                for url in tqdm_asyncio(urls):
                    await extract_url_page(page, url, f)

        await ctx.tracing.stop(path="trace.zip")
        await ctx.close()
        await browser.close()
        logger.info("Browser closed.")


# The main function can be used as a CLI entrypoint
def main():
    parser = argparse.ArgumentParser(description="Web scraper with aria2c output")
    parser.add_argument("urls_file", type=Path, help="Input file containing URLs")
    parser.add_argument(
        "aria2c_file", type=Path, help="Output file for aria2c download links"
    )
    parser.add_argument(
        "--timeout", type=int, default=5000, help="Timeout per page (ms)"
    )
    parser.add_argument(
        "--max_workers", type=int, default=2, help="Maximum number of workers"
    )
    args = parser.parse_args()
    blocking_run(args)


if __name__ == "__main__":
    main()

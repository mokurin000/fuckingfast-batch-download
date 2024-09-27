import asyncio
import argparse
import logging
import urllib.parse
from pathlib import Path
from asyncio import Queue
from collections.abc import Coroutine

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from aiofile import async_open
from playwright.async_api import async_playwright, Page, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"


async def worker_func(tasks: Queue[Coroutine]):
    while True:
        coro = await tasks.get()
        logger.info(
            f"Worker {asyncio.current_task().get_name()} executing task: {coro}"
        )
        await coro
        tasks.task_done()


async def extract_url_page(page: Page, url: str, aria2c_file, close_page=False):
    logger.info(f"Navigating to URL: {url}")
    await page.goto(url)

    download_loc = page.locator("button.link-button")
    async with page.expect_download(timeout=TIMEOUT_PER_PAGE) as download_info:
        logger.info("Initiating download...")
        await download_loc.click()
        await download_loc.click()

    download = await download_info.value
    await download.cancel()
    if close_page:
        await page.close()

    filename = url.split("#")[-1]
    async with async_open(aria2c_file, "a", encoding="utf-8") as f:
        await f.write(f"{download.url}\n    out={filename}\n    continue=true\n")
    logger.info(f"Download URL: {download.url}, Filename: {filename}")


async def extract_url_ctx(ctx: BrowserContext, url: str, aria2c_file):
    page = await ctx.new_page()
    await extract_url_page(page, url, aria2c_file, close_page=True)


def blocking_run(args):
    asyncio.run(run(args))


async def run(args):
    global TIMEOUT_PER_PAGE
    global MAX_WORKERS
    global URLs_FILE
    global ARIA2C_FILE

    # Set from CLI args
    TIMEOUT_PER_PAGE = int(args.timeout)
    MAX_WORKERS = int(args.max_workers)
    URLs_FILE = args.urls_file
    ARIA2C_FILE = args.aria2c_file

    with open(URLs_FILE, "r", encoding="utf-8") as urls:
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

        if MAX_WORKERS > 1:
            tasks = Queue()
            workers = [
                asyncio.create_task(worker_func(tasks), name=f"worker_{i+1}")
                for i in range(MAX_WORKERS)
            ]

            for url in urls:
                await tasks.put(extract_url_ctx(ctx, url, ARIA2C_FILE))
            await tasks.join()

            for worker in workers:
                worker.cancel()
        else:
            page = await ctx.new_page()
            with logging_redirect_tqdm():
                for url in tqdm(urls):
                    await extract_url_page(page, url, ARIA2C_FILE)

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

import os
import asyncio
import urllib
import urllib.parse
from asyncio import Queue
from collections.abc import Coroutine

from playwright.async_api import async_playwright, Page, BrowserContext

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"

TIMEOUT_PER_PAGE = int(os.environ.get("TIMEOUT_PER_PAGE", 5_000))
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 2))


async def worker_func(tasks: Queue[Coroutine]):
    while True:
        coro = await tasks.get()
        await coro
        tasks.task_done()


async def extract_url_page(page: Page, url: str, close_page=False):
    await page.goto(url)

    download_loc = page.locator("button.link-button")
    async with page.expect_download(timeout=TIMEOUT_PER_PAGE) as download_info:
        await download_loc.click()
        await download_loc.click()

    download = await download_info.value
    await download.cancel()
    if close_page:
        await page.close()

    filename = url.split("#")[-1]
    print(download.url, f"    out={filename}", "    continue=true", sep="\n")


async def extract_url_ctx(ctx: BrowserContext, url: str):
    page = await ctx.new_page()
    await extract_url_page(page, url, close_page=True)


async def main():
    with open("urls.txt", "r", encoding="utf-8") as urls:
        urls = [url for url in urls.read().split("\n") if url]
    async with async_playwright() as playwright:

        def on_page(page: Page):
            url = page.url
            parsed = urllib.parse.urlparse(url)

            if parsed.hostname is None:
                return
            if parsed.hostname != "fuckingfast.co":
                return page.close()

        browser = await playwright.chromium.launch(headless=False)
        ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
        ctx.on("page", on_page)
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")

        if MAX_WORKERS > 1:
            tasks = Queue()
            workers = [
                asyncio.create_task(worker_func(tasks)) for _ in range(MAX_WORKERS)
            ]

            for url in urls:
                await tasks.put(extract_url_ctx(ctx, url))
            await tasks.join()

            for worker in workers:
                worker.cancel()
        else:
            page = await ctx.new_page()
            for url in urls:
                await extract_url_page(page, url)

        await ctx.tracing.stop(path="trace.zip")
        await ctx.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

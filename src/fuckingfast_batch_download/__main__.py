import sys
import asyncio
import urllib
import urllib.parse

from playwright.async_api import async_playwright, Page

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"

TIMEOUT_PER_PAGE = 5_000


async def extract_url_to_aria2(page: Page, url: str):
    await page.goto(url)

    download_loc = page.locator("button.link-button")
    async with page.expect_download(timeout=TIMEOUT_PER_PAGE) as download_info:
        await download_loc.click()
        await download_loc.click()

    download = await download_info.value
    await download.cancel()

    filename = url.split("#")[-1]
    print(download.url, f"     out={filename}", "    continue=true", sep="\n")
    sys.stdout.flush()


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

        browser = await playwright.chromium.launch(headless=True)
        ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
        ctx.on("page", on_page)
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")

        page = await ctx.new_page()

        for url in urls:
            await extract_url_to_aria2(page, url)

        await ctx.tracing.stop(path="trace.zip")
        await ctx.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

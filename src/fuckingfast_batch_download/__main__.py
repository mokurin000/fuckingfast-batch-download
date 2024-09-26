import asyncio
import urllib
import urllib.parse

from playwright.async_api import async_playwright, Page, BrowserContext

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"

TIMEOUT_PER_PAGE = 5_000


async def extract_url_to_aria2(ctx: BrowserContext, url: str):
    page = await ctx.new_page()
    await page.goto(url)

    download_loc = page.locator("button.link-button")
    async with page.expect_download(timeout=TIMEOUT_PER_PAGE) as download_info:
        await download_loc.click()
        await download_loc.click()

    download = await download_info.value
    await download.cancel()
    await page.close()

    print(download.url, f"     out={url.split("#")[-1]}", sep="\n")


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
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")
        ctx.on("page", on_page)

        await asyncio.gather(*(extract_url_to_aria2(ctx, url) for url in urls))

        await ctx.tracing.stop(path="trace.zip")
        await ctx.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

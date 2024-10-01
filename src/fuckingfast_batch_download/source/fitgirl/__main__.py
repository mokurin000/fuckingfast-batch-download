import asyncio
import argparse

import xdialog
from playwright.async_api import (
    async_playwright,
    BrowserContext,
    Error as PlaywrightError,
)


async def scrap(ctx: BrowserContext, url: str):
    page = await ctx.new_page()
    await page.goto(url)

    links_loc = page.get_by_text("Filehoster: FuckingFast")
    links = await links_loc.all()
    if not links:
        xdialog.error(message="ERROR: fuckingfast source not found!")
        return
    if len(links) > 1:
        xdialog.error(message="ERROR: please paste url of single game!")
        return

    jump = links.pop()
    await page.goto(await jump.get_attribute("href"))

    first_url_loc = page.locator("div#plaintext ul li:nth-child(1) a")
    await first_url_loc.wait_for(timeout=0, state="attached")
    url_loc = page.locator("div#plaintext ul li a")
    urls = await url_loc.all_inner_texts()

    output = xdialog.save_file(
        title="URL list file", filetypes=[("Text files", "*.txt")]
    )

    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(urls) + "\n")


async def run(args):
    async with async_playwright() as playwright:
        if not args.skip_edge:
            try:
                browser = await playwright.chromium.launch(
                    headless=True, channel="msedge"
                )
            except PlaywrightError:
                xdialog.warning(message="Edge was not found, fallback to Chromium")
                browser = await playwright.chromium.launch(headless=True)
        else:
            browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.tracing.start(name="fitgirl scrap", title="fitgirl scrap")
        await scrap(ctx=context, url=args.url)
        await context.tracing.stop(path="trace-fg.zip")
        await context.close()
        await browser.close()


def main(args):
    asyncio.run(run(args))


def _main():
    parser = argparse.ArgumentParser(
        description="Scrap fitgirl fuckingfast links and save to a file."
    )
    parser.add_argument("url", type=str, help="The URL to scrap")
    parser.add_argument("--skip-edge", type=bool, help="never launch msedge")
    args = parser.parse_args()

    main(args)


if __name__ == "__main__":
    _main()

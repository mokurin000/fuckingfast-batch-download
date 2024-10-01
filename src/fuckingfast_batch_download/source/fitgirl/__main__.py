import asyncio
import argparse

import xdialog
from playwright.async_api import async_playwright, BrowserContext


async def scrap(ctx: BrowserContext, url: str):
    page = await ctx.new_page()
    await page.goto(url)

    links_loc = page.get_by_text("Filehoster: FuckingFast")
    links = await links_loc.all()
    if not links:
        xdialog.error("ERROR: fuckingfast source not found!")
        return
    if len(links) > 1:
        xdialog.error("ERROR: please paste url of single game!")
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
    args = parser.parse_args()

    main(args.url)


if __name__ == "__main__":
    _main()

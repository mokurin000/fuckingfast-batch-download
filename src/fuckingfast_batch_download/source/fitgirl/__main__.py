import asyncio
import argparse
import logging

import xdialog
from playwright.async_api import (
    async_playwright,
    BrowserContext,
    Error as PlaywrightError,
)




async def scrap(ctx: BrowserContext, url: str, timeout: float):
    page = await ctx.new_page()
    logging.info(f"Navigating to {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=timeout)

    links_loc = page.get_by_text("Filehoster: FuckingFast")
    links = await links_loc.all()
    if not links:
        message = "ERROR: fuckingfast source not found!"
        logging.error(message)
        xdialog.error(message=message)
        return
    if len(links) > 1:
        message = "ERROR: please paste url of single game!"
        logging.error(message)
        xdialog.error(message=message)
        return

    hoster_links_elem = await page.locator("ul li div a").all()
    hoster_links = await asyncio.gather(
        *(tag.get_attribute("href") for tag in hoster_links_elem)
    )
    fuckingfast_links = [
        link for link in hoster_links if link.startswith("https://fuckingfast.co")
    ]
    output = xdialog.save_file(
        title="URL list file", filetypes=[("Text files", "*.txt")]
    )

    if not output:
        message = "User cancellation"
        logging.info(message)
        xdialog.info(message=message)
        return
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(fuckingfast_links) + "\n")


async def run(args):
    headless = not args.no_headless
    async with async_playwright() as playwright:
        if not args.skip_edge:
            try:
                browser = await playwright.chromium.launch(
                    headless=headless, channel="msedge"
                )
            except PlaywrightError:
                xdialog.warning(message="Edge was not found, fallback to Chromium")
                browser = await playwright.chromium.launch(headless=headless)
        else:
            browser = await playwright.chromium.launch(headless=headless)
        context = await browser.new_context()
        await context.tracing.start(name="fitgirl scrap", title="fitgirl scrap")
        try:
            await scrap(ctx=context, url=args.url, timeout=args.timeout)
        except PlaywrightError as e:
            xdialog.error(title="Scrap error", message=f"{e}")
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
    parser.add_argument(
        "--timeout",
        type=float,
        default=0,
        help="timeout (millisecond) for waiting page to load",
    )
    parser.add_argument("--skip-edge", help="never launch msedge", action="store_true")
    parser.add_argument(
        "--no-headless", help="disable headless mode", action="store_true"
    )
    args = parser.parse_args()

    main(args)


if __name__ == "__main__":
    _main()

from threading import Thread

import xdialog
import cli2gui

from fuckingfast_batch_download.source.fitgirl.__main__ import main, _main

THREAD: Thread = None


def wrapper(args):
    global THREAD

    if THREAD is not None and THREAD.is_alive():
        xdialog.info(message="Task already running")
        return
    THREAD = Thread(target=main, args=(args,))
    THREAD.start()


deco = cli2gui.Cli2Gui(
    run_function=wrapper,
    gui="dearpygui",
    program_name="FitGirl Scraper",
    program_description="A GUI for scraping FitGirl FuckingFast links and saving them to a file.",
    auto_enable=True,
)

gui = deco(_main)()

if __name__ == "__main__":
    gui()

from threading import Thread

import xdialog
from cli2gui import Cli2Gui

from fuckingfast_batch_download.__main__ import blocking_run, main

THREAD: Thread = None


def wrapper(args):
    global THREAD

    if THREAD is not None and THREAD.is_alive():
        xdialog.info(message="Task already running")
        return
    THREAD = Thread(target=blocking_run, args=(args,))
    THREAD.run()


# Set up Cli2Gui
decorator_function = Cli2Gui(
    gui="freesimplegui",
    run_function=wrapper,
    auto_enable=True,
    program_name="fuckingfast-fetch",
)

# GUI entrypoint
gui = decorator_function(main)

if __name__ == "__main__":
    gui()

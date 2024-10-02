from cli2gui import Cli2Gui

from fuckingfast_batch_download.__main__ import blocking_run, main

# Set up Cli2Gui
decorator_function = Cli2Gui(
    run_function=blocking_run,
    auto_enable=True,
    program_name="fuckingfast-fetch",
)

# GUI entrypoint
gui = decorator_function(main)

if __name__ == "__main__":
    gui()

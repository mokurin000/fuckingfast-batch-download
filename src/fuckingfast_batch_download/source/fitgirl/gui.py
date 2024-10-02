import cli2gui

from fuckingfast_batch_download.source.fitgirl.__main__ import main, _main


deco = cli2gui.Cli2Gui(
    run_function=main,
    gui="freesimplegui",
    program_name="FitGirl Scraper",
    program_description="A GUI for scraping FitGirl FuckingFast links and saving them to a file.",
    auto_enable=True,
)

gui = deco(_main)()

if __name__ == "__main__":
    gui()

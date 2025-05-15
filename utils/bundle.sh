uv sync

project="fuckingfast_batch_download"

uv run pyinstaller --optimize 2 -D -n scrap-gui \
    --noconsole \
    --clean --noconfirm \
    --hidden-import=tkinter --collect-data=cli2gui \
    src/$project/ui/scrap_gui.py
uv run pyinstaller --optimize 2 -D -n extract-gui \
    --clean --noconfirm \
    --hidden-import=tkinter --collect-data=cli2gui \
    src/$project/ui/main_gui.py

rm *.spec

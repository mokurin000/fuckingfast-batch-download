uv sync

export PLAYWRIGHT_BROWSERS_PATH=0
project="fuckingfast_batch_download"

uv run playwright install chromium

uv run pyinstaller --optimize 2 -D -n scrap-gui-chromium \
    --noconsole \
    --clean --noconfirm \
    --hidden-import=tkinter --collect-data=cli2gui \
    src/$project/ui/scrap_gui.py
uv run pyinstaller --optimize 2 -D -n extract-gui-chromium \
    --clean --noconfirm \
    --hidden-import=tkinter --collect-data=cli2gui \
    src/$project/ui/main_gui.py

# reuse library
mv ./dist/scrap-gui-chromium/scrap-gui-chromium* ./dist/extract-gui-chromium
rm -rf 'dist/scrap-gui-chromium'
rm *.spec

uv sync
uv add pyinstaller
micromamba install pyinstaller -y

pip install -e .

$ENV:PLAYWRIGHT_BROWSERS_PATH = 0

$CLEAN_OPT = '--clean', '--noconfirm'
$HIDE_WINDOW = '--noconsole'
$HIDDEN_DEPS = '--hidden-import=tkinter', '--collect-data=cli2gui'

playwright install chromium

pyinstaller @HIDDEN_DEPS --optimize 2 -D -n scrap-gui-chromium @CLEAN_OPT $HIDE_WINDOW src/$project/ui/scrap_gui.py
pyinstaller @HIDDEN_DEPS --optimize 2 -D -n extract-gui-chromium @CLEAN_OPT src/$project/ui/main_gui.py

if ($env:REMOVE_ENV) {
    micromamba env remove -n $env_name -y
}

# reuse library
Move-Item .\dist\scrap-gui-chromium\scrap-gui-chromium.exe dist\extract-gui-chromium
Remove-Item -Recurse -Force dist\scrap-gui-chromium

# Optional, comment this to debug pyinstaller spec.
Remove-Item *.spec

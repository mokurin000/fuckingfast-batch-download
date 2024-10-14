$project = "fuckingfast_batch_download"
micromamba create -n $project-chromium -y "python<3.12"
micromamba activate $project-chromium
micromamba install pyinstaller -y
micromamba run pip install -e .

$ENV:PLAYWRIGHT_BROWSERS_PATH = 0
$ENV:HTTPS_PROXY = "http://127.0.0.1:7890"

$CLEAN_OPT = '--clean', '--noconfirm'
$HIDE_WINDOW = '--noconsole'
$HIDDEN_DEPS = '--hidden-import=tkinter', '--collect-data=cli2gui'

micromamba run playwright install chromium

micormamba run pyinstaller @HIDDEN_DEPS --optimize 2 -D -n scrap-gui-chromium @CLEAN_OPT $HIDE_WINDOW src/$project/source/fitgirl/gui.py
micormamba run pyinstaller @HIDDEN_DEPS --optimize 2 -D -n extract-gui-chromium @CLEAN_OPT src/$project/gui.py

# reuse library
Move-Item .\dist\scrap-gui-chromium\scrap-gui-chromium.exe dist\extract-gui-chromium
Remove-Item -Recurse -Force dist\scrap-gui-chromium

# Optional, comment this to debug pyinstaller spec.
Remove-Item *.spec

micromamba env remove -n $project-chromium -y
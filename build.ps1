$project = "fuckingfast_batch_download"
micromamba create -n $project "python<3.12"
micromamba activate $project

pip install -e .
pip install pyinstaller

$ENV:HTTPS_PROXY = "http://127.0.0.1:7890"

$CLEAN_OPT = '--clean', '--noconfirm'
$HIDE_WINDOW = '--noconsole'
$HIDDEN_DEPS = '--hidden-import=tkinter', '--collect-data=cli2gui'

pyinstaller @HIDDEN_DEPS --optimize 2 -D -n scrap-gui @CLEAN_OPT $HIDE_WINDOW src/$project/source/fitgirl/gui.py
pyinstaller @HIDDEN_DEPS --optimize 2 -D -n extract-gui @CLEAN_OPT src/$project/gui.py

# reuse library
Move-Item .\dist\scrap-gui\scrap-gui.exe dist\extract-gui
Remove-Item -Recurse -Force dist\scrap-gui

# Optional, comment this to debug pyinstaller spec.
Remove-Item *.spec

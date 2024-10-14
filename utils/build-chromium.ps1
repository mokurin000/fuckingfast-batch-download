$project = "fuckingfast_batch_download"
$env_name = $project + "-pyinstaller-chromium"

micromamba create -n $env_name -y "python<3.12"
micromamba activate $env_name
micromamba install pyinstaller -y
micromamba run pip install -e .

$ENV:PLAYWRIGHT_BROWSERS_PATH = 0
$proxy_info = (Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings')
if ($proxy_info.proxyEnable) {
    $ENV:HTTPS_PROXY = "http://" + $proxy_info.proxyServer
}

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

micromamba env remove -n $env_name -y
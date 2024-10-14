$project = "fuckingfast_batch_download"
$env_name = $project + "-pyinstaller-chromium"

if ($env:FORCE_RECREATION) {
    micromamba create -n $env_name -y "python<3.12"
}
else {
    micromamba create -n $env_name "python<3.12"
}

micromamba activate $env_name
micromamba install pyinstaller -y

pip install -e .

$ENV:PLAYWRIGHT_BROWSERS_PATH = 0
$proxy_info = (Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings')
if ($proxy_info.proxyEnable) {
    $ENV:HTTPS_PROXY = "http://" + $proxy_info.proxyServer
}

$CLEAN_OPT = '--clean', '--noconfirm'
$HIDE_WINDOW = '--noconsole'
$HIDDEN_DEPS = '--hidden-import=tkinter', '--collect-data=cli2gui'

playwright install chromium

pyinstaller @HIDDEN_DEPS --optimize 2 -D -n scrap-gui-chromium @CLEAN_OPT $HIDE_WINDOW src/$project/ui/scrap_gui.py
pyinstaller @HIDDEN_DEPS --optimize 2 -D -n extract-gui-chromium @CLEAN_OPT src/$project/ui/main_gui.py

if ($env:SKIP_CREATE_ENV) {
    micromamba env remove -n $env_name -y
}

# reuse library
Move-Item .\dist\scrap-gui-chromium\scrap-gui-chromium.exe dist\extract-gui-chromium
Remove-Item -Recurse -Force dist\scrap-gui-chromium

# Optional, comment this to debug pyinstaller spec.
Remove-Item *.spec

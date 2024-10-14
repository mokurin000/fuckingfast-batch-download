$project = "fuckingfast_batch_download"
$env_name = $project + "-nuitka-chromium"

micromamba create -n $env_name -y "python<3.12"
micromamba activate $env_name
micromamba install -c conda-forge nuitka ordered-set -y

pip install -e .

$ENV:PLAYWRIGHT_BROWSERS_PATH = 0
$proxy_info = (Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings')
if ($proxy_info.proxyEnable) {
    $ENV:HTTPS_PROXY = "http://" + $proxy_info.proxyServer
}

playwright install chromium

$META = '--product-name=FuckingFast Batch Download', '--company-name=mokurin000', '--file-version=0.1.0.0'
$OPTIMIZE = "--lto=yes", "--jobs=20"
$FIX_TK = "--enable-plugin=tk-inter"

$nuitka_output = "nuitka-chromium-dist"
nuitka @META @OPTIMIZE $FIX_TK --standalone --output-dir=$nuitka_output --main=src\fuckingfast_batch_download\ui\main_gui.py
nuitka --windows-console-mode=attach @META @OPTIMIZE $FIX_TK --standalone --output-dir=$nuitka_output --main=src\fuckingfast_batch_download\ui\scrap_gui.py

# Copy playwright
$result_path = $nuitka_output + "/main_gui.dist/playwright"
mkdir -Force $result_path
$playwright_path = (python -c 'from importlib.resources import files; print(files("playwright"))')
Copy-Item -Recurse -Force -Path $playwright_path"/driver" -Destination $result_path

micromamba env remove -n $env_name -y

# Move scrap-gui to main-gui directory
Move-Item $nuitka_output/scrap_gui.dist/scrap_gui.exe $nuitka_output/main_gui.dist
Remove-Item -Recurse -Force $nuitka_output/scrap_gui.dist

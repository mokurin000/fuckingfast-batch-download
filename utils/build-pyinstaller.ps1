$project = "fuckingfast_batch_download"
$env_name = $project + "-pyinstaller"

if ($env:FORCE_RECREATION) {
    micromamba create -n $env_name -y "python<3.12"
}
else {
    $existing_envs = micromamba env list --json | ConvertFrom-Json | Select-Object -ExpandProperty envs | ForEach-Object { (Split-Path $_ -Leaf) }
    if ($existing_envs -notcontains $env_name) {
        micromamba create -n $env_name -y "python<3.12"
    }
}

micromamba activate $env_name
micromamba install pyinstaller -y

pip install -e .

$CLEAN_OPT = '--clean', '--noconfirm'
$HIDE_WINDOW = '--noconsole'
$HIDDEN_DEPS = '--hidden-import=tkinter', '--collect-data=cli2gui'

pyinstaller @HIDDEN_DEPS --optimize 2 -D -n scrap-gui @CLEAN_OPT $HIDE_WINDOW src/$project/ui/scrap_gui.py
pyinstaller @HIDDEN_DEPS --optimize 2 -D -n extract-gui @CLEAN_OPT src/$project/ui/main_gui.py

if ($env:REMOVE_ENV) {
    micromamba env remove -n $env_name -y
}

# reuse library
Move-Item .\dist\scrap-gui\scrap-gui.exe dist\extract-gui
Remove-Item -Recurse -Force dist\scrap-gui

# Optional, comment this to debug pyinstaller spec.
Remove-Item *.spec

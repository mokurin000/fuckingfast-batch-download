$project = "fuckingfast_batch_download"
$env_name = $project + "-nuitka"

micromamba create -n $env_name -y "python<3.12"
micromamba activate $env_name
micromamba install -c conda-forge nuitka ordered-set -y

pip install -e .

$META = '--product-name="FuckingFast Batch Download"', '--company-name=mokurin000', '--file-version=0.1.0.0'
$OPTIMIZE = "--lto=yes", "--jobs=20"


$nuitka_output = "nuitka-dist"
nuitka @META @OPTIMIZE --standalone --output-dir=$nuitka_output --main=src\fuckingfast_batch_download\gui.py
$result_path = $nuitka_output + "/gui.dist/playwright"
mkdir -Force $result_path

$playwright_path = (python -c 'from importlib.resources import files; print(files("playwright"))')
Copy-Item -Recurse -Force -Path $playwright_path"/driver" -Destination $result_path

micromamba env remove -n $env_name -y

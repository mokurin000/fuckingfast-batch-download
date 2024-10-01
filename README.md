# fuckingfast-batch-download

Extract direct link from `fuckingfast.co`, to semi-automate download large games from fitgirl.

## Installtion

### Via releases (Recommended)

[Download]: https://github.com/mokurin000/fuckingfast-batch-download/releases/tag/nightly

[Download] pre-built windows release from releases.

### Via pipx

```bash
# Install
pipx install https://github.com/mokurin000/fuckingfast-batch-download
# Update
pipx upgrade feeluown --include-injected
```

### Local install (for development)

```bash
# Clone
git clone --depth 1 https://github.com/mokurin000/fuckingfast-batch-download.git
cd fuckingfast-batch-download
# Create virtual environment
python3 -m venv .venv
# Activate virtual environment
. .venv/bin/activate # for mac/linux
. .venv/Scripts/activate # for windows powershell
# Install
python3 -m pip install -e .
# Update
git pull
```

## Usage

```bash
# Scrap fuckingfast.co urls
python3 -m fuckingfast_batch_download.source.fitgirl.gui
# Extract direct download links
python3 -m fuckingfast_batch_download.gui
# Download & Enjoy!
aria2c -x 4 -s 1 --save-session=aria2.session -i output.txt 
```

# fuckingfast-batch-download

Extract direct link from `fuckingfast.co`, to semi-automate download large games from fitgirl.

## Installtion

### Via releases (Recommended)

[Download]: https://github.com/mokurin000/fuckingfast-batch-download/releases/tag/nightly

[Download] pre-built windows release from releases.

Hint: to use them as CLI tool, add `--disable-cli2gui` to your arguments.

### Via uv

```bash
uv tool add https://github.com/mokurin000/fuckingfast-batch-download
```

### Local install (for development)

```bash
# Clone
git clone --depth 1 https://github.com/mokurin000/fuckingfast-batch-download.git
cd fuckingfast-batch-download
# Update
git pull
```

## Usage

```bash
# Scrap fuckingfast.co urls
uv run fitgirl-scrape-gui
# Extract direct download links
uv run fuckingfast-extract-gui
# Download & Enjoy!
aria2c -x 4 -s 1 --save-session=aria2.session -i output.txt 
```

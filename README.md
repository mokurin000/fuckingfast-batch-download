# fuckingfast-batch-download

Extract direct link from `fuckingfast.co`, to semi-automate download large games from fitgirl.

## Installtion

```bash
pip3 install -e .
```

## Usage

```bash
# First paste `fetch-links/sites/fitgirl.js` to your web-devtools console
# Copy the result array with 'Copy Object'
python3 fetch-links/links.py > urls.txt
# Scrap direct download links
python3 -m fuckingfast_batch_download
# ...
# Download & Enjoy!
aria2c -x 4 -s 1 -i output.txt --save-session=aria2.session
```

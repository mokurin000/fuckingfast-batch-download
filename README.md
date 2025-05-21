# fuckingfast-batch-download

> A [much more lightwright version](https://github.com/mokurin000/fitgirl-ddl) in Rust is out!
>
> It comes with less than 2 MiB binary size, runs faster!

Extract direct link from `fuckingfast.co`, to semi-automate download large games from fitgirl.

## Usage

1. First copy an URL from [fitgirl-repacks.site](https://fitgirl-repacks.site/)
> the URL is in the form like `https://fitgirl-repacks.site/xxxx-xxxx-xxxxx/`
> 
> for the games in the **popular repacks**, right-click the image and click `Copy URL`.
>
> for the ones in gallery, right-click the uppercased game title, then `Copy URL`.
2. Run `scrap-gui-chromium`
 - Paste the URL into `Url` box
 - `Select/Create` the `Output File`
 - Click `Run`
 - Wait for a popup "Saved url file!"
3. Run `extract-gui-chromium.exe`
 - Select `Urls File` as you created in step 2
 - `Select/Create` `aria2c File`, it's actually an aria2 input file.
 > DO NOT overwite the text file generated in step 2!
 - Click `Run`
 - Wait for the progress bar in the terminal
 - Once it is completed, click `Exit`.
4. Open the text file generated in step 3
   - copy all of its contents
   - open [Motrix](https://motrix.app/)
   - Click the `+` button
     - ps: this should paste the aria2 inputs automatically
   - Set `Splits` to 1
   - Click `Submit`

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

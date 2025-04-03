const urls = [
    "https://fitgirl-repacks.site/inayah-life-after-gods/",
    "https://fitgirl-repacks.site/twilight-monk/",
    "https://fitgirl-repacks.site/themis/",
    "https://fitgirl-repacks.site/super-monkey-ball-banana-rumble/",
    "https://fitgirl-repacks.site/within-the-cosmos/",
];

for $url in $urls {
    let name = $url | str replace "https://fitgirl-repacks.site/" "" | str replace "/" "";
    uv run python -m fuckingfast_batch_download.source.fitgirl --skip-edge --output-filename ($name + ".txt") $url
}
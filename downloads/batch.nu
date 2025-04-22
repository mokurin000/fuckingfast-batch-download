const urls = [
    https://fitgirl-repacks.site/artisan-td/
    https://fitgirl-repacks.site/short-snow/
];

for $url in $urls {
    let name = $url | str replace "https://fitgirl-repacks.site/" "" | str replace "/" "";
    let url_file = ($name + ".txt");
    let aria2_file = ($name + "_input.txt");
    uv run python -m fuckingfast_batch_download.source.fitgirl --output-file $url_file --no-saved-dialog $url
    uv run python -m fuckingfast_batch_download $url_file $aria2_file
}
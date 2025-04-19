#!/bin/bash
inotifywait -m -e moved_to --format "%f" "/usr/local/apache2/htdocs/hls" | while read FILE; do
    if [[ "$FILE" == *.ts ]]; then
        sleep(0.5)
        IN="/usr/local/apache2/htdocs/hls/$FILE"
        OUT="/usr/local/apache2/out/${FILE%.ts}.mp3"
        ffmpeg -i "$IN" -q:a 0 -map a "$OUT"
    fi
done


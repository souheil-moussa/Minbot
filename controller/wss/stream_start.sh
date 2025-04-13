#!/bin/bash
echo "stream started"
ffmpeg -f pulse -i plughw:0,0 -ac 1 -ar 48000 -c:a aac -b:a 128k -f hls -hls_time 0.5 -hls_list_size 5 -hls_flags delete_segments http://$1:8080/hls/audio.m3u


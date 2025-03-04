#!/bin/bash
echo "stream started"
ffmpeg -f alsa -i plughw:2,0 -ac 1 -ar 44100 -c:a aac -b:a 64k -f hls -hls_time 0.5 -hls_list_size 5 -hls_flags delete_segments http://192.168.1.200:8080/hls/audio.m3u


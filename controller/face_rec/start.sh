#!/bin/bash
libcamera-vid -t 30000 --width 1280 --height 720 --framerate 30 -o output.mp4 &
source /home/souheil/Desktop/FYP/face/bin/activate
python scan2.py 
python face_rec.py 

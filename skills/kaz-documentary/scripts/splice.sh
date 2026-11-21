#!/usr/bin/env bash
# Replace frames [start_frame, end_frame) of board.mp4 with insert.mp4 (same size/fps).
# Usage: splice.sh board.mp4 insert.mp4 start_frame end_frame out.mp4
set -e
ffmpeg -loglevel error -y -i "$1" -i "$2" -filter_complex \
 "[0:v]trim=end_frame=$3,setpts=PTS-STARTPTS[a];[0:v]trim=start_frame=$4,setpts=PTS-STARTPTS[c];[a][1:v][c]concat=n=3:v=1[v]" \
 -map "[v]" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$5"

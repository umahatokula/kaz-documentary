#!/usr/bin/env bash
# Usage: mix_and_mux.sh video.mp4 voiceover.(mp3|wav) bed.wav out.mp4
# Ducks the bed under the voice, normalises to -14 LUFS, shareable H.264 (CRF 24).
set -e
ffmpeg -loglevel error -y -i "$1" -i "$2" -i "$3" -filter_complex \
 "[1:a]aresample=48000,asplit=2[v1][v2];[2:a]aformat=channel_layouts=mono[b];[b][v1]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[bd];[bd][v2]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]" \
 -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 24 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$4"

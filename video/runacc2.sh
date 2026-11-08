#!/bin/bash
set -e
K=$1; cd /home/claude
export BATCH=${BATCH:-accdata4}
export FMTS=${FMTS:-fmts2}
N=$(python3 -c "
import importlib, os
fmts=importlib.import_module(os.environ.get('FMTS','fmts'))
D=importlib.import_module(os.environ['BATCH'])
c=D.cfg('$K'); ph,sl,T=fmts.build(c); print(len(fmts.frames(ph)))")
rm -rf "fr_$K"; mkdir -p "fr_$K"
python3 accrender.py "$K" 0 "$N" "fr_$K" >/dev/null
G=$(ls "fr_$K" | wc -l); [ "$G" -eq "$N" ] || { echo "НЕ ХВАТАЕТ КАДРОВ $K $G/$N"; exit 1; }
python3 accaudio.py "$K" >/dev/null
ffmpeg -y -framerate 30 -i "fr_$K/f_%05d.jpg" -c:v libx264 -preset faster \
  -pix_fmt yuv420p -r 30 -crf 21 "/tmp/$K.v.mp4" -loglevel error
ffmpeg -y -i "/tmp/$K.v.mp4" -i "$K.wav" -c:v copy -c:a aac -b:a 192k -ac 2 \
  -shortest "/mnt/user-data/outputs/$K.mp4" -loglevel error
rm -rf "fr_$K" "/tmp/$K.v.mp4" "$K.wav"
echo "ОК $K $(ffprobe -v error -show_entries format=duration -of csv=p=0 /mnt/user-data/outputs/$K.mp4)с"

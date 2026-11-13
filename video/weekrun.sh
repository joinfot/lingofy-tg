#!/bin/bash
# Собирает дни по одному: нарезка перезаписывает voice_real.json,
# поэтому рендер каждого дня идёт сразу за своей нарезкой.
cd /home/claude
for d in "$@"; do
  echo "=========== день $d"
  BATCH=accdata$d VDUR=vdur$d FMTS=fmts3 python3 vcut.py cut$d >/dev/null || { echo "НАРЕЗКА УПАЛА $d"; continue; }
  BATCH=accdata$d FMTS=fmts3 bash allacc2.sh 2>&1 | tail -3
  BATCH=accdata$d FMTS=fmts3 python3 vcheck5.py 2>&1 | tail -2
done

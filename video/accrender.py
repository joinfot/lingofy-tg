# -*- coding: utf-8 -*-
"""Рендер кадров одного ролика: accrender.py КЛЮЧ СТАРТ СКОЛЬКО ПАПКА

Пишет f_00000.jpg и дальше по номерам. Нумерация сквозная от начала ролика,
поэтому срезы можно считать в несколько процессов и просто сложить в одну
папку — ffmpeg соберёт их по именам.
"""
import importlib
import os
import sys


KEY = sys.argv[1]
START = int(sys.argv[2])
COUNT = int(sys.argv[3])
OUT = sys.argv[4]

D = importlib.import_module(os.environ.get("BATCH", "accdata2"))
fmts = importlib.import_module(os.environ.get("FMTS", "fmts"))
cfg = D.cfg(KEY)
phases, slots, T = fmts.build(cfg)
seq = fmts.frames(phases)

os.makedirs(OUT, exist_ok=True)
end = min(START + COUNT, len(seq))
for n in range(START, end):
    kind, i, k = seq[n]
    img = fmts.draw(cfg, kind, i, k)
    img.convert("RGB").save(f"{OUT}/f_{n:05d}.jpg", quality=93, optimize=False)
    if (n - START) % 120 == 0:
        print(f"{KEY} {n - START}/{end - START}", flush=True)
print(f"{KEY} готово {end - START} кадров", flush=True)

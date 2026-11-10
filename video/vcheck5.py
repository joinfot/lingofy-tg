# -*- coding: utf-8 -*-
"""Приёмка партии: vcheck5.py

Сверяет каждый готовый mp4 с расчётом: длительность, наличие звука, и то,
что в дорожке действительно есть речь, а не одна музыка.

Повод завести это отдельно: в этой партии три файла вышли ровно вполовину
короче и на вид были целые. Глазами такое не ловится — только сверкой с
расчётной длиной.
"""
import importlib
import json
import os
import subprocess
import sys

OUT = "/mnt/user-data/outputs"
TOL = 0.25

D = importlib.import_module(os.environ.get("BATCH", "accdata5"))
fmts = importlib.import_module(os.environ.get("FMTS", "fmts2"))


def probe(path, *args):
    return subprocess.run(["ffprobe", "-v", "error", *args, "-of", "csv=p=0",
                           path], capture_output=True, text=True).stdout.strip()


def volumes(path):
    # volumedetect печатает итог на уровне info: с -v error его не видно
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "info", "-i", path,
                        "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    out = {}
    for line in r.splitlines():
        for tag in ("mean_volume", "max_volume"):
            if tag in line:
                out[tag] = float(line.split(":")[-1].replace("dB", "").strip())
    return out


bad = []
for v in D.V:
    k = v["key"]
    p = f"{OUT}/{k}.mp4"
    if not os.path.exists(p):
        print(f"  {k:18s} НЕТ ФАЙЛА")
        bad.append(k)
        continue
    _, _, T = fmts.build(D.cfg(k))
    got = float(probe(p, "-show_entries", "format=duration") or 0)
    astr = probe(p, "-select_streams", "a:0", "-show_entries",
                 "stream=codec_name,channels")
    vol = volumes(p)
    note = []
    if abs(got - T) > TOL:
        note.append(f"длина {got:.2f} вместо {T:.2f}")
    if not astr:
        note.append("нет звуковой дорожки")
    # одна музыка без речи звучит заметно тише: голос поднят до 0.82
    if vol.get("max_volume", -99) < -3.0:
        note.append(f"тихо, max {vol.get('max_volume')}dB — речь не легла?")
    mark = "ок" if not note else "; ".join(note).upper()
    print(f"  {k:18s} {got:6.2f}с (ждём {T:6.2f})  "
          f"{astr or '-':14s} max {vol.get('max_volume', 0):6.1f}dB  {mark}")
    if note:
        bad.append(k)

print()
if bad:
    print("перебрать заново:", " ".join(bad))
    sys.exit(1)
print(f"вся партия принята: {len(D.V)} роликов")

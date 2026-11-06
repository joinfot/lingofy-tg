# -*- coding: utf-8 -*-
"""Разбор скачанной озвучки: vcut.py ПАПКА

Делает три вещи.

1. Опознаёт файлы. Имена у них одинаковые и отличаются только номером,
   поэтому порядок номеров сопоставляется с порядком генерации, а потом
   КАЖДЫЙ файл сверяется по длительности с эталоном от ElevenLabs. Если
   хоть один не сошёлся — работа останавливается: лучше ничего, чем ролик
   с чужим голосом. Один раз такое уже проехало незамеченным.

2. Режет каждую дорожку на реплики по паузам, тремя способами, и берёт тот,
   что лучше ложится на текст.

3. Пишет куски в voice_a/ и настоящие длительности в voice_real.json —
   по ним потом пересчитываются длины фаз, чтобы речь нигде не обрывалась.
"""
import importlib
import json
import os
import re
import sys

import numpy as np

import fmts
import vdur2
import ysplit

SRC = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads"
PAD = 0.07          # местный mp3 чуть длиннее из-за добивки кадра
OUT = "/home/claude/voice_a"
D = importlib.import_module(os.environ.get("BATCH", "accdata2"))


def num(p):
    m = re.findall(r"(\d+)", os.path.basename(p))
    return int(m[-1]) if m else 10 ** 9


files = [os.path.join(SRC, f) for f in os.listdir(SRC)
         if f.lower().endswith((".mp3", ".wav", ".m4a"))]
files.sort(key=lambda p: (num(p), p))

if len(files) != len(vdur2.ORDER):
    print(f"файлов {len(files)}, а дорожек {len(vdur2.ORDER)} — не берусь")
    sys.exit(1)

print("сверяю файлы с эталоном")
loaded, bad = [], []
for path, (key, lang, want) in zip(files, vdur2.ORDER):
    x = ysplit.load(path)
    got = len(x) / ysplit.SR
    ok = abs(got - want) <= PAD
    loaded.append((key, lang, x, got))
    mark = "ок" if ok else "НЕ СХОДИТСЯ"
    print(f"  {os.path.basename(path):28s} -> {key}|{lang}  "
          f"{got:6.2f} при ожидаемых {want:6.2f}  {mark}")
    if not ok:
        bad.append((os.path.basename(path), key, lang, got, want))

if bad:
    print("\nпорядок файлов не совпал с порядком генерации — ничего не режу.")
    for b in bad:
        print("   ", b)
    sys.exit(1)

# тексты реплик берутся из той же сборки, что и кадры
texts = {}
for v in D.V:
    c = D.cfg(v["key"])
    ph, sl, T = fmts.build(c)
    for lang in ("ru", "de"):
        texts[f"{v['key']}|{lang}"] = [t for (_, l, t) in sl if l == lang]

os.makedirs(OUT, exist_ok=True)
real, weak = {}, []
print("\nрежу по паузам")
for key, lang, x, got in loaded:
    seq = texts[f"{key}|{lang}"]
    how, cuts, score = ysplit.best_of(x, seq)
    if cuts is None:
        print(f"  {key}|{lang}: не разрезалось на {len(seq)} — пропускаю")
        weak.append((key, lang, 0.0))
        continue
    np.savez(f"{OUT}/{key}__{lang}.npz",
             **{str(i): c.astype(np.float32) for i, c in enumerate(cuts)})
    for i, c in enumerate(cuts):
        real[f"{key}|{lang}|{i}"] = len(c) / ysplit.SR
    flag = "" if score >= 0.82 else "  <- слабо легло, проверить"
    if score < 0.82:
        weak.append((key, lang, score))
    print(f"  {key:18s} {lang}  {how:5s}  совпадение {score:.2f}"
          f"  куски {' '.join(f'{len(c)/ysplit.SR:.1f}' for c in cuts)}{flag}")

json.dump(real, open("/home/claude/voice_real.json", "w"), indent=1)
print(f"\nзаписано {len(real)} кусков в voice_real.json")
if weak:
    print("слабые места:", ", ".join(f"{k}|{l} {s:.2f}" for k, l, s in weak))

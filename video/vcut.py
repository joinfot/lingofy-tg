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

import ysplit

# какая партия — такие эталонные длительности
vdur2 = importlib.import_module(os.environ.get("VDUR", "vdur2"))
# движок форматов тоже свой у каждой партии
fmts = importlib.import_module(os.environ.get("FMTS", "fmts"))

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

# тексты реплик берутся из той же сборки, что и кадры
texts = {}
for v in D.V:
    c = D.cfg(v["key"])
    ph, sl, T = fmts.build(c)
    for lang in ("ru", "de"):
        texts[f"{v['key']}|{lang}"] = [t for (_, l, t) in sl if l == lang]

# Сначала каждому файлу ищется дорожка той же длительности. Имена у
# скачанных файлов бывают то с номерами, то с отметкой времени, а порядок
# скачивания не обязан совпадать с порядком генерации, — длительность же
# не врёт.
print("сверяю файлы с эталоном")
dur = [(p, ysplit.load(p)) for p in files]
dur = [(p, x, len(x) / ysplit.SR) for p, x in dur]

left = list(vdur2.ORDER)
pairs, amb = [], []
for i, (path, x, got) in enumerate(dur):
    hit = [t for t in left if abs(got - t[2]) <= PAD]
    if len(hit) == 1:
        pairs.append([path, x, got, hit[0]])
        left.remove(hit[0])
    else:
        pairs.append([path, x, got, None])
        amb.append(i)

# Там, где длительности совпали, решает второй признак: как внутренние
# паузы ложатся на текст. Перебираются все раскладки неоднозначной группы,
# берётся та, у которой суммарное совпадение с текстом выше. Перепутанный
# вариант проигрывает заметно — у дорожек разный рисунок длин фраз.
if amb:
    import itertools
    cand = [t for t in left]
    best, barg = -1e9, None
    for perm in itertools.permutations(cand, len(amb)):
        if any(abs(dur[i][2] - t[2]) > PAD for i, t in zip(amb, perm)):
            continue
        tot = 0.0
        for i, t in zip(amb, perm):
            seq = texts[f"{t[0]}|{t[1]}"]
            _, cuts, sc = ysplit.best_of(dur[i][1], seq)
            tot += sc
        if tot > best:
            best, barg = tot, perm
    if barg is None:
        print("неоднозначные дорожки не разложились — ничего не режу.")
        sys.exit(1)
    print(f"  неоднозначных по длительности: {len(amb)}, "
          f"разложены по рисунку пауз (сумма совпадений {best:.2f})")
    for i, t in zip(amb, barg):
        pairs[i][3] = t
        left.remove(t)

bad = [p for p in pairs if p[3] is None or abs(p[2] - p[3][2]) > PAD]
loaded = []
for path, x, got, t in pairs:
    if t is None:
        print(f"  {os.path.basename(path)[:26]:26s} -> дорожка не найдена")
        continue
    key, lang, want = t
    loaded.append((key, lang, x, got))
    mark = "ок" if abs(got - want) <= PAD else "НЕ СХОДИТСЯ"
    print(f"  {os.path.basename(path)[:26]:26s} -> {key}|{lang}  "
          f"{got:6.2f} при ожидаемых {want:6.2f}  {mark}")

if bad:
    print("\nнашлись файлы, которым не нашлось дорожки, — ничего не режу.")
    sys.exit(1)

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

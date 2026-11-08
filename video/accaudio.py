# -*- coding: utf-8 -*-
"""Звук одного ролика: accaudio.py КЛЮЧ -> КЛЮЧ.wav

Голос кладётся в те же места, из которых считалась длина фаз, поэтому
реплика не может вылезти за свой кадр. Музыка под голосом приглушается.
Если нарезанного голоса ещё нет, собирается только музыка — это нормальный
первый проход, по нему видно картинку и ритм.
"""
import importlib
import os
import sys

import numpy as np
from scipy.io import wavfile

import mus

SR = mus.SR
KEY = sys.argv[1]
D = importlib.import_module(os.environ.get("BATCH", "accdata2"))
fmts = importlib.import_module(os.environ.get("FMTS", "fmts"))
cfg = D.cfg(KEY)
phases, slots, T = fmts.build(cfg)

n = int(round(T * SR))
voice = np.zeros((n, 2), np.float32)
duck = []
have = 0
miss = []

cuts = {}
for lang in ("ru", "de"):
    p = f"/home/claude/voice_a/{KEY}__{lang}.npz"
    if os.path.exists(p):
        z = np.load(p)
        cuts[lang] = [z[k] for k in sorted(z.files, key=lambda s: int(s))]

cnt = {"ru": 0, "de": 0}
for t0, lang, txt in slots:
    i = cnt[lang]
    cnt[lang] += 1
    seg = None
    if lang in cuts and i < len(cuts[lang]):
        seg = cuts[lang][i].astype(np.float32)
    if seg is None:
        miss.append(f"{lang}:{i}")
        continue
    a = int(round(t0 * SR))
    b = min(n, a + len(seg))
    if b <= a:
        continue
    s = seg[: b - a]
    pk = float(np.max(np.abs(s))) or 1.0
    s = s / pk * 0.82
    voice[a:b, 0] += s
    voice[a:b, 1] += s
    duck.append((t0, len(seg) / SR))
    have += 1

bed = mus.window(T, cfg["th"]["mus_off"])
lvl = 0.34 if have else 0.80
bed = mus.dress(bed, T, duck=duck if have else None, lvl=lvl)

# окно музыки и дорожка голоса считают длину по-разному и расходятся
# на один отсчёт — подгоняю, иначе сложение просто падает
if len(bed) > n:
    bed = bed[:n]
elif len(bed) < n:
    bed = np.pad(bed, ((0, n - len(bed)), (0, 0)))

out = bed + voice
pk = float(np.max(np.abs(out))) or 1.0
if pk > 0.985:
    out = out / pk * 0.985

wavfile.write(f"/home/claude/{KEY}.wav", SR,
              (out * 32767).astype(np.int16))
print(f"{KEY}: {T:.2f}с, реплик {have}/{len(slots)}" +
      (f", нет {','.join(miss)}" if miss else ""), flush=True)

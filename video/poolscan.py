# -*- coding: utf-8 -*-
"""Раскладывает присланные дорожки по дням: poolscan.py [папка]

Файлы приходят порциями по двадцать и без имён, поэтому складываются в одну
кучу. Здесь по длительностям решается, из какого дня каждый файл, и какие дни
уже собрались целиком.

Длительность местного mp3 на 0.03–0.05 с больше, чем у исходника, поэтому
сравнение идёт с допуском PAD. Один файл может попасть в допуск сразу к
нескольким дорожкам — поэтому не жадный проход, а назначение целиком
(linear_sum_assignment): так день либо закрывается полностью, либо честно
показывает, чего не хватает.
"""
import hashlib
import importlib
import os
import subprocess
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment

PAD = 0.07
DAYS = [6, 7, 8, 9, 10, 11]
DATE = {6: "13 ноября", 7: "14 ноября", 8: "15 ноября",
        9: "16 ноября", 10: "17 ноября", 11: "18 ноября"}


def dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out)


def scan(folder):
    files = sorted(f for f in os.listdir(folder) if f.endswith(".mp3"))
    got = [(f, dur(os.path.join(folder, f))) for f in files]
    # дубли: тот же файл, присланный дважды
    seen, uniq = {}, []
    for f, t in got:
        # По длительности и размеру считать нельзя: при постоянном битрейте
        # две разные дорожки одной длины весят одинаково. Дубль — это тот же
        # файл, присланный дважды, поэтому сверяется содержимое.
        key = hashlib.md5(open(os.path.join(folder, f), "rb").read()).hexdigest()
        if key in seen:
            print(f"дубль: {f} = {seen[key]}")
            continue
        seen[key] = f
        uniq.append((f, t))
    return uniq


def match(day, pool):
    """Сколько дорожек дня закрывается файлами из кучи."""
    ref = importlib.import_module(f"vdur{day}").ORDER
    cost = np.zeros((len(ref), len(pool)))
    for i, (_, _, t) in enumerate(ref):
        for j, (_, g) in enumerate(pool):
            cost[i, j] = abs(g - t) if abs(g - t) <= PAD else 1e6
    r, c = linear_sum_assignment(cost)
    ok = [(i, j) for i, j in zip(r, c) if cost[i, j] < 1e6]
    return ref, ok


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "pool"
    pool = scan(folder)
    print(f"\nв куче {len(pool)} дорожек\n")
    for d in DAYS:
        ref, ok = match(d, pool)
        miss = len(ref) - len(ok)
        mark = "СОБРАН" if miss == 0 else f"не хватает {miss}"
        print(f"день {d} ({DATE[d]}): {len(ok)} из {len(ref)} — {mark}")

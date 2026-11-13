# -*- coding: utf-8 -*-
"""Раскладывает кучу по дням: poolsplit.py [папка] [дни через запятую]

Назначение решается сразу по всем дням вместе, а не по одному: длительности
повторяются и внутри дня, и между днями, поэтому день, разобранный в
одиночку, утащит файл у соседнего.

Одной длины мало. В партиях 7–11 на 8.88 с приходится четыре дорожки из
трёх разных дней, и по длине их не различить — в первой раскладке на
j2_vertrag|ru так и встал чужой файл (ноль по паузам). Поэтому:

1. Строится граф «дорожка — подходящий по длине файл».
2. Компоненты, где выбора нет, закрываются сразу.
3. В спорных компонентах каждая пара считается по-настоящему: дорожка
   режется по паузам под свой текст, и назначение выбирается по сумме
   совпадений. Пять реплик в файле от четырёх отличаются надёжно.

Складывает файлы в cutN/ копиями — куча остаётся целой.
"""
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment

import ysplit

PAD = 0.07
BIG = 1e6


def dur(path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True).stdout)


def pool_of(folder):
    seen, uniq = {}, []
    for f in sorted(os.listdir(folder)):
        if not f.endswith(".mp3"):
            continue
        p = os.path.join(folder, f)
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        if h in seen:
            continue
        seen[h] = f
        uniq.append((f, dur(p)))
    return uniq


def parts(day, key, lang):
    man = json.load(open(f"man{day}.json"))
    txt = man[f"{key}|{lang}"]
    return [p for p in txt.split("\n\n") if p.strip()]


def components(ok):
    """Компоненты двудольного графа: {слоты}, {файлы}."""
    seen_s, out = set(), []
    adj_s, adj_f = {}, {}
    for i, j in ok:
        adj_s.setdefault(i, []).append(j)
        adj_f.setdefault(j, []).append(i)
    for s in adj_s:
        if s in seen_s:
            continue
        qs, qf, stack = set(), set(), [("s", s)]
        while stack:
            kind, v = stack.pop()
            if kind == "s":
                if v in qs:
                    continue
                qs.add(v)
                stack += [("f", x) for x in adj_s.get(v, [])]
            else:
                if v in qf:
                    continue
                qf.add(v)
                stack += [("s", x) for x in adj_f.get(v, [])]
        seen_s |= qs
        out.append((sorted(qs), sorted(qf)))
    return out


def main(folder, days):
    pool = pool_of(folder)
    slots = []
    for d in days:
        for k, l, t in importlib.import_module(f"vdur{d}").ORDER:
            slots.append((d, k, l, t))

    ok = [(i, j) for i, (_, _, _, t) in enumerate(slots)
          for j, (_, g) in enumerate(pool) if abs(g - t) <= PAD]

    take, cache = {}, {}
    for cs, cf in components(ok):
        if len(cs) == 1 and len(cf) == 1:
            take[cs[0]] = cf[0]
            continue
        cost = np.full((len(cs), len(cf)), BIG)
        for a, i in enumerate(cs):
            d, k, l, t = slots[i]
            seq = parts(d, k, l)
            for b, j in enumerate(cf):
                if abs(pool[j][1] - t) > PAD:
                    continue
                kk = (j, i)
                if kk not in cache:
                    x = cache.get(("wav", j))
                    if x is None:
                        x = ysplit.load(os.path.join(folder, pool[j][0]))
                        cache[("wav", j)] = x
                    cache[kk] = ysplit.best_of(x, seq)[2]
                cost[a, b] = -cache[kk]
        r, c = linear_sum_assignment(cost)
        for a, b in zip(r, c):
            if cost[a, b] < BIG:
                take[cs[a]] = cf[b]
        names = ", ".join(f"{slots[i][1]}|{slots[i][2]}" for i in cs)
        print(f"спорная группа ({len(cs)}): {names}")

    print(f"\nв куче {len(pool)}, дорожек по дням {len(slots)}, "
          f"разложено {len(take)}")

    per = {d: [] for d in days}
    for i, (d, k, l, t) in enumerate(slots):
        if i in take:
            per[d].append((k, l, pool[take[i]][0]))
        else:
            print(f"НЕ ХВАТАЕТ: день {d}  {k}|{l}  {t:.2f}с")

    for d in days:
        out = f"cut{d}"
        if len(per[d]) < 30:
            print(f"день {d}: {len(per[d])} из 30 — папку не делаю")
            continue
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        for k, l, f in per[d]:
            shutil.copy(os.path.join(folder, f), os.path.join(out, f))
        print(f"день {d}: {out}/ — {len(os.listdir(out))} файлов")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "pool"
    days = [int(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2
                             else ["7", "8", "9", "10", "11"])]
    main(folder, days)

# -*- coding: utf-8 -*-
"""Проверка новизны по ключевым словам: novelty.py МОДУЛЬ

Сравнивать весь текст ролика бессмысленно: «bitte», «дома» и «значит»
есть в каждой партии, и тогда повтором выглядит всё. Повтор — это когда
заново учат то же самое: то же немецкое слово, ту же табличку, то же
сокращение. Поэтому из каждого ролика берутся только те слова, которые он
и объясняет, и сверяются с прошлыми партиями по одному.
"""
import importlib
import os
import re
import sys

sys.path.insert(0, "/home/claude")
import topics

# что именно учит каждый формат
HEADS = {
    "raten": lambda r: [r[4]],
    "mythos": lambda r: [r[3]],
    "wort": lambda r: [r[0]],
    "anders": lambda r: [r[1], r[2]],
    "pov": lambda r: [r[1]],
    "schild": lambda r: [r[0]],
    "kuerzel": lambda r: [r[0], r[1]],
    "kultur": lambda r: [r[2]],
}

ART = {"der", "die", "das", "ein", "eine", "the"}


def key_words(s):
    """Значимые слова ключа: без артиклей и коротких служебных."""
    w = [x.lower() for x in re.findall(r"[\wÄÖÜäöüß-]+", str(s))]
    return [x for x in w if x not in ART and len(x) >= 4]


def norm(s):
    """Фраза без знаков и регистра — чтобы сравнивать по существу."""
    return " ".join(re.findall(r"[\wÄÖÜäöüß]+", str(s).lower()))


def inventory(skip):
    """Что уже выходило: целые фразы и отдельные выученные слова.

    Фраза считается бывшей, только если она встречалась целиком. Иначе
    «Tschüss» внутри чужого предложения делал бы повтором любую фразу,
    где есть это слово.
    """
    phrases, words = set(), set()
    for s in topics.harvest(skip):
        n = norm(s)
        if not n:
            continue
        phrases.add(n)
        parts = [p for p in n.split() if p not in ART and len(p) >= 5]
        if len(parts) == 1:
            words.add(parts[0])
    return phrases, words


def check(mod):
    D = importlib.import_module(mod)
    phrases, words = inventory((mod,))
    print()
    total = hits = 0
    for v in D.V:
        fmt = v.get("fmt") or getattr(D, "FMT", {}).get(v["acc"])
        get = HEADS[fmt]
        dups = []
        for r in v["rows"]:
            for h in get(r):
                total += 1
                n = norm(h)
                kw = key_words(h)
                # целая фраза уже звучала — либо это то же одно слово
                same = n in phrases or (len(kw) == 1 and kw[0] in words)
                if same:
                    dups.append(h)
                    hits += 1
        mark = "  <- уже было: " + "; ".join(dups[:4]) if dups else ""
        print(f"  {v['key']:16s} {fmt:8s} ключей {len(v['rows'])}{mark}")
    print(f"\nключей всего {total}, повторов {hits}")
    return hits


if __name__ == "__main__":
    sys.exit(1 if check(sys.argv[1]) else 0)

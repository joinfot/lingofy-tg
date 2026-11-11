# -*- coding: utf-8 -*-
"""Тексты для озвучки: makeman.py МОДУЛЬ ФАЙЛ

Берёт те же реплики, из которых считаются кадры, и готовит их к диктору.

Две вещи, на которых уже обжигались:

1. Знак в конце. Без него диктор склеивает реплики в одну длинную фразу,
   и потом их не разрезать по паузам. Но если фраза кончается запятой или
   двоеточием — точку не добавляем, иначе выходит «господа,.».

2. Немецкие слова внутри русской реплики. Русский голос читает латиницу
   по буквам или на свой лад, поэтому в ОЗВУЧКЕ они заменяются на запись
   кириллицей. На экране при этом остаётся исходное написание.
"""
import importlib
import json
import os
import re
import sys

TERM = ".!?…,:;"

# как произносить немецкие слова в русской дорожке
SAY = {
    "Ausbildung": "Аусбильдунг",
    "Termin": "термин по-немецки",
    "Berufsschule": "Беруфсшуле",
    "Hausmeister": "Хаусмайстер",
    "Nachmieter": "Нахмитер",
    "Schlüsseldienst": "Шлюссельдинст",
    "Schornsteinfeger": "Шорнштайнфегер",
    "Packstation": "Пакштацьон",
    "Notaufnahme": "Нотауфнаме",
    "Sperrmüll": "Шперрмюль",
    "Schwierig": "швириг",
    "schwierig": "швириг",
    "Genau": "генау",
    "Wie bitte": "ви битте",
    "Von mir aus": "фон мир аус",
    "Leiten": "ляйтен",
}


def say(txt):
    """Русская реплика в том виде, в каком её надо прочесть."""
    for de, ru in sorted(SAY.items(), key=lambda kv: -len(kv[0])):
        txt = re.sub(rf"\b{re.escape(de)}\b", ru, txt)
    # замена могла встать в начало предложения со строчной буквы
    return re.sub(r"(^|[.!?…]\s+)([а-яё])",
                  lambda m: m.group(1) + m.group(2).upper(), txt)


def close(p):
    p = p.strip()
    return p if p and p[-1] in TERM else p + "."


def build(mod, fmts_name):
    D = importlib.import_module(mod)
    fmts = importlib.import_module(fmts_name)
    man = {}
    for v in D.V:
        ph, sl, T = fmts.build(D.cfg(v["key"]))
        for lang in ("ru", "de"):
            parts = [t for (_, l, t) in sl if l == lang]
            parts = [close(say(p) if lang == "ru" else p) for p in parts]
            man[f"{v['key']}|{lang}"] = "\n\n".join(parts)
    return man


if __name__ == "__main__":
    mod = sys.argv[1]
    out = sys.argv[2]
    man = build(mod, os.environ.get("FMTS", "fmts3"))
    json.dump(man, open(out, "w"), ensure_ascii=False, indent=1)
    # латиница в русской дорожке — последний шанс её заметить
    left = sorted({w for k, t in man.items() if k.endswith("|ru")
                   for w in re.findall(r"[A-Za-zÄÖÜäöüß]{3,}", t)})
    print(f"дорожек {len(man)}, знаков {sum(len(x) for x in man.values())}")
    if left:
        print("латиницей в русской озвучке осталось:", ", ".join(left))

# -*- coding: utf-8 -*-
"""Точные длительности дорожек пятой партии — прямо от ElevenLabs.

Ролики короткие, дорожек тридцать, и совпадений по длительности тут уже
шесть пар:

    u1_laeden|de и v3_alltag|de        — обе 6.08
    u3_essen|ru и x1_strasse|de        — обе 7.68
    u3_essen|de и x2_arzt|de           — обе 6.56
    v3_alltag|ru и w1_brief|de         — обе 10.88
    w2_wohnungssuche|de и y2_arbeit|ru — обе 10.16
    y2_arbeit|de и y3_strasse|de       — обе 8.24

Шесть пар — это двенадцать неоднозначных файлов, и сплошной перебор всех
раскладок тут уже не считается. Поэтому в vcut.py неоднозначные разводятся
по группам одинаковой длительности: внутри пары всего два варианта, и
каждая пара решается отдельно — по тому, как внутренние паузы ложатся на
текст.
"""

ORDER = [
    ("u1_laeden", "ru", 5.20), ("u1_laeden", "de", 6.08),
    ("u2_feiertage", "ru", 10.48), ("u2_feiertage", "de", 7.52),
    ("u3_essen", "ru", 7.68), ("u3_essen", "de", 6.56),
    ("v1_vogel", "ru", 11.20), ("v1_vogel", "de", 6.32),
    ("v2_gefuehle", "ru", 17.44), ("v2_gefuehle", "de", 6.40),
    ("v3_alltag", "ru", 10.88), ("v3_alltag", "de", 6.08),
    ("w1_brief", "ru", 12.56), ("w1_brief", "de", 10.88),
    ("w2_wohnungssuche", "ru", 12.64), ("w2_wohnungssuche", "de", 10.16),
    ("w3_nachbar", "ru", 12.48), ("w3_nachbar", "de", 8.96),
    ("x1_strasse", "ru", 7.36), ("x1_strasse", "de", 7.68),
    ("x2_arzt", "ru", 6.00), ("x2_arzt", "de", 6.56),
    ("x3_parken", "ru", 9.84), ("x3_parken", "de", 8.72),
    ("y1_november", "ru", 12.00), ("y1_november", "de", 8.08),
    ("y2_arbeit", "ru", 10.16), ("y2_arbeit", "de", 8.24),
    ("y3_strasse", "ru", 11.76), ("y3_strasse", "de", 8.24),
]

DUR = {f"{k}|{l}": d for k, l, d in ORDER}

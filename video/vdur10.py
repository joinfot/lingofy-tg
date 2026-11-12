# -*- coding: utf-8 -*-
"""Точные длительности дорожек партии accdata10 — прямо от ElevenLabs.

Совпали по длительности:
    x2_anzeige|de, x3_produkt|de — все 6.08
    u3_dinge|de, x1_laden|ru — все 6.64
    w2_flohmarkt|de, y1_einkauf|de — все 7.12
    v3_anzeige|de, w2_flohmarkt|ru — все 10.72

Их разводит перебор по рисунку пауз, группами (см. vcut.py).

Расходятся на 0.08 с при допуске 0.07: 6.48/6.56, 6.56/6.64, 6.64/6.72, 7.04/7.12, 8.96/9.04, 9.04/9.12, 9.52/9.60, 9.60/9.68, 9.68/9.76, 10.72/10.80.
Такой файл попадёт в неоднозначную группу и разберётся по паузам.
"""

ORDER = [
    ("u1_kaufen", "ru", 6.72), ("u1_kaufen", "de", 5.92),
    ("u2_laden", "ru", 9.60), ("u2_laden", "de", 7.04),
    ("u3_dinge", "ru", 9.04), ("u3_dinge", "de", 6.64),
    ("v1_menschen", "ru", 10.80), ("v1_menschen", "de", 6.32),
    ("v2_handeln", "ru", 9.12), ("v2_handeln", "de", 10.08),
    ("v3_anzeige", "ru", 9.28), ("v3_anzeige", "de", 10.72),
    ("w1_verkauf", "ru", 9.76), ("w1_verkauf", "de", 6.48),
    ("w2_flohmarkt", "ru", 10.72), ("w2_flohmarkt", "de", 7.12),
    ("w3_reklamation", "ru", 12.56), ("w3_reklamation", "de", 8.48),
    ("x1_laden", "ru", 6.64), ("x1_laden", "de", 6.56),
    ("x2_anzeige", "ru", 13.60), ("x2_anzeige", "de", 6.08),
    ("x3_produkt", "ru", 14.16), ("x3_produkt", "de", 6.08),
    ("y1_einkauf", "ru", 9.52), ("y1_einkauf", "de", 7.12),
    ("y2_reparieren", "ru", 9.68), ("y2_reparieren", "de", 7.76),
    ("y3_essen", "ru", 8.96), ("y3_essen", "de", 7.60),
]

DUR = {f"{k}|{l}": x for k, l, x in ORDER}

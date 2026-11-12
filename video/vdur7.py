# -*- coding: utf-8 -*-
"""Точные длительности дорожек партии accdata7 — прямо от ElevenLabs.

Совпали по длительности:
    h1_arzt|de, j2_vertrag|de — все 8.32
    f2_wohnen|ru, h3_uebergabe|de — все 8.48
    h1_arzt|ru, h2_samstag|ru — все 11.36

Их разводит перебор по рисунку пауз, группами (см. vcut.py).

Расходятся на 0.08 с при допуске 0.07: 6.08/6.16, 6.16/6.24, 6.88/6.96, 6.96/7.04, 8.24/8.32, 8.88/8.96, 8.96/9.04, 9.36/9.44, 13.04/13.12.
Такой файл попадёт в неоднозначную группу и разберётся по паузам.
"""

ORDER = [
    ("f1_arbeit", "ru", 6.08), ("f1_arbeit", "de", 5.68),
    ("f2_wohnen", "ru", 8.48), ("f2_wohnen", "de", 6.24),
    ("f3_rad", "ru", 9.04), ("f3_rad", "de", 6.96),
    ("g1_tiere", "ru", 10.24), ("g1_tiere", "de", 6.16),
    ("g2_gespraech", "ru", 13.12), ("g2_gespraech", "de", 8.96),
    ("g3_termin", "ru", 13.04), ("g3_termin", "de", 10.00),
    ("h1_arzt", "ru", 11.36), ("h1_arzt", "de", 8.32),
    ("h2_samstag", "ru", 11.36), ("h2_samstag", "de", 7.28),
    ("h3_uebergabe", "ru", 12.16), ("h3_uebergabe", "de", 8.48),
    ("i1_verbote", "ru", 7.68), ("i1_verbote", "de", 6.88),
    ("i2_preise", "ru", 14.96), ("i2_preise", "de", 4.32),
    ("i3_haus", "ru", 14.64), ("i3_haus", "de", 6.64),
    ("j1_geld", "ru", 9.36), ("j1_geld", "de", 8.24),
    ("j2_vertrag", "ru", 8.88), ("j2_vertrag", "de", 8.32),
    ("j3_gaeste", "ru", 9.44), ("j3_gaeste", "de", 7.04),
]

DUR = {f"{k}|{l}": x for k, l, x in ORDER}

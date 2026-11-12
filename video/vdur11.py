# -*- coding: utf-8 -*-
"""Точные длительности дорожек партии accdata11 — прямо от ElevenLabs.

Совпали по длительности:
    z2_nachbarn|de, z3_feiern|de — все 6.00
    aa2_kennen|de, cc1_ruhe|ru — все 7.76
    dd2_verein|de, dd3_wochenende|de — все 7.84

Их разводит перебор по рисунку пауз, группами (см. vcut.py).

Расходятся на 0.08 с при допуске 0.07: 5.60/5.68, 6.00/6.08, 7.76/7.84, 8.64/8.72, 8.88/8.96, 14.00/14.08.
Такой файл попадёт в неоднозначную группу и разберётся по паузам.
"""

ORDER = [
    ("z1_leben", "ru", 6.08), ("z1_leben", "de", 5.68),
    ("z2_nachbarn", "ru", 8.72), ("z2_nachbarn", "de", 6.00),
    ("z3_feiern", "ru", 8.88), ("z3_feiern", "de", 6.00),
    ("aa1_charakter", "ru", 14.32), ("aa1_charakter", "de", 6.88),
    ("aa2_kennen", "ru", 11.52), ("aa2_kennen", "de", 7.76),
    ("aa3_einladen", "ru", 8.64), ("aa3_einladen", "de", 9.28),
    ("bb1_nachbarn", "ru", 12.24), ("bb1_nachbarn", "de", 9.12),
    ("bb2_verein", "ru", 11.12), ("bb2_verein", "de", 8.40),
    ("bb3_geburtstag", "ru", 10.08), ("bb3_geburtstag", "de", 6.72),
    ("cc1_ruhe", "ru", 7.76), ("cc1_ruhe", "de", 7.36),
    ("cc2_verein", "ru", 14.00), ("cc2_verein", "de", 5.44),
    ("cc3_orte", "ru", 14.08), ("cc3_orte", "de", 5.60),
    ("dd1_freunde", "ru", 9.44), ("dd1_freunde", "de", 7.12),
    ("dd2_verein", "ru", 8.96), ("dd2_verein", "de", 7.84),
    ("dd3_wochenende", "ru", 9.76), ("dd3_wochenende", "de", 7.84),
]

DUR = {f"{k}|{l}": x for k, l, x in ORDER}

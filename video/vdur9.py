# -*- coding: utf-8 -*-
"""Точные длительности дорожек партии accdata9 — прямо от ElevenLabs.

Совпали по длительности:
    p1_verkehr|ru, p3_bank|de — все 6.40
    s1_bahn|ru, t2_schule|de — все 7.36
    p3_bank|ru, r3_elternabend|de, t3_lohn|de — все 8.40
    r1_konto|de, r2_kontrolle|de — все 9.04
    q3_absagen|ru, q3_absagen|de — все 11.28
    q2_fragen|ru, r3_elternabend|ru — все 11.52
    r2_kontrolle|ru, t3_lohn|ru — все 11.76

Их разводит перебор по рисунку пауз, группами (см. vcut.py).

Расходятся на 0.08 с при допуске 0.07: 6.08/6.16, 6.16/6.24, 11.76/11.84.
Такой файл попадёт в неоднозначную группу и разберётся по паузам.
"""

ORDER = [
    ("p1_verkehr", "ru", 6.40), ("p1_verkehr", "de", 6.16),
    ("p2_schule", "ru", 8.80), ("p2_schule", "de", 6.08),
    ("p3_bank", "ru", 8.40), ("p3_bank", "de", 6.40),
    ("q1_geld", "ru", 11.84), ("q1_geld", "de", 6.24),
    ("q2_fragen", "ru", 11.52), ("q2_fragen", "de", 10.80),
    ("q3_absagen", "ru", 11.28), ("q3_absagen", "de", 11.28),
    ("r1_konto", "ru", 12.48), ("r1_konto", "de", 9.04),
    ("r2_kontrolle", "ru", 11.76), ("r2_kontrolle", "de", 9.04),
    ("r3_elternabend", "ru", 11.52), ("r3_elternabend", "de", 8.40),
    ("s1_bahn", "ru", 7.36), ("s1_bahn", "de", 7.76),
    ("s2_adresse", "ru", 12.72), ("s2_adresse", "de", 4.80),
    ("s3_bank", "ru", 13.76), ("s3_bank", "de", 5.60),
    ("t1_fahren", "ru", 9.92), ("t1_fahren", "de", 7.04),
    ("t2_schule", "ru", 9.28), ("t2_schule", "de", 7.36),
    ("t3_lohn", "ru", 11.76), ("t3_lohn", "de", 8.40),
]

DUR = {f"{k}|{l}": x for k, l, x in ORDER}

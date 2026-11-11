# -*- coding: utf-8 -*-
"""Точные длительности дорожек шестой партии — прямо от ElevenLabs.

Совпали по длительности четыре пары:

    a3_azubi|de и e3_arzt|de       — обе 7.28
    e1_post|de и e2_muell|de       — обе 7.68
    e1_post|ru и e3_arzt|ru        — обе 9.68
    c1_ersterTag|ru и d3_stadt|ru  — обе 12.48

Их разводит перебор по рисунку пауз, группами (см. vcut.py).

Отдельно стоит помнить про a2_alltag|ru (10.64) и b2_hoeflich|de (10.56):
они расходятся всего на 0.08 секунды при допуске 0.07. Запас крошечный,
но его хватает — местный mp3 длиннее оригинала на 0.03–0.05.
"""

ORDER = [
    ("a1_leute", "ru", 7.04), ("a1_leute", "de", 6.24),
    ("a2_alltag", "ru", 10.64), ("a2_alltag", "de", 7.20),
    ("a3_azubi", "ru", 11.36), ("a3_azubi", "de", 7.28),
    ("b1_dinge", "ru", 11.92), ("b1_dinge", "de", 6.08),
    ("b2_hoeflich", "ru", 8.16), ("b2_hoeflich", "de", 10.56),
    ("b3_schreiben", "ru", 11.28), ("b3_schreiben", "de", 9.28),
    ("c1_ersterTag", "ru", 12.48), ("c1_ersterTag", "de", 8.56),
    ("c2_zugausfall", "ru", 13.60), ("c2_zugausfall", "de", 10.08),
    ("c3_kasse", "ru", 10.32), ("c3_kasse", "de", 8.32),
    ("d1_bahn", "ru", 7.36), ("d1_bahn", "de", 7.92),
    ("d2_brief", "ru", 12.72), ("d2_brief", "de", 5.04),
    ("d3_stadt", "ru", 12.48), ("d3_stadt", "de", 6.00),
    ("e1_post", "ru", 9.68), ("e1_post", "de", 7.68),
    ("e2_muell", "ru", 9.28), ("e2_muell", "de", 7.68),
    ("e3_arzt", "ru", 9.68), ("e3_arzt", "de", 7.28),
]

DUR = {f"{k}|{l}": d for k, l, d in ORDER}

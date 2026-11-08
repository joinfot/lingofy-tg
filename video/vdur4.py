# -*- coding: utf-8 -*-
"""Точные длительности дорожек четвёртой партии — прямо от ElevenLabs.

В этой партии ролики короткие, дорожек много коротких, и три пары совпали
по длительности секунда в секунду:

    p2_behoerden|ru и p3_marken|ru   — обе 8.08
    q2_unuebersetzbar|de и r2_aldi|de — обе 6.64
    r1_buergeramt|de и r3_besuch|ru  — обе 11.84

Одной длительности для них мало. Такие пары разводятся вторым признаком —
тем, как внутренние паузы ложатся на текст: у каждой дорожки свой рисунок
длин фраз, и перепутанный вариант ложится заметно хуже.
"""

ORDER = [
    ("p1_scheinanglizismen", "ru", 8.96), ("p1_scheinanglizismen", "de", 5.28),
    ("p2_behoerden", "ru", 8.08), ("p2_behoerden", "de", 6.40),
    ("p3_marken", "ru", 8.08), ("p3_marken", "de", 4.56),
    ("q1_tiere", "ru", 12.80), ("q1_tiere", "de", 6.24),
    ("q2_unuebersetzbar", "ru", 18.96), ("q2_unuebersetzbar", "de", 6.64),
    ("q3_lang", "ru", 17.20), ("q3_lang", "de", 8.16),
    ("r1_buergeramt", "ru", 13.36), ("r1_buergeramt", "de", 11.84),
    ("r2_aldi", "ru", 10.24), ("r2_aldi", "de", 6.64),
    ("r3_besuch", "ru", 11.84), ("r3_besuch", "de", 8.72),
    ("s1_haus", "ru", 8.56), ("s1_haus", "de", 9.12),
    ("s2_supermarkt", "ru", 7.44), ("s2_supermarkt", "de", 6.80),
    ("s3_bahnhof", "ru", 7.12), ("s3_bahnhof", "de", 7.60),
    ("t1_alltag", "ru", 13.28), ("t1_alltag", "de", 6.88),
    ("t2_ordnung", "ru", 11.12), ("t2_ordnung", "de", 6.96),
    ("t3_wohnung", "ru", 12.24), ("t3_wohnung", "de", 6.48),
]

DUR = {f"{k}|{l}": d for k, l, d in ORDER}

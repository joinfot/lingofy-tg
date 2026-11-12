# -*- coding: utf-8 -*-
"""Точные длительности дорожек партии accdata8 — прямо от ElevenLabs.

Совпали по длительности:
    k1_markt|ru, l1_woerter|de — все 6.40
    m1_markt|de, n1_winter|ru — все 8.40
    k2_weihnachten|ru, o1_advent|ru — все 10.08

Их разводит перебор по рисунку пауз, группами (см. vcut.py).

Расходятся на 0.08 с при допуске 0.07: 6.72/6.80, 6.80/6.88, 7.76/7.84, 8.56/8.64, 11.28/11.36, 11.52/11.60.
Такой файл попадёт в неоднозначную группу и разберётся по паузам.
"""

ORDER = [
    ("k1_markt", "ru", 6.40), ("k1_markt", "de", 6.88),
    ("k2_weihnachten", "ru", 10.08), ("k2_weihnachten", "de", 6.80),
    ("k3_winter", "ru", 8.64), ("k3_winter", "de", 6.72),
    ("l1_woerter", "ru", 12.56), ("l1_woerter", "de", 6.40),
    ("l2_tisch", "ru", 11.28), ("l2_tisch", "de", 11.60),
    ("l3_einladen", "ru", 12.40), ("l3_einladen", "de", 9.44),
    ("m1_markt", "ru", 11.52), ("m1_markt", "de", 8.40),
    ("m2_feier", "ru", 11.36), ("m2_feier", "de", 8.56),
    ("m3_eis", "ru", 11.84), ("m3_eis", "de", 8.80),
    ("n1_winter", "ru", 8.40), ("n1_winter", "de", 7.12),
    ("n2_zeiten", "ru", 15.20), ("n2_zeiten", "de", 5.44),
    ("n3_termin", "ru", 13.68), ("n3_termin", "de", 4.96),
    ("o1_advent", "ru", 10.08), ("o1_advent", "de", 8.08),
    ("o2_winteralltag", "ru", 9.68), ("o2_winteralltag", "de", 7.84),
    ("o3_jahreswechsel", "ru", 10.48), ("o3_jahreswechsel", "de", 7.76),
]

DUR = {f"{k}|{l}": x for k, l, x in ORDER}

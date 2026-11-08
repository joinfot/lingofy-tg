# -*- coding: utf-8 -*-
"""Точные длительности дорожек третьей партии — прямо от ElevenLabs.

Это единственный надёжный способ понять, какой скачанный файл к какому
ролику относится: имена у них одинаковые, а по тексту не сопоставить —
я их не слышу. Длительность местного mp3 на 0.03–0.05 с больше из-за
добивки последнего кадра, поэтому сверка идёт с допуском.

В этой партии совпадений длительностей нет — каждая дорожка опознаётся
однозначно даже без опоры на порядок.
"""

ORDER = [
    ("k1_imperativ", "ru", 16.96), ("k1_imperativ", "de", 12.00),
    ("k2_wissen", "ru", 13.20), ("k2_wissen", "de", 11.12),
    ("k3_datum", "ru", 16.56), ("k3_datum", "de", 14.80),
    ("l1_krankmeldung", "ru", 12.80), ("l1_krankmeldung", "de", 13.12),
    ("l2_fuehrerschein", "ru", 12.40), ("l2_fuehrerschein", "de", 16.40),
    ("l3_versicherung", "ru", 11.20), ("l3_versicherung", "de", 13.76),
    ("m1_weihnachtsmarkt", "ru", 24.56), ("m1_weihnachtsmarkt", "de", 23.60),
    ("m2_reklamation", "ru", 25.92), ("m2_reklamation", "de", 23.92),
    ("m3_sportverein", "ru", 25.84), ("m3_sportverein", "de", 26.64),
    ("n1_verbpraep", "ru", 26.16), ("n1_verbpraep", "de", 10.72),
    ("n2_adjpraep", "ru", 20.72), ("n2_adjpraep", "de", 11.92),
    ("n3_indirekt", "ru", 21.12), ("n3_indirekt", "de", 12.88),
    ("o1_advent", "ru", 13.52), ("o1_advent", "de", 25.20),
    ("o2_steuer", "ru", 10.96), ("o2_steuer", "de", 26.80),
    ("o3_uebergabe", "ru", 14.08), ("o3_uebergabe", "de", 29.36),
]

DUR = {f"{k}|{l}": d for k, l, d in ORDER}

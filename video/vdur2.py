# -*- coding: utf-8 -*-
"""Точные длительности дорожек второй партии — прямо от ElevenLabs.

Это единственный надёжный способ понять, какой скачанный файл к какому
ролику относится: имена у них одинаковые, а по тексту не сопоставить —
я их не слышу. Длительность местного mp3 на 0.03–0.05 с больше из-за
добивки последнего кадра, поэтому сверка идёт с допуском.

Порядок в ORDER — это порядок, в котором дорожки уходили на генерацию.
Им разрешаются совпадения длительностей: h2|ru и h3|ru обе по 22.80.
"""

ORDER = [
    ("f1_wohin", "ru", 13.68), ("f1_wohin", "de", 16.24),
    ("f2_dativverben", "ru", 12.80), ("f2_dativverben", "de", 13.52),
    ("f3_komposita", "ru", 16.40), ("f3_komposita", "de", 12.40),
    ("g1_post", "ru", 11.68), ("g1_post", "de", 13.20),
    ("g2_bewerbung", "ru", 12.16), ("g2_bewerbung", "de", 14.08),
    ("g3_kuendigung", "ru", 13.52), ("g3_kuendigung", "de", 14.48),
    ("h1_verspaetung", "ru", 21.44), ("h1_verspaetung", "de", 19.28),
    ("h2_verschieben", "ru", 22.80), ("h2_verschieben", "de", 20.56),
    ("h3_kleinanzeigen", "ru", 22.80), ("h3_kleinanzeigen", "de", 22.48),
    ("i1_verschmelzung", "ru", 29.60), ("i1_verschmelzung", "de", 11.76),
    ("i2_fragen", "ru", 24.16), ("i2_fragen", "de", 8.88),
    ("i3_pronomen", "ru", 20.88), ("i3_pronomen", "de", 8.96),
    ("j1_geld", "ru", 13.04), ("j1_geld", "de", 24.64),
    ("j2_lernen", "ru", 11.52), ("j2_lernen", "de", 23.68),
    ("j3_winter", "ru", 10.40), ("j3_winter", "de", 22.40),
]

DUR = {f"{k}|{l}": d for k, l, d in ORDER}

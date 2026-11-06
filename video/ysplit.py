# -*- coding: utf-8 -*-
"""Нарезка одной дорожки на отдельные реплики по паузам.

ElevenLabs отдаёт весь текст ролика одним файлом. Резать его надо ровно по
числу фраз, и ровно по тем паузам, которые диктор сделал между ними, — а не
по любой тишине: внутри фразы есть вдохи, запятые и точки в середине.

Поэтому пауза считается не от пика файла, а от громкости соседней речи:
тихая запись иначе выглядит сплошной паузой. А какие из подходящих пауз
настоящие границы, решает динамика: длительность куска должна быть
пропорциональна длине его фразы.
"""
import subprocess
import tempfile

import numpy as np
from scipy.io import wavfile

SR = 44100
WIN = int(0.020 * SR)


def load(path):
    """mp3 -> моно float32 на 44100."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    subprocess.run(["ffmpeg", "-y", "-i", path, "-ac", "1", "-ar", str(SR),
                    tmp, "-loglevel", "error"], check=True)
    sr, x = wavfile.read(tmp)
    x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(1)
    if np.abs(x).max() > 1.5:
        x = x / 32768.0
    return x


def env(x):
    """Огибающая по 20 мс."""
    n = len(x) // WIN * WIN
    return np.sqrt((x[:n].reshape(-1, WIN) ** 2).mean(1) + 1e-12)


def gaps(x, min_w=0.12, rel=0.15):
    """Паузы: (начало, конец, длительность) в секундах.

    Порог берётся от громкости речи вокруг самой паузы, а не от пика всего
    файла, иначе на тихой записи вдох считается речью, а на громкой —
    настоящая пауза теряется.
    """
    e = env(x)
    k = max(1, int(0.6 / 0.020))
    pad = np.pad(e, k, mode="edge")
    loc = np.array([np.percentile(pad[i:i + 2 * k + 1], 85)
                    for i in range(len(e))])
    quiet = e < np.maximum(loc * rel, e.max() * 0.012)
    out, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            a, b = i * 0.020, j * 0.020
            if b - a >= min_w:
                out.append((a, b, b - a))
            i = j
        else:
            i += 1
    return out


def _bounds(x, n_parts, min_gap):
    """Середины подходящих пауз — кандидаты в границы."""
    T = len(x) / SR
    g = [(a, b, d) for a, b, d in gaps(x) if d >= min_gap]
    # края не границы: там тишина до и после речи
    g = [t for t in g if t[0] > 0.15 and t[1] < T - 0.15]
    return [((a + b) / 2, d) for a, b, d in g]


def _speech_span(x):
    """Где начинается и кончается речь — чтобы не считать края тишиной."""
    e = env(x)
    thr = max(e.max() * 0.06, 1e-4)
    on = np.where(e > thr)[0]
    if len(on) == 0:
        return 0.0, len(x) / SR
    return max(0.0, on[0] * 0.020 - 0.08), min(len(x) / SR,
                                               (on[-1] + 1) * 0.020 + 0.12)


def _cut(x, edges):
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        out.append(x[int(a * SR):int(b * SR)].copy())
    return out


def split(x, seq):
    """Простейший способ: N−1 самых длинных пауз."""
    n = len(seq)
    c = _bounds(x, n, 0.15)
    c.sort(key=lambda t: -t[1])
    picks = sorted(t[0] for t in c[:n - 1])
    s, e = _speech_span(x)
    return _cut(x, [s] + picks + [e])


def split_fit(x, seq):
    """Жадно: берём паузу, ближайшую к ожидаемой по тексту точке."""
    n = len(seq)
    s, e = _speech_span(x)
    ch = np.array([max(1, len(t)) for t in seq], float)
    want = s + np.cumsum(ch / ch.sum())[:-1] * (e - s)
    c = [t[0] for t in _bounds(x, n, 0.15)]
    picks = []
    for w in want:
        free = [p for p in c if p not in picks]
        if not free:
            break
        picks.append(min(free, key=lambda p: abs(p - w)))
    picks = sorted(picks)
    while len(picks) < n - 1:
        picks.append(e)
    return _cut(x, [s] + picks[:n - 1] + [e])


def split_best(x, seq, min_gap=0.15):
    """Кандидатами в границы служат только разрывы не короче min_gap,
    а какие выбрать, решает динамика: длительность группы должна быть
    пропорциональна числу знаков её фразы.

    Жадный выбор здесь ошибается: он цепляется за длинную паузу в середине
    фразы (например, после тире) и оставляет настоящей границе крошечный
    кусок. Динамика считает раскладку целиком.
    """
    n = len(seq)
    s, e = _speech_span(x)
    if n == 1:
        return _cut(x, [s, e])
    cand = [t for t in _bounds(x, n, min_gap) if s < t[0] < e]
    if len(cand) < n - 1:
        return split_fit(x, seq)
    pos = [s] + [c[0] for c in cand] + [e]
    gap = [0.0] + [c[1] for c in cand] + [0.0]
    m = len(pos)

    ch = np.array([max(1, len(t)) for t in seq], float)
    speech = e - s
    want = speech * ch / ch.sum()

    INF = 1e18
    # dp[j][p] — лучшая стоимость, если j-я фраза кончается в точке p
    dp = np.full((n, m), INF)
    prev = np.full((n, m), -1, int)
    for p in range(1, m):
        d = pos[p] - pos[0]
        dp[0][p] = abs(d - want[0]) / max(want[0], 0.2) - 0.25 * min(gap[p], 0.6)
    for j in range(1, n):
        for p in range(j + 1, m):
            best, arg = INF, -1
            for q in range(j, p):
                if dp[j - 1][q] >= INF:
                    continue
                d = pos[p] - pos[q]
                c = dp[j - 1][q] + abs(d - want[j]) / max(want[j], 0.2)
                if j < n - 1:
                    c -= 0.25 * min(gap[p], 0.6)
                if c < best:
                    best, arg = c, q
            dp[j][p] = best
            prev[j][p] = arg
    if dp[n - 1][m - 1] >= INF:
        return split_fit(x, seq)
    edges, p = [pos[m - 1]], m - 1
    for j in range(n - 1, 0, -1):
        p = prev[j][p]
        edges.append(pos[p])
    edges.append(pos[0])
    return _cut(x, sorted(set(edges)))


def fit_score(cuts, seq):
    """Насколько раскладка похожа на текст: 1.0 — идеально."""
    d = np.array([len(c) / SR for c in cuts], float)
    ch = np.array([max(1, len(t)) for t in seq], float)
    if d.sum() <= 0:
        return 0.0
    a = d / d.sum()
    b = ch / ch.sum()
    return float(1.0 - np.abs(a - b).sum() / 2)


def best_of(x, seq):
    """Три способа, берём тот, что лучше ложится на текст."""
    out = []
    for name, fn in (("best", split_best), ("split", split), ("fit", split_fit)):
        try:
            c = fn(x, seq)
        except Exception:
            continue
        if len(c) != len(seq) or min(len(s) for s in c) < int(0.12 * SR):
            continue
        out.append((fit_score(c, seq), name, c))
    if not out:
        return "none", None, 0.0
    out.sort(key=lambda t: -t[0])
    sc, name, c = out[0]
    return name, c, sc

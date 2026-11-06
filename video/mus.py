# -*- coding: utf-8 -*-
"""Подложка из трека Олега (mus/aglow.wav).

Своей музыки здесь нет и не появляется: берётся окно из его файла, и всё,
что с ним делается, — это громкость и срез. Никаких синтезированных
подъёмов, ударов и слоёв поверх: музыка должна быть его.

Трек ровный по всей длине, края — затухания, поэтому рабочая часть берётся
с отступом. Для каждого аккаунта своё окно, петлить не нужно.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
import os

PATH = os.environ.get("MUSPATH", "/home/claude/mus/aglow.wav")
BODY = (12.0, 130.0)          # рабочая часть без затуханий
BLK = int(0.040 * SR)

_cache = {}


# ─────────────────── автоматизация громкости и среза ───────────────────

def ramp(n, pts):
    """Кусочно-линейная кривая по точкам [(время, значение), ...]."""
    t = np.array([p[0] for p in pts], float)
    v = np.array([p[1] for p in pts], float)
    x = np.arange(n) / SR
    return np.interp(x, t, v).astype(np.float32)


def sweep(x, cutoff, kind="low"):
    """Фильтр с едущей частотой среза.

    Перекрытие с шагом в половину окна: окна Ханна складываются в единицу.
    Сигнал дополняется тишиной по краям — иначе первый отсчёт накрыт только
    краем одного окна, где сумма окон почти нуль, и деление на неё даёт
    выброс. Один такой выброс не слышно, но по нему нормируется вся
    дорожка, и музыка уходит в еле слышную.
    """
    n = len(x)
    hop, win_n = BLK, 2 * BLK
    win = np.hanning(win_n).astype(np.float32)
    xp = np.concatenate([np.zeros(BLK, np.float32),
                         x.astype(np.float32),
                         np.zeros(2 * BLK, np.float32)])
    np_ = len(xp)
    out = np.zeros(np_ + win_n, dtype=np.float32)
    wsum = np.zeros(np_ + win_n, dtype=np.float32)
    warm = 4 * BLK
    for pos in range(0, np_, hop):
        a = max(0, pos - warm)
        b = min(np_, pos + win_n)
        chunk = xp[a:b]
        if len(chunk) < 16:
            continue
        ci = min(max(pos - BLK, 0), n - 1)
        fc = float(np.clip(cutoff[ci], 60.0, 19000.0))
        sos = butter(4, fc / (SR / 2), btype=kind, output="sos")
        y = sosfilt(sos, chunk).astype(np.float32)
        s = pos - a
        seg = y[s:s + win_n]
        w = win[:len(seg)]
        out[pos:pos + len(seg)] += seg * w
        wsum[pos:pos + len(seg)] += w
    return (out[BLK:BLK + n] / np.maximum(wsum[BLK:BLK + n], 0.30)).astype(np.float32)


# ─────────────────────────── сам трек ───────────────────────────

def track():
    if "x" not in _cache:
        sr, x = wavfile.read(PATH)
        if sr != SR:
            raise SystemExit(f"трек на {sr} Гц, ожидалось {SR}")
        x = x.astype(np.float32)
        x = x / (32768.0 if x.dtype != np.float32 or np.abs(x).max() > 1.5 else 1.0)
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        _cache["x"] = x
    return _cache["x"]


def window(T, off, fade=0.5):
    """Окно длиной T секунд, начиная с off.

    Если окно не влезает в рабочую часть, начало сдвигается назад, а не
    склеивается с затуханием: лучше повтор куска, чем провал громкости.
    """
    x = track()
    a0, a1 = BODY
    a1 = min(a1, len(x) / SR)
    off = min(max(off, a0), max(a0, a1 - T))
    a = int(off * SR)
    n = int(T * SR)
    seg = x[a:a + n].copy()
    if len(seg) < n:
        need = n - len(seg)
        seg = np.concatenate([seg, x[int(a0 * SR):int(a0 * SR) + need]], axis=0)
    k = int(fade * SR)
    if k > 0:
        r = np.linspace(0, 1, k, dtype=np.float32)[:, None]
        seg[:k] *= r
        seg[-k:] *= r[::-1]
    return seg


def dress(bed, T, duck=None, lvl=1.0):
    """Вступление из фильтра, уход в конце, приглушение под голосом."""
    if bed.ndim == 1:
        bed = np.stack([bed, bed], axis=1)
    n = len(bed)
    g = ramp(n, [(0.0, 0.0), (0.8, 0.85), (2.0, 1.0),
                 (T - 2.4, 1.0), (T - 0.5, 0.8), (T, 0.0)])
    for a, dur in (duck or []):
        pts = [(0.0, 1.0), (max(0.0, a - 0.10), 1.0), (a, 0.42),
               (a + dur, 0.42), (min(T, a + dur + 0.18), 1.0), (T, 1.0)]
        pts = sorted({round(p, 3): v for p, v in pts if 0.0 <= p <= T}.items())
        g = np.minimum(g, ramp(n, pts))
    fc = ramp(n, [(0.0, 700.0), (1.6, 6000.0), (2.6, 18000.0),
                  (T - 2.0, 18000.0), (T, 2500.0)])
    out = np.zeros_like(bed)
    for c in (0, 1):
        out[:, c] = sweep(bed[:, c].astype(np.float32), fc) * g
    pk = float(np.max(np.abs(out))) or 1.0
    return (out / pk * 0.9 * lvl).astype(np.float32)

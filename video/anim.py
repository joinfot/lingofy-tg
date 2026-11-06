# -*- coding: utf-8 -*-
"""Живые фоны: каждый — бесшовная петля.

Рисовать фон заново в каждом кадре дорого, поэтому один раз считается
короткая петля, а кадры по ней ходят по кругу. Петля бесшовная по
построению: всё, что движется, за её длину проходит ровно целый период.
Считается в уменьшенном размере и растягивается — фон мягкий, на нём это
незаметно, зато быстро.
"""
import math

import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
SW, SH = 360, 640          # рабочий размер петли
LOOP = 36                  # кадров в петле

_cache = {}
_Y, _X = np.mgrid[0:SH, 0:SW].astype(np.float32)
_XN = _X / SW
_YN = _Y / SH
_CX, _CY = SW / 2, SH * 0.45
_DX, _DY = _X - _CX, _Y - _CY
_R = np.sqrt(_DX ** 2 + (_DY * 0.72) ** 2)
_A = np.arctan2(_DY, _DX)


def _mix(t, c0, c1):
    """t в диапазоне 0..1 -> цвет между двумя."""
    c0 = np.array(c0, np.float32)
    c1 = np.array(c1, np.float32)
    return c0[None, None, :] + (c1 - c0)[None, None, :] * t[:, :, None]


def _fin(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def f_rays(p, pal):
    """Лучи из центра, медленно вращаются."""
    base = _mix(np.clip(_R / (SW * 1.5), 0, 1), pal[0], pal[1])
    spokes = np.sin(_A * 18 + p * 2 * math.pi)
    base += (spokes > 0.55)[:, :, None] * 26.0
    glow = np.exp(-(_R / (SW * 0.55)) ** 2)
    base += glow[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.30
    return _fin(base)


def f_stripes(p, pal):
    """Косые полосы уезжают вбок."""
    s = np.sin((_XN * 7 + _YN * 4 + p) * 2 * math.pi)
    base = _mix(np.clip(_YN * 0.9, 0, 1), pal[0], pal[1])
    base += (s > 0.3)[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.18
    return _fin(base)


def f_bokeh(p, pal):
    """Размытые круги плывут вверх."""
    base = _mix(np.clip(_YN, 0, 1), pal[0], pal[1])
    rng = np.random.default_rng(7)
    add = np.zeros((SH, SW), np.float32)
    for _ in range(16):
        cx = rng.uniform(0, SW)
        r = rng.uniform(26, 70)
        y0 = rng.uniform(0, SH)
        cy = (y0 - p * SH * 0.6) % (SH + 200) - 100
        d = (_X - cx) ** 2 + (_Y - cy) ** 2
        add += np.exp(-d / (2 * r * r)) * rng.uniform(0.5, 1.0)
    base += add[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.42
    return _fin(base)


def f_tunnel(p, pal):
    """Кольца наезжают из глубины."""
    rings = np.sin((_R / 46 - p) * 2 * math.pi)
    base = _mix(np.clip(_R / (SW * 1.3), 0, 1), pal[1], pal[0])
    base += (rings > 0.45)[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.26
    return _fin(base)


def f_wave(p, pal):
    """Волны перекатываются снизу вверх."""
    v = np.sin((_YN * 5 - p) * 2 * math.pi + np.sin(_XN * 3 * math.pi) * 0.8)
    base = _mix((v + 1) / 2, pal[0], pal[1])
    base += (v > 0.85)[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.22
    return _fin(base)


def f_grid(p, pal):
    """Перспективная сетка уезжает к горизонту."""
    base = _mix(np.clip(_YN, 0, 1), pal[0], pal[1])
    hor = 0.42
    below = _YN > hor
    z = np.where(below, 1.0 / np.maximum(_YN - hor, 1e-3), 0.0)
    lines = np.sin((z * 0.9 + p) * 2 * math.pi)
    vx = np.sin((_XN - 0.5) * z * 0.55 * 2 * math.pi)
    g = ((lines > 0.80) | (vx > 0.985)) & below
    base += g[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.50
    return _fin(base)


def f_plasma(p, pal):
    """Плавное переливание."""
    a = np.sin(_XN * 4 * math.pi + p * 2 * math.pi)
    b = np.sin(_YN * 3 * math.pi - p * 2 * math.pi)
    c = np.sin((_XN + _YN) * 3 * math.pi + p * 2 * math.pi)
    v = (a + b + c) / 3
    base = _mix((v + 1) / 2, pal[0], pal[1])
    base += (v > 0.7)[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.20
    return _fin(base)


def f_dots(p, pal):
    """Точечная сетка пульсирует волной."""
    base = _mix(np.clip(_YN, 0, 1), pal[0], pal[1])
    gx = np.abs(((_X / 34) % 1) - 0.5)
    gy = np.abs(((_Y / 34) % 1) - 0.5)
    dot = (gx < 0.16) & (gy < 0.16)
    puls = (np.sin((_R / 120 - p) * 2 * math.pi) + 1) / 2
    base += (dot * puls)[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.75
    return _fin(base)


def f_aurora(p, pal):
    """Мягкие световые занавесы дрейфуют вбок."""
    base = _mix(np.clip(_YN, 0, 1), pal[0], pal[1])
    for k, sc in enumerate((1.0, 0.6)):
        band = np.exp(-(((_XN + np.sin(_YN * 2.2 * math.pi + p * 2 * math.pi + k) * 0.18)
                         - (0.35 + 0.3 * k)) ** 2) / 0.012)
        base += band[:, :, None] * np.array(pal[2], np.float32)[None, None, :] * 0.5 * sc
    return _fin(base)


KINDS = {"rays": f_rays, "stripes": f_stripes, "bokeh": f_bokeh,
         "tunnel": f_tunnel, "wave": f_wave, "grid": f_grid,
         "plasma": f_plasma, "dots": f_dots, "aurora": f_aurora}


def loop(kind, pal, blur=1.2):
    """Готовит петлю кадров фона (считается один раз на ролик)."""
    key = (kind, tuple(map(tuple, pal)), blur)
    if key in _cache:
        return _cache[key]
    fn = KINDS[kind]
    out = []
    for k in range(LOOP):
        im = Image.fromarray(fn(k / LOOP, pal), "RGB")
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        out.append(im)
    _cache[key] = out
    return out


def frame(kind, pal, k, blur=1.2):
    """Фон для кадра k — петля растягивается до полного размера."""
    return loop(kind, pal, blur)[k % LOOP].resize((W, H), Image.BILINEAR).convert("RGBA")

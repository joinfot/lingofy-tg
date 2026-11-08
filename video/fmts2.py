# -*- coding: utf-8 -*-
"""Пять форматов новой формулы: сначала узнавание, язык бонусом.

Что изменилось против старых форматов:

Первый кадр — сам предмет. Никаких заставок с темой: на нулевом кадре уже
висит табличка, факт или вопрос. Заставка съедала ту самую секунду, за
которую человек решает, листать дальше или нет.

Ролики короче — 25–40 секунд вместо шестидесяти. Содержания меньше, а
времени на каждый экран больше: читать успевают, а досматривают до конца
гораздо чаще.

Телеграм обещает выгоду, а не существует как подпись. Не «подпишись», а
«полный список там».

Длина каждого экрана по-прежнему считается от настоящей длительности
реплики, поэтому речь нигде не обрывается, а текст висит ровно столько,
сколько его читают.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

import acc
from acc import (H, W, FPS, background, ctext, fit, font, foot, lines, wrap)

RATE = {"de": 14.2, "ru": 15.5}

REAL = {}
try:
    import json as _json
    with open("/home/claude/voice_real.json") as _fh:
        REAL = _json.load(_fh)
except Exception:
    REAL = {}


def est(txt, lang):
    return len(txt) / RATE[lang] + 0.25


class Clock:
    """Длительность очередной реплики — настоящая, если озвучка уже нарезана."""

    def __init__(self, cfg):
        self.key = cfg.get("key", "")
        self.n = {"ru": 0, "de": 0}

    def take(self, txt, lang):
        i = self.n[lang]
        self.n[lang] += 1
        d = REAL.get(f"{self.key}|{lang}|{i}")
        return d + 0.12 if d is not None else est(txt, lang)


# ───────────────────────── общие детали ─────────────────────────

def bg(cfg, k):
    return background(cfg["th"], cfg["variant"], k)


def serial(d, cfg, i, n):
    """«2 / 5» наверху — обещание, что ролик досматривается до конца."""
    th = cfg["th"]
    ctext(d, W / 2, 96, f"{i + 1} / {n}", font(th["f_reg"], 40),
          th["ink"] + (170,))


def tg_frame(cfg, k, n=0):
    """Телеграм как выгода: что именно там лежит."""
    th = cfg["th"]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    p = acc.ease(min(1.0, k / (0.35 * FPS)))
    f, ls, s = fit(d, cfg["tg_hook"], th["f_bold"], 76, 48, W - 170, 3)
    y = lines(d, W / 2, 620, ls, f, th["ink"] + (int(255 * p),))
    ctext(d, W / 2, y + 60, "@lingofydeutsch", font(th["f_bold"], 86),
          th["accent"] + (int(255 * p),))
    ctext(d, W / 2, y + 190, "ссылка в профиле", font(th["f_reg"], 40),
          th["ink"] + (165,))
    return img


def outro_frame(cfg, k, n=0):
    th = cfg["th"]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    f, ls, s = fit(d, cfg["end"], th["f_bold"], 84, 50, W - 160, 3)
    y = lines(d, W / 2, 600, ls, f, th["ink"] + (255,))
    ctext(d, W / 2, y + 54, cfg["end_sub"], font(th["f_reg"], 46),
          th["ink"] + (195,))
    f2, ls2, s2 = fit(d, cfg["tg_hook"], th["f_semi"], 50, 34, W - 180, 3)
    y2 = lines(d, W / 2, 1180, ls2, f2, th["accent"] + (255,))
    ctext(d, W / 2, y2 + 30, "@lingofydeutsch", font(th["f_bold"], 78),
          th["ink"] + (255,))
    return img


def plate(img, d, text, cy, w, h, face, ink, border=None, radius=14,
          fkey=None, fmax=96, fmin=40):
    """Табличка: щит с полем, рамкой и текстом по центру."""
    x0, x1 = (W - w) / 2, (W + w) / 2
    y0, y1 = cy - h / 2, cy + h / 2
    d.rounded_rectangle((x0 + 8, y0 + 12, x1 + 8, y1 + 12), radius=radius,
                        fill=(0, 0, 0, 80))
    d.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=face + (255,))
    if border:
        d.rounded_rectangle((x0 + 12, y0 + 12, x1 - 12, y1 - 12),
                            radius=max(4, radius - 8), outline=border + (255,),
                            width=7)
    f, ls, s = fit(d, text, fkey, fmax, fmin, w - 110, 3)
    yy = cy - len(ls) * s * 0.62
    for l in ls:
        ctext(d, W / 2, yy, l, f, ink + (255,))
        yy += int(s * 1.18)


# ═════════════════════ D: «Что это значит?» ═════════════════════
# строка: (надпись, вид таблички, что значит, где висит, что сказать по-немецки)

SIGN_LOOK = {
    "blau": ((20, 62, 140), (255, 255, 255), (255, 255, 255)),
    "weiss": ((248, 248, 246), (22, 24, 28), (22, 24, 28)),
    "gelb": ((248, 206, 32), (26, 24, 16), (26, 24, 16)),
    "rot": ((198, 40, 38), (255, 255, 255), (255, 255, 255)),
    "gruen": ((28, 128, 78), (255, 255, 255), (255, 255, 255)),
}


def schild_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        # сама табличка — первое, что видно, без всякой заставки
        de = C.take(r[4], "de")
        ds = max(2.6, 0.45 + de + 0.75)
        ph.append(("s", i, ds))
        sl.append((t + 0.45, "de", r[4]))
        t += ds
        ru = C.take(r[2], "ru")
        dr = max(3.4, 0.30 + ru + 1.05)
        ph.append(("r", i, dr))
        sl.append((t + 0.30, "ru", r[2]))
        t += dr
        if i == n - 3:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.4))
    t += 3.4
    return ph, sl, t


def schild_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    look = SIGN_LOOK.get(r[1], SIGN_LOOK["weiss"])
    face, ink, border = look
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    n = len(cfg["rows"])
    serial(d, cfg, i, n)

    if kind == "s":
        plate(img, d, r[0], 900, W - 170, 520, face, ink, border,
              fkey=th["f_bold"], fmax=104, fmin=48)
        p = acc.ease(min(1.0, max(0.0, (k / FPS - 0.9) / 0.4)))
        ctext(d, W / 2, 1340, "Знаешь, что тут написано?",
              font(th["f_semi"], 52), th["ink"] + (int(220 * p),))
    else:
        plate(img, d, r[0], 700, W - 260, 360, face, ink, border,
              fkey=th["f_bold"], fmax=74, fmin=38)
        p = acc.ease(min(1.0, k / (0.35 * FPS)))
        f, ls, s = fit(d, r[2], th["f_bold"], 78, 46, W - 160, 3)
        y = lines(d, W / 2, 990, ls, f, th["accent"] + (int(255 * p),))
        q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.45) / 0.4)))
        f2, ls2, s2 = fit(d, r[3], th["f_reg"], 48, 32, W - 200, 3)
        lines(d, W / 2, y + 54, ls2, f2, th["ink"] + (int(210 * q),))
    foot(img, th, cfg.get('foot'))
    return img


# ═════════════════ E: «В Германии это нормально» ═════════════════
# строка: (факт, подробность, немецкое слово, перевод слова)

def kultur_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        ru = C.take(r[0], "ru")
        de = C.take(r[2], "de")
        df = max(5.0, 0.35 + ru + 0.35 + de + 1.15)
        ph.append(("f", i, df))
        sl.append((t + 0.35, "ru", r[0]))
        sl.append((t + 0.35 + ru + 0.35, "de", r[2]))
        t += df
        if i == n - 3:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.4))
    t += 3.4
    return ph, sl, t


def kultur_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    n = len(cfg["rows"])
    serial(d, cfg, i, n)

    ctext(d, W / 2, 300, cfg["badge"], font(th["f_semi"], 48),
          th["accent"] + (235,))
    p = acc.ease(min(1.0, k / (0.35 * FPS)))
    f, ls, s = fit(d, r[0], th["f_bold"], 92, 52, W - 150, 4)
    y = lines(d, W / 2, 540, ls, f, th["ink"] + (int(255 * p),))

    q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.7) / 0.45)))
    f2, ls2, s2 = fit(d, r[1], th["f_reg"], 52, 34, W - 180, 4)
    y2 = lines(d, W / 2, y + 70, ls2, f2, th["ink"] + (int(205 * q),))

    # немецкое слово — бонус, не главное: отдельной плашкой внизу
    z = acc.ease(min(1.0, max(0.0, (k / FPS - 1.3) / 0.45)))
    if z > 0.01:
        bw = W - 260
        box = ((W - bw) / 2, y2 + 60, (W + bw) / 2, y2 + 250)
        d.rounded_rectangle(box, radius=th["radius"],
                            fill=th["accent"] + (int(255 * z),))
        ctext(d, W / 2, y2 + 95, r[2], font(th["f_bold"], 62),
              th["on"] + (int(255 * z),))
        ctext(d, W / 2, y2 + 180, r[3], font(th["f_reg"], 42),
              th["on"] + (int(195 * z),))
    foot(img, th, cfg.get('foot'))
    return img


# ═══════════════ B: смешные и длинные немецкие слова ═══════════════
# строка: (слово, [части], дословно, что значит на самом деле)

def wort_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        de = C.take(r[0], "de")
        dw = max(2.2, 0.40 + de + 0.45)
        ph.append(("w", i, dw))
        sl.append((t + 0.40, "de", r[0]))
        t += dw
        ru = C.take(r[2], "ru")
        dl = max(2.6, 0.25 + ru + 0.55)
        ph.append(("l", i, dl))
        sl.append((t + 0.25, "ru", r[2]))
        t += dl
        ru2 = C.take(r[3], "ru")
        dm = max(2.8, 0.25 + ru2 + 0.70)
        ph.append(("m", i, dm))
        sl.append((t + 0.25, "ru", r[3]))
        t += dm
        if i == n - 3:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.4))
    t += 3.4
    return ph, sl, t


def wort_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    n = len(cfg["rows"])
    serial(d, cfg, i, n)

    # слово целиком — крупно, оно и есть крючок
    f, ls, s = fit(d, r[0], th["f_bold"], 110, 46, W - 140, 3)
    y = lines(d, W / 2, 540, ls, f, th["ink"] + (255,))

    if kind in ("l", "m"):
        # разбор на части: каждая со своим переводом
        p = acc.ease(min(1.0, k / (0.35 * FPS))) if kind == "l" else 1.0
        base = th["bg"][1][0]
        hl = acc.tint(th["accent"], base, 0.22)
        yy = y + 70
        fp = font(th["f_semi"], 54)
        ft = font(th["f_reg"], 40)
        for part, mean in r[1]:
            wpx = d.textlength(part, font=fp)
            d.rounded_rectangle((W / 2 - wpx / 2 - 26, yy - 12,
                                 W / 2 + wpx / 2 + 26, yy + 72),
                                radius=10, fill=hl + (int(255 * p),))
            ctext(d, W / 2, yy, part, fp, th["accent"] + (int(255 * p),))
            ctext(d, W / 2, yy + 84, mean, ft, th["ink"] + (int(195 * p),))
            yy += 150
        q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.5) / 0.4))) if kind == "l" else 1.0
        f3, ls3, s3 = fit(d, "дословно: " + r[2], th["f_semi"], 52, 34,
                          W - 180, 2)
        y3 = lines(d, W / 2, yy + 20, ls3, f3, th["ink"] + (int(225 * q),))
    else:
        ctext(d, W / 2, y + 90, "а что это такое?", font(th["f_reg"], 48),
              th["ink"] + (170,))
        y3 = y + 160

    if kind == "m":
        p = acc.ease(min(1.0, k / (0.4 * FPS)))
        bw = W - 200
        f4, ls4, s4 = fit(d, r[3], th["f_bold"], 68, 42, bw - 110, 3)
        bh = len(ls4) * int(s4 * 1.18) + 90
        box = ((W - bw) / 2, y3 + 50, (W + bw) / 2, y3 + 50 + bh)
        d.rounded_rectangle(box, radius=th["radius"],
                            fill=th["accent"] + (int(255 * p),))
        yy4 = y3 + 92
        for l in ls4:
            ctext(d, W / 2, yy4, l, f4, th["on"] + (int(255 * p),))
            yy4 += int(s4 * 1.18)
    foot(img, th, cfg.get('foot'))
    return img


# ════════════════════════ C: POV и сценки ════════════════════════
# строка: (что происходит, немецкая реплика, перевод)

def pov_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    # заголовок POV — но он уже и есть ситуация, не заставка
    ru0 = C.take(cfg["pov"], "ru")
    d0 = max(2.4, 0.30 + ru0 + 0.70)
    ph.append(("p", 0, d0))
    sl.append((0.30, "ru", cfg["pov"]))
    t += d0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        de = C.take(r[1], "de")
        ru = C.take(r[2], "ru")
        db = max(3.6, 0.30 + de + 0.25 + ru + 0.70)
        ph.append(("b", i, db))
        sl.append((t + 0.30, "de", r[1]))
        sl.append((t + 0.30 + de + 0.25, "ru", r[2]))
        t += db
        if i == n - 2:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.4))
    t += 3.4
    return ph, sl, t


def pov_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")

    if kind == "p":
        f, ls, s = fit(d, cfg["pov"], th["f_bold"], 96, 52, W - 150, 4)
        lines(d, W / 2, 740, ls, f, th["ink"] + (255,))
        p = acc.ease(min(1.0, max(0.0, (k / FPS - 0.8) / 0.4)))
        ctext(d, W / 2, 1180, cfg["pov_sub"], font(th["f_reg"], 46),
              th["ink"] + (int(200 * p),))
        foot(img, th, cfg.get('foot'))
        return img

    r = cfg["rows"][i]
    n = len(cfg["rows"])
    serial(d, cfg, i, n)
    ctext(d, W / 2, 210, cfg["pov"], font(th["f_reg"], 40), th["ink"] + (150,))

    # что происходит — ремаркой, реплика — крупно
    f0, ls0, s0 = fit(d, r[0], th["f_reg"], 48, 32, W - 200, 2)
    y = lines(d, W / 2, 520, ls0, f0, th["ink"] + (175,))

    p = acc.ease(min(1.0, k / (0.35 * FPS)))
    bw = W - 150
    fde = font(th["f_bold"], 62)
    lsd = wrap(d, r[1], fde, bw - 120)
    bh = len(lsd) * 78 + 80
    box = ((W - bw) / 2, y + 60, (W + bw) / 2, y + 60 + bh)
    d.rounded_rectangle(box, radius=th["radius"],
                        fill=th["accent"] + (int(245 * p),))
    yy = y + 100
    for l in lsd:
        ctext(d, W / 2, yy, l, fde, th["on"] + (int(255 * p),))
        yy += 78

    q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.6) / 0.45)))
    f2, ls2, s2 = fit(d, r[2], th["f_semi"], 54, 36, W - 200, 3)
    lines(d, W / 2, y + 60 + bh + 50, ls2, f2, th["ink"] + (int(225 * q),))
    foot(img, th, cfg.get('foot'))
    return img


# ═══════════════════ A: челленджи и угадайки ═══════════════════
# строка: (вопрос, [варианты], номер верного, пояснение, что сказать по-немецки)

def raten_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        ru = C.take(r[0], "ru")
        dq = max(3.2, 0.30 + ru + 1.30)
        ph.append(("q", i, dq))
        sl.append((t + 0.30, "ru", r[0]))
        t += dq
        de = C.take(r[4], "de")
        da = max(3.4, 0.45 + de + 1.05)
        ph.append(("a", i, da))
        sl.append((t + 0.45, "de", r[4]))
        t += da
        if i == n - 3:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.6))
    t += 3.6
    return ph, sl, t


def raten_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    rev = kind == "a"
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    n = len(cfg["rows"])
    serial(d, cfg, i, n)

    f, ls, s = fit(d, r[0], th["f_bold"], 86, 48, W - 150, 3)
    y = lines(d, W / 2, 330, ls, f, th["ink"] + (255,))

    opts = r[1]
    top = max(700, y + 140)
    gap = 190
    dim_fill = tuple(int(c * 0.28) for c in th["ink"])
    for j, opt in enumerate(opts):
        cy = top + j * gap
        right = rev and j == r[2]
        dim = rev and j != r[2]
        fill = th["accent"] if right else (dim_fill if dim else th["accent2"])
        d.rounded_rectangle((110, cy - 76, W - 110, cy + 76),
                            radius=th["radius"], fill=fill + (255,))
        ink = (th["ink"] + (145,)) if dim else (th["on"] + (255,))
        f2, ls2, s2 = fit(d, opt, th["f_semi"], 58, 34, W - 300, 2)
        yy = cy - len(ls2) * s2 * 0.60
        for l in ls2:
            ctext(d, W / 2, yy, l, f2, ink)
            yy += int(s2 * 1.16)

    if rev and r[3]:
        p = acc.ease(min(1.0, max(0.0, (k / FPS - 0.5) / 0.45)))
        f3, ls3, s3 = fit(d, r[3], th["f_reg"], 48, 32, W - 180, 3)
        lines(d, W / 2, top + len(opts) * gap + 20, ls3, f3,
              th["ink"] + (int(225 * p),))
    foot(img, th, cfg.get('foot'))
    return img


# ─────────────────────────── сборка ───────────────────────────

BUILD = {"schild": schild_build, "kultur": kultur_build, "wort": wort_build,
         "pov": pov_build, "raten": raten_build}
FRAME = {"schild": schild_frame, "kultur": kultur_frame, "wort": wort_frame,
         "pov": pov_frame, "raten": raten_frame}


def build(cfg):
    return BUILD[cfg["th"]["fmt"]](cfg)


def frames(phases):
    out = []
    for kind, i, dur in phases:
        for q in range(int(round(dur * FPS))):
            out.append((kind, i, q))
    return out


def draw(cfg, kind, i, k):
    return FRAME[cfg["th"]["fmt"]](cfg, kind, i, k)

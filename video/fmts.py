# -*- coding: utf-8 -*-
"""Пять форматов — по одному на аккаунт.

Общий договор у всех: build(cfg) возвращает фазы, места под озвучку и
длительность. Фаза — это (вид, номер, сколько секунд); из фаз раскатываются
кадры. Место под озвучку — (время, язык, текст), и оно же идёт в список на
генерацию в ElevenLabs, чтобы текст на экране и текст в озвучке не могли
разойтись: источник один.

Длина фазы считается из длительности её реплики. Пока озвучки нет, берётся
оценка по числу знаков; как только файлы нарезаны, подставляются настоящие
длительности из voice_real.json, и ни одна реплика не обрывается.
"""
import math

from PIL import ImageDraw

import acc
from acc import (H, W, FPS, background, ctext, fit, font, foot, lines)

# темп речи, замеренный по прошлым партиям ElevenLabs (знаков в секунду)
RATE = {"de": 14.2, "ru": 15.5}

REAL = {}
try:
    import json as _json
    with open("/home/claude/voice_real.json") as _fh:
        REAL = _json.load(_fh)
except Exception:
    REAL = {}


def est(txt, lang):
    """Грубая оценка длительности реплики по числу знаков."""
    return len(txt) / RATE[lang] + 0.25


class Clock:
    """Выдаёт длительность очередной реплики ролика на нужном языке.

    Считает реплики по порядку отдельно для каждого языка — ровно в том же
    порядке, в каком они уходили в ElevenLabs, поэтому номера сходятся сами
    собой, без сопоставления по тексту.
    """

    def __init__(self, cfg):
        self.key = cfg.get("key", "")
        self.n = {"ru": 0, "de": 0}

    def take(self, txt, lang):
        i = self.n[lang]
        self.n[lang] += 1
        d = REAL.get(f"{self.key}|{lang}|{i}")
        return d + 0.12 if d is not None else est(txt, lang)


# ─────────────────────────── общее ───────────────────────────

def bg(cfg, k):
    return background(cfg["th"], cfg["variant"], k)


def topline(d, cfg, txt, y=118):
    th = cfg["th"]
    ctext(d, W / 2, y, txt, font(th["f_reg"], 38), th["ink"] + (190,))


def intro_frame(cfg, k, n=0):
    """Общее вступление: тема по-русски и по-немецки."""
    th = cfg["th"]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    p = acc.ease(min(1.0, k / (0.5 * FPS)))
    f, ls, s = fit(d, cfg["hook"], th["f_bold"], 96, 54, W - 150, 3)
    y = lines(d, W / 2, 520, ls, f, th["ink"] + (int(255 * p),))
    f2, ls2, s2 = fit(d, cfg["hook_de"], th["f_semi"], 62, 38, W - 190, 2)
    q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.8) / 0.5)))
    lines(d, W / 2, y + 48, ls2, f2, th["accent"] + (int(255 * q),))
    ctext(d, W / 2, 1180, cfg["sub"], font(th["f_reg"], 44), th["ink"] + (200,))
    foot(img, th)
    return img


def tg_frame(cfg, k, n=0):
    th = cfg["th"]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    p = acc.ease(min(1.0, k / (0.4 * FPS)))
    ctext(d, W / 2, 700, "@lingofydeutsch", font(th["f_bold"], 82),
          th["ink"] + (int(255 * p),))
    f, ls, s = fit(d, th["tgline"], th["f_semi"], 56, 38, W - 200, 2)
    lines(d, W / 2, 830, ls, f, th["accent"] + (int(255 * p),))
    ctext(d, W / 2, 1010, "ссылка в профиле", font(th["f_reg"], 38),
          th["ink"] + (170,))
    return img


def outro_frame(cfg, k, n=0):
    th = cfg["th"]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    f, ls, s = fit(d, cfg["end"], th["f_bold"], 86, 50, W - 160, 3)
    y = lines(d, W / 2, 540, ls, f, th["ink"] + (255,))
    ctext(d, W / 2, y + 56, cfg["end_de"], font(th["f_semi"], 52),
          th["accent"] + (255,))
    ctext(d, W / 2, 1180, "@lingofydeutsch", font(th["f_bold"], 76),
          th["ink"] + (255,))
    ctext(d, W / 2, 1280, th["tgline"], font(th["f_reg"], 42), th["ink"] + (200,))
    return img


# ─────────────────────────── A: квиз ───────────────────────────
# строка: (вопрос, [три варианта], номер верного, пояснение, что сказать по-немецки)

QA = dict(tg=2.4, outro=4.0)


def quiz_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    ru0 = C.take(cfg["hook"], "ru")
    de0 = C.take(cfg["hook_de"], "de")
    d0 = max(4.6, 0.35 + ru0 + 0.25 + de0 + 0.45)
    ph.append(("i", 0, d0))
    sl += [(0.35, "ru", cfg["hook"]), (0.35 + ru0 + 0.25, "de", cfg["hook_de"])]
    t += d0
    half = len(cfg["rows"]) // 2
    for i, r in enumerate(cfg["rows"]):
        dq = C.take(r[0], "ru")
        da = max(3.6, 0.30 + dq + 0.60)
        ph.append(("a", i, da))
        sl.append((t + 0.30, "ru", r[0]))
        t += da
        dd = C.take(r[4], "de")
        ds = max(4.2, 0.55 + dd + 1.10)
        ph.append(("s", i, ds))
        sl.append((t + 0.55, "de", r[4]))
        t += ds
        if i == half - 1:
            ph.append(("g", 0, QA["tg"]))
            t += QA["tg"]
    ph.append(("o", 0, QA["outro"]))
    t += QA["outro"]
    return ph, sl, t


def quiz_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "i":
        return intro_frame(cfg, k)
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    rev = kind == "s"
    q = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    topline(d, cfg, f"{i+1} / {len(cfg['rows'])}")
    f, ls, s = fit(d, q[0], th["f_bold"], 74, 44, W - 170, 3)
    lines(d, W / 2, 250, ls, f, th["ink"] + (255,))

    top, gap, r = 700, 206, 76
    dim_fill = tuple(int(c * 0.30) for c in th["ink"])
    for j, opt in enumerate(q[1]):
        cy = top + j * gap
        right = rev and j == q[2]
        dim = rev and j != q[2]
        fill = th["accent"] if right else (dim_fill if dim else th["accent2"])
        d.ellipse((150 - r, cy - r, 150 + r, cy + r), fill=fill + (255,),
                  outline=th["ink"] + (210,), width=4)
        ctext(d, 150, cy - 40, "ABC"[j], font(th["f_bold"], 68),
              (th["ink"] if dim else th["on"]) + (255,))
        d.rounded_rectangle((252, cy - 72, W - 90, cy + 72),
                            radius=th["radius"], fill=fill + (255,))
        ink = (th["ink"] + (150,)) if dim else (th["on"] + (255,))
        f2, ls2, s2 = fit(d, opt, th["f_semi"], 54, 32, W - 400, 2)
        yy = cy - len(ls2) * s2 * 0.60
        for l in ls2:
            ctext(d, (252 + W - 90) / 2, yy, l, f2, ink)
            yy += int(s2 * 1.16)

    if rev and q[3]:
        f3, ls3, s3 = fit(d, q[3], th["f_reg"], 44, 30, W - 190, 2)
        lines(d, W / 2, 1420, ls3, f3, th["ink"] + (215,))
    foot(img, th)
    return img


# ─────────────────────────── B: разбор фразы ───────────────────────────
# строка: (фраза, перевод, [(кусок, подпись), ...])

PA = dict(part=1.7, tg=2.6, outro=4.0)


def parse_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    ru0 = C.take(cfg["hook"], "ru")
    de0 = C.take(cfg["hook_de"], "de")
    d0 = max(4.8, 0.40 + ru0 + 0.25 + de0 + 0.45)
    ph.append(("i", 0, d0))
    sl += [(0.40, "ru", cfg["hook"]), (0.40 + ru0 + 0.25, "de", cfg["hook_de"])]
    t += d0
    half = len(cfg["rows"]) // 2
    for i, r in enumerate(cfg["rows"]):
        dd = C.take(r[0], "de")
        dw = max(2.8, 0.35 + dd + 0.55)
        ph.append(("w", i, dw))
        sl.append((t + 0.35, "de", r[0]))
        t += dw
        for j in range(len(r[2])):
            ph.append((f"p{j}", i, PA["part"]))
            t += PA["part"]
        dr = C.take(r[1], "ru")
        dt = max(2.6, 0.35 + dr + 0.60)
        ph.append(("t", i, dt))
        sl.append((t + 0.35, "ru", r[1]))
        t += dt
        if i == half - 1:
            ph.append(("g", 0, PA["tg"]))
            t += PA["tg"]
    ph.append(("o", 0, PA["outro"]))
    t += PA["outro"]
    return ph, sl, t


def parse_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "i":
        return intro_frame(cfg, k)
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    parts = r[2]
    step = -1 if kind in ("w", "t") else int(kind[1:])
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    topline(d, cfg, f"фраза {i+1} из {len(cfg['rows'])}")

    f = font(th["f_bold"], 70)
    chunks = [p[0] for p in parts]
    sp = d.textlength(" ", font=f)
    rows_, cur, curw = [], [], 0.0
    for c in chunks:
        wd = d.textlength(c, font=f)
        if curw + wd > W - 220 and cur:
            rows_.append((cur, curw))
            cur, curw = [], 0.0
        cur.append((c, wd))
        curw += wd + sp
    if cur:
        rows_.append((cur, curw))

    base = th["bg"][1][0]
    hl = acc.tint(th["accent"], base, 0.26)
    y = 620
    idx = 0
    boxes = {}
    for rw, rww in rows_:
        x = (W - (rww - sp)) / 2
        for c, wd in rw:
            on = (idx == step)
            if on:
                d.rounded_rectangle((x - 14, y - 10, x + wd + 14, y + 80),
                                    radius=8, fill=hl + (255,))
            d.text((x, y), c, font=f,
                   fill=(th["accent"] if on else th["ink"]) + (255,))
            boxes[idx] = (x + wd / 2, y + 86)
            x += wd + sp
            idx += 1
        y += 104

    # подпись всегда под всей фразой, иначе она налезает на вторую строку
    low = y + 24
    if step >= 0 and step in boxes:
        cx, by = boxes[step]
        d.line((cx, by, cx, low - 8), fill=th["accent"] + (255,), width=4)
        f2, ls2, s2 = fit(d, parts[step][1], th["f_semi"], 50, 32, W - 220, 2)
        lines(d, W / 2, low + 8, ls2, f2, th["accent"] + (255,))

    if kind == "t":
        d.line((180, low + 10, W - 180, low + 10),
               fill=th["accent"] + (160,), width=3)
        f3, ls3, s3 = fit(d, r[1], th["f_semi"], 58, 36, W - 200, 3)
        lines(d, W / 2, low + 48, ls3, f3, th["ink"] + (235,))
    foot(img, th)
    return img


# ─────────────────────────── C: переписка ───────────────────────────
# строка: (кто 0/1, немецкая реплика, перевод)

CA = dict(tg=2.4, outro=3.8)


def chat_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    ru0 = C.take(cfg["hook"], "ru")
    de0 = C.take(cfg["hook_de"], "de")
    d0 = max(4.6, 0.30 + ru0 + 0.25 + de0 + 0.45)
    ph.append(("i", 0, d0))
    sl += [(0.30, "ru", cfg["hook"]), (0.30 + ru0 + 0.25, "de", cfg["hook_de"])]
    t += d0
    half = len(cfg["rows"]) // 2
    for i, r in enumerate(cfg["rows"]):
        de_ = C.take(r[1], "de")
        ru_ = C.take(r[2], "ru")
        dl = max(3.4, 0.25 + de_ + 0.20 + ru_ + 0.40)
        ph.append(("l", i, dl))
        sl.append((t + 0.25, "de", r[1]))
        sl.append((t + 0.25 + de_ + 0.20, "ru", r[2]))
        t += dl
        if i == half - 1:
            ph.append(("g", 0, CA["tg"]))
            t += CA["tg"]
    ph.append(("o", 0, CA["outro"]))
    t += CA["outro"]
    return ph, sl, t


def chat_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "i":
        return intro_frame(cfg, k)
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    topline(d, cfg, cfg["title"])

    # показываем последние пять реплик, свежая — внизу, с появлением
    first = max(0, i - 4)
    shown = cfg["rows"][first:i + 1]
    fde = font(th["f_bold"], 42)
    fru = font(th["f_reg"], 34)
    mw = W - 300

    # стопка прижата к низу, как в мессенджере: свежая реплика всегда на
    # одном месте, а не уезжает вниз по мере разговора
    meas = []
    for r in shown:
        lsd = acc.wrap(d, r[1], fde, mw)
        lsr = acc.wrap(d, r[2], fru, mw)
        bw = max([d.textlength(l, font=fde) for l in lsd] +
                 [d.textlength(l, font=fru) for l in lsr]) + 72
        bh = len(lsd) * 52 + len(lsr) * 44 + 50
        meas.append((lsd, lsr, bw, bh))
    total = sum(m[3] for m in meas) + 26 * (len(meas) - 1)
    y = max(300, 1560 - total)

    for j, r in enumerate(shown):
        who = r[0]
        new = (first + j) == i
        p = acc.ease(min(1.0, k / (0.35 * FPS))) if new else 1.0
        lsd, lsr, bw, bh = meas[j]
        x0 = 90 if who == 0 else W - 90 - bw
        col = th["accent2"] if who == 0 else th["accent"]
        ink = th["ink"] if who == 0 else th["on"]
        off = int((1 - p) * 40)
        d.rounded_rectangle((x0, y + off, x0 + bw, y + bh + off),
                            radius=th["radius"], fill=col + (int(235 * p),))
        yy = y + 22 + off
        for l in lsd:
            d.text((x0 + 36, yy), l, font=fde, fill=ink + (int(255 * p),))
            yy += 52
        for l in lsr:
            d.text((x0 + 36, yy + 6), l, font=fru, fill=ink + (int(185 * p),))
            yy += 44
        y += bh + 26
    foot(img, th)
    return img


# ─────────────────────────── D: ошибка → верно ───────────────────────────
# строка: (неверно, верно, пояснение)

DA = dict(wrong=2.6, tg=2.2, outro=3.6)


def fix_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    ru0 = C.take(cfg["hook"], "ru")
    de0 = C.take(cfg["hook_de"], "de")
    d0 = max(4.6, 0.30 + ru0 + 0.25 + de0 + 0.45)
    ph.append(("i", 0, d0))
    sl += [(0.30, "ru", cfg["hook"]), (0.30 + ru0 + 0.25, "de", cfg["hook_de"])]
    t += d0
    half = len(cfg["rows"]) // 2
    for i, r in enumerate(cfg["rows"]):
        ph.append(("w", i, DA["wrong"]))
        t += DA["wrong"]
        dd = C.take(r[1], "de")
        dr_ = max(3.2, 0.40 + dd + 0.75)
        ph.append(("r", i, dr_))
        sl.append((t + 0.40, "de", r[1]))
        t += dr_
        dn_ = C.take(r[2], "ru")
        dn = max(2.6, 0.20 + dn_ + 0.60)
        ph.append(("n", i, dn))
        sl.append((t + 0.20, "ru", r[2]))
        t += dn
        if i == half - 1:
            ph.append(("g", 0, DA["tg"]))
            t += DA["tg"]
    ph.append(("o", 0, DA["outro"]))
    t += DA["outro"]
    return ph, sl, t


def fix_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "i":
        return intro_frame(cfg, k)
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    topline(d, cfg, f"{i+1} / {len(cfg['rows'])}")

    d.rectangle((84, 430, W - 84, 640), fill=th["accent"] + (255,))
    f, ls, s = fit(d, r[0], th["f_bold"], 62, 38, W - 240, 2)
    yy = 470 if len(ls) > 1 else 500
    y0 = yy
    for l in ls:
        ctext(d, W / 2, yy, l, f, th["on"] + (255,))
        yy += int(s * 1.16)
    if kind in ("r", "n"):
        p = acc.ease(min(1.0, k / (0.35 * FPS))) if kind == "r" else 1.0
        ymid = y0 + (yy - y0) / 2 + s * 0.12
        d.line((128, ymid, 128 + (W - 256) * p, ymid),
               fill=th["on"] + (255,), width=7)
        ctext(d, W / 2, 352, "так не говорят", font(th["f_reg"], 40),
              th["accent"] + (255,))
    else:
        ctext(d, W / 2, 352, "как сказал бы ты?", font(th["f_reg"], 40),
              th["ink"] + (170,))

    if kind in ("r", "n"):
        p = acc.ease(min(1.0, k / (0.4 * FPS))) if kind == "r" else 1.0
        d.rectangle((84, 790, W - 84, 1010), fill=th["accent2"] + (int(255 * p),))
        ctext(d, W / 2, 716, "правильно", font(th["f_reg"], 40),
              th["accent2"] + (int(255 * p),))
        f2, ls2, s2 = fit(d, r[1], th["f_bold"], 66, 40, W - 240, 2)
        yy2 = 836 if len(ls2) > 1 else 866
        for l in ls2:
            ctext(d, W / 2, yy2, l, f2, th["on"] + (int(255 * p),))
            yy2 += int(s2 * 1.16)

    if kind == "n":
        f3, ls3, s3 = fit(d, r[2], th["f_reg"], 46, 32, W - 220, 3)
        lines(d, W / 2, 1120, ls3, f3, th["ink"] + (225,))
    foot(img, th)
    return img


# ─────────────────────────── E: карточки ───────────────────────────
# строка: (слово, перевод, пример, перевод примера)

EA = dict(flip=0.5, tg=2.4, outro=4.2)


def card_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    ru0 = C.take(cfg["hook"], "ru")
    de0 = C.take(cfg["hook_de"], "de")
    d0 = max(4.6, 0.35 + ru0 + 0.25 + de0 + 0.45)
    ph.append(("i", 0, d0))
    sl += [(0.35, "ru", cfg["hook"]), (0.35 + ru0 + 0.25, "de", cfg["hook_de"])]
    t += d0
    half = len(cfg["rows"]) // 2
    for i, r in enumerate(cfg["rows"]):
        dwd = C.take(r[0], "de")
        dw = max(2.6, 0.30 + dwd + 0.90)
        ph.append(("w", i, dw))
        sl.append((t + 0.30, "de", r[0]))
        t += dw
        ph.append(("f", i, EA["flip"]))
        t += EA["flip"]
        ru_ = C.take(r[1], "ru")
        ex_ = C.take(r[2], "de")
        db = max(4.4, 0.20 + ru_ + 0.30 + ex_ + 0.70)
        ph.append(("b", i, db))
        sl.append((t + 0.20, "ru", r[1]))
        sl.append((t + 0.20 + ru_ + 0.30, "de", r[2]))
        t += db
        if i == half - 1:
            ph.append(("g", 0, EA["tg"]))
            t += EA["tg"]
    ph.append(("o", 0, EA["outro"]))
    t += EA["outro"]
    return ph, sl, t


def card_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "i":
        return intro_frame(cfg, k)
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    topline(d, cfg, f"карточка {i+1} из {len(cfg['rows'])}")

    # переворот: карточка сжимается по ширине и раскрывается другой стороной
    if kind == "f":
        p = k / max(1, int(EA["flip"] * FPS))
        sx = abs(math.cos(p * math.pi))
        face_back = p > 0.5
    else:
        sx = 1.0
        face_back = kind == "b"
    cw, chh = (W - 200), 760
    cx, cy = W / 2, 880
    bw = max(12, cw * sx)
    box = (cx - bw / 2, cy - chh / 2, cx + bw / 2, cy + chh / 2)
    fill = th["accent"] if face_back else (255, 255, 255)
    d.rounded_rectangle((box[0] + 10, box[1] + 16, box[2] + 10, box[3] + 16),
                        radius=th["radius"], fill=(0, 0, 0, 70))
    d.rounded_rectangle(box, radius=th["radius"], fill=fill + (255,))
    if sx < 0.55:
        foot(img, th)
        return img

    ink = th["on"]
    if not face_back:
        f, ls, s = fit(d, r[0], th["f_bold"], 96, 54, bw - 140, 2)
        lines(d, cx, cy - len(ls) * s * 0.6, ls, f, ink + (255,))
        ctext(d, cx, cy + 220, "что это значит?", font(th["f_reg"], 40),
              ink + (150,))
    else:
        f, ls, s = fit(d, r[1], th["f_bold"], 84, 48, bw - 140, 2)
        y = lines(d, cx, cy - 250, ls, f, ink + (255,))
        d.line((cx - 180, y + 24, cx + 180, y + 24), fill=ink + (110,), width=3)
        f2, ls2, s2 = fit(d, r[2], th["f_semi"], 56, 34, bw - 150, 3)
        y2 = lines(d, cx, y + 64, ls2, f2, ink + (240,))
        f3, ls3, s3 = fit(d, r[3], th["f_reg"], 44, 28, bw - 150, 2)
        lines(d, cx, y2 + 22, ls3, f3, ink + (165,))
    foot(img, th)
    return img


# ─────────────────────────── сборка ───────────────────────────

BUILD = {"quiz": quiz_build, "parse": parse_build, "chat": chat_build,
         "fix": fix_build, "card": card_build}
FRAME = {"quiz": quiz_frame, "parse": parse_frame, "chat": chat_frame,
         "fix": fix_frame, "card": card_frame}


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

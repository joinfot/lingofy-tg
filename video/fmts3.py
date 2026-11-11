# -*- coding: utf-8 -*-
"""Три новых формата к пяти проверенным: fmts3.py

За неделю каждый из пяти форматов вышел бы по двадцать раз, и лента
стала бы однообразной. Эти три добавляются к старым, а не заменяют их:
старые пять работают и импортируются отсюда как есть.

    mythos  — «Правда или миф» (аккаунт A к угадайкам)
    kuerzel — «Расшифруй сокращение» (аккаунт D к табличкам)
    anders  — «В учебнике так, а говорят так» (аккаунт B к словам)

Правила те же: первый кадр — сам предмет, 25–40 секунд, телеграм через
выгоду.

Отдельно про «anders»: формат НЕ про ошибки. Книжная фраза и живая обе
верны, разница в регистре и обстановке, и пояснение говорит именно это.
Назвать правильную фразу ошибкой нельзя — на этом канал теряет доверие
быстрее, чем набирает просмотры.
"""
from PIL import ImageDraw

import acc
from acc import H, W, FPS, ctext, fit, font, foot, lines
from fmts2 import (BUILD, FRAME, Clock, bg, est, frames, outro_frame, plate,
                   serial, tg_frame)

# ════════════════════ A: «Правда или миф» ════════════════════
# строка: (утверждение, правда ли, разбор, как это звучит по-немецки)

STAMP = {True: ("ПРАВДА", (34, 150, 94)), False: ("МИФ", (198, 54, 48))}


def mythos_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        ru = C.take(r[0], "ru")
        dm = max(3.4, 0.30 + ru + 1.25)
        ph.append(("m", i, dm))
        sl.append((t + 0.30, "ru", r[0]))
        t += dm
        de = C.take(r[3], "de")
        dv = max(4.0, 0.55 + de + 1.60)
        ph.append(("v", i, dv))
        sl.append((t + 0.55, "de", r[3]))
        t += dv
        if i == n - 3:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.6))
    t += 3.6
    return ph, sl, t


def mythos_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    serial(d, cfg, i, len(cfg["rows"]))

    # утверждение висит на обоих кадрах: его перечитывают, пока думают
    f, ls, s = fit(d, r[0], th["f_bold"], 84, 48, W - 150, 4)
    y = lines(d, W / 2, 360, ls, f, th["ink"] + (255,))

    if kind == "m":
        p = acc.ease(min(1.0, max(0.0, (k / FPS - 0.8) / 0.4)))
        ctext(d, W / 2, 1180, "Правда или миф?", font(th["f_semi"], 60),
              th["ink"] + (int(225 * p),))
    else:
        word, col = STAMP[bool(r[1])]
        # штамп выезжает снизу и чуть пружинит — это и есть момент ответа
        p = acc.ease(min(1.0, k / (0.30 * FPS)))
        fs = font(th["f_bold"], 128)
        wv = d.textlength(word, font=fs)
        bw, bh = wv + 110, 190
        cy = 880 + int((1 - p) * 70)
        d.rounded_rectangle(((W - bw) / 2, cy - bh / 2,
                             (W + bw) / 2, cy + bh / 2),
                            radius=20, fill=col + (int(255 * p),))
        ctext(d, W / 2, cy - 64, word, fs, (255, 255, 255, int(255 * p)))
        q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.45) / 0.45)))
        f2, ls2, s2 = fit(d, r[2], th["f_reg"], 50, 34, W - 180, 4)
        y2 = lines(d, W / 2, 1120, ls2, f2, th["ink"] + (int(215 * q),))
        f3, ls3, s3 = fit(d, r[3], th["f_semi"], 46, 32, W - 220, 2)
        lines(d, W / 2, y2 + 56, ls3, f3, th["accent"] + (int(235 * q),))
    foot(img, th, cfg.get("foot"))
    return img


# ═════════════════ D: «Расшифруй сокращение» ═════════════════
# строка: (сокращение, полное немецкое, перевод, где встречается)

def kuerzel_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        # первый кадр молчит: пауза, в которую человек успевает угадать
        ph.append(("k", i, 2.3))
        t += 2.3
        de = C.take(r[1], "de")
        ru = C.take(f"{r[2]}. {r[3]}", "ru")
        dd = max(4.6, 0.40 + de + 0.30 + ru + 1.15)
        ph.append(("d", i, dd))
        sl.append((t + 0.40, "de", r[1]))
        sl.append((t + 0.40 + de + 0.30, "ru", f"{r[2]}. {r[3]}"))
        t += dd
        if i == n - 3:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.4))
    t += 3.4
    return ph, sl, t


def kuerzel_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    serial(d, cfg, i, len(cfg["rows"]))

    if kind == "k":
        # сокращение во весь экран: его узнают раньше, чем прочитают
        plate(img, d, r[0], 860, W - 230, 430, (248, 248, 246), (22, 24, 28),
              (22, 24, 28), fkey=th["f_bold"], fmax=200, fmin=96)
        p = acc.ease(min(1.0, max(0.0, (k / FPS - 0.7) / 0.4)))
        ctext(d, W / 2, 1300, "Знаешь, что это?", font(th["f_semi"], 54),
              th["ink"] + (int(220 * p),))
    else:
        plate(img, d, r[0], 700, W - 420, 260, (248, 248, 246), (22, 24, 28),
              (22, 24, 28), fkey=th["f_bold"], fmax=120, fmin=64)
        p = acc.ease(min(1.0, k / (0.32 * FPS)))
        f, ls, s = fit(d, r[1], th["f_bold"], 72, 42, W - 160, 2)
        y = lines(d, W / 2, 980, ls, f, th["accent"] + (int(255 * p),))
        q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.35) / 0.4)))
        f2, ls2, s2 = fit(d, r[2], th["f_bold"], 66, 42, W - 170, 2)
        y2 = lines(d, W / 2, y + 48, ls2, f2, th["ink"] + (int(255 * q),))
        w = acc.ease(min(1.0, max(0.0, (k / FPS - 0.75) / 0.45)))
        f3, ls3, s3 = fit(d, r[3], th["f_reg"], 46, 32, W - 200, 3)
        lines(d, W / 2, y2 + 56, ls3, f3, th["ink"] + (int(200 * w),))
    foot(img, th, cfg.get("foot"))
    return img


# ═══════════ B: «В учебнике так, а говорят так» ═══════════
# строка: (ситуация, книжная фраза, живая фраза, в чём разница)

def anders_build(cfg):
    ph, sl = [], []
    C = Clock(cfg)
    t = 0.0
    n = len(cfg["rows"])
    for i, r in enumerate(cfg["rows"]):
        de = C.take(r[1], "de")
        db = max(3.2, 0.40 + de + 0.85)
        ph.append(("b", i, db))
        sl.append((t + 0.40, "de", r[1]))
        t += db
        de2 = C.take(r[2], "de")
        ru = C.take(r[3], "ru")
        # книжная фраза уже прочитана на прошлом кадре, поэтому хвост короче
        dl = max(4.4, 0.35 + de2 + 0.30 + ru + 0.85)
        ph.append(("l", i, dl))
        sl.append((t + 0.35, "de", r[2]))
        sl.append((t + 0.35 + de2 + 0.30, "ru", r[3]))
        t += dl
        if i == n - 3:
            ph.append(("g", 0, 2.4))
            t += 2.4
    ph.append(("o", 0, 3.5))
    t += 3.5
    return ph, sl, t


def anders_frame(cfg, kind, i, k):
    th = cfg["th"]
    if kind == "g":
        return tg_frame(cfg, k)
    if kind == "o":
        return outro_frame(cfg, k)
    r = cfg["rows"][i]
    img = bg(cfg, k)
    d = ImageDraw.Draw(img, "RGBA")
    serial(d, cfg, i, len(cfg["rows"]))

    ctext(d, W / 2, 300, r[0], font(th["f_semi"], 50), th["ink"] + (200,))

    # обе фразы на своих местах: сверху книжная, снизу живая
    lab = font(th["f_reg"], 40)
    ctext(d, W / 2, 470, "в учебнике", lab, th["ink"] + (150,))
    f, ls, s = fit(d, r[1], th["f_bold"], 70, 42, W - 170, 3)
    y = lines(d, W / 2, 540, ls, f, th["ink"] + (255 if kind == "b" else 130,))

    if kind == "b":
        p = acc.ease(min(1.0, max(0.0, (k / FPS - 0.9) / 0.4)))
        ctext(d, W / 2, 1210, "а в жизни?", font(th["f_semi"], 56),
              th["ink"] + (int(220 * p),))
    else:
        p = acc.ease(min(1.0, k / (0.32 * FPS)))
        ctext(d, W / 2, y + 90, "а говорят", lab,
              th["ink"] + (int(170 * p),))
        f2, ls2, s2 = fit(d, r[2], th["f_bold"], 78, 46, W - 160, 3)
        y2 = lines(d, W / 2, y + 160, ls2, f2,
                   th["accent"] + (int(255 * p),))
        q = acc.ease(min(1.0, max(0.0, (k / FPS - 0.5) / 0.45)))
        f3, ls3, s3 = fit(d, r[3], th["f_reg"], 46, 32, W - 190, 4)
        lines(d, W / 2, y2 + 70, ls3, f3, th["ink"] + (int(205 * q),))
    foot(img, th, cfg.get("foot"))
    return img


# ─────────────────────────── сборка ───────────────────────────
# старые пять приходят из fmts2 и работают как раньше

BUILD = dict(BUILD, mythos=mythos_build, kuerzel=kuerzel_build,
             anders=anders_build)
FRAME = dict(FRAME, mythos=mythos_frame, kuerzel=kuerzel_frame,
             anders=anders_frame)


def build(cfg):
    return BUILD[cfg["th"]["fmt"]](cfg)


def draw(cfg, kind, i, k):
    return FRAME[cfg["th"]["fmt"]](cfg, kind, i, k)

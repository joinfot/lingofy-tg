# -*- coding: utf-8 -*-
"""Пять аккаунтов: оформление, шрифты, фон, место в треке, голоса.

Задача была не «пятнадцать разных роликов», а «пять разных каналов по три
ролика». Поэтому различается не всё подряд, а уровнями:

  между аккаунтами — формат (что вообще происходит на экране), шрифт,
  палитра, геометрия, тип фона, длительность, пара голосов;

  внутри аккаунта — тема и содержание, оттенок акцента и вариант фона;
  шрифт, формат и геометрия остаются, чтобы канал был узнаваем.

Шрифты отобраны по покрытию: кириллица и умляуты должны быть в одном
файле, иначе русский текст выпадет в квадраты. Poppins, Caladea и
TeX Gyre Heros Cn по этой причине не подошли, хотя внешне годились.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30

F = {
    "inter_black": "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
    "inter_semi": "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf",
    "inter_med": "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf",
    "lora_bold": "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf#Bold",
    "lora_reg": "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf#Regular",
    "lora_semi": "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf#SemiBold",
    "mono_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "mono_reg": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "cond_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "cond_reg": "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
    "lib_bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "lib_reg": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
}

_fc = {}


def font(key, size):
    """Шрифт по ключу. Запись «путь#Начертание» — вариативный шрифт."""
    path = F.get(key, key)
    ck = (path, size)
    if ck in _fc:
        return _fc[ck]
    if "#" in path:
        p, inst = path.split("#", 1)
        f = ImageFont.truetype(p, size)
        f.set_variation_by_name(inst)
    else:
        f = ImageFont.truetype(path, size)
    _fc[ck] = f
    return f


def tint(col, base, a):
    """Светлая подложка цвета col на фоне base.

    Прозрачную заливку с малой альфой PIL кое-где рисует непрозрачной, и
    текст поверх пропадает. Поэтому смешиваем цвета заранее и кладём
    сплошным — результат предсказуем.
    """
    return tuple(int(base[i] + (col[i] - base[i]) * a) for i in range(3))


# ─────────────────────────── текст ───────────────────────────

def wrap(d, txt, f, mw):
    out, line = [], ""
    for w_ in txt.split():
        t = (line + " " + w_).strip()
        if d.textlength(t, font=f) <= mw or not line:
            line = t
        else:
            out.append(line)
            line = w_
    if line:
        out.append(line)
    return out


def fit(d, txt, key, mx, mn, mw, max_lines=2, step=2):
    """Подбирает кегль так, чтобы текст влез в mw и в max_lines строк."""
    s = mx
    while s > mn:
        f = font(key, s)
        ls = wrap(d, txt, f, mw)
        if len(ls) <= max_lines:
            return f, ls, s
        s -= step
    f = font(key, mn)
    return f, wrap(d, txt, f, mw)[:max_lines], mn


def ctext(d, cx, y, txt, f, col):
    b = d.textbbox((0, 0), txt, font=f)
    d.text((cx - (b[2] - b[0]) / 2 - b[0], y), txt, font=f, fill=col)


def lines(d, cx, y, ls, f, col, lh=1.18):
    s = f.size
    for l in ls:
        ctext(d, cx, y, l, f, col)
        y += int(s * lh)
    return y


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ─────────────────────────── фоны ───────────────────────────

def solid(pal, variant=0):
    """Статичный фон: мягкие пятна поверх основного цвета."""
    ck = ("solid", tuple(map(tuple, pal)), variant)
    if ck in _fc:
        return _fc[ck]
    img = Image.new("RGB", (W, H), pal[0])
    d = ImageDraw.Draw(img)
    spots = [
        [(-200, -300, 760, 560), (520, 1380, 1480, 2200)],
        [(600, -260, 1500, 540), (-300, 1200, 560, 2000)],
        [(-250, 500, 620, 1300), (560, -200, 1420, 640)],
    ][variant % 3]
    for box in spots:
        d.ellipse(box, fill=pal[1])
    img = img.filter(ImageFilter.GaussianBlur(190))
    _fc[ck] = img
    return img


def paper(pal, variant=0):
    """Фон «бумага»: тёплая основа, линовка и мягкая тень по краям."""
    ck = ("paper", tuple(map(tuple, pal)), variant)
    if ck in _fc:
        return _fc[ck]
    img = Image.new("RGB", (W, H), pal[0])
    d = ImageDraw.Draw(img)
    step = (74, 92, 110)[variant % 3]
    for y in range(240, H - 180, step):
        d.line((88, y, W - 88, y), fill=pal[1], width=2)
    d.line((150, 150, 150, H - 150), fill=pal[2], width=3)
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).rectangle((60, 60, W - 60, H - 60), fill=120)
    vig = vig.filter(ImageFilter.GaussianBlur(70))
    img = Image.composite(img, Image.new("RGB", (W, H), pal[3]), vig)
    _fc[ck] = img
    return img


def grid(pal, variant=0):
    """Тёмный фон с еле заметной сеткой — под переписку."""
    ck = ("grid", tuple(map(tuple, pal)), variant)
    if ck in _fc:
        return _fc[ck]
    img = Image.new("RGB", (W, H), pal[0])
    d = ImageDraw.Draw(img)
    step = (60, 72, 90)[variant % 3]
    for x in range(0, W, step):
        d.line((x, 0, x, H), fill=pal[1], width=1)
    for y in range(0, H, step):
        d.line((0, y, W, y), fill=pal[1], width=1)
    glow = Image.new("RGB", (W, H), pal[0])
    ImageDraw.Draw(glow).ellipse((-240, 260, 1320, 1500), fill=pal[2])
    glow = glow.filter(ImageFilter.GaussianBlur(240))
    img = Image.blend(img, glow, 0.45)
    _fc[ck] = img
    return img


# ─────────────────────────── плашка канала ───────────────────────────

def foot(img, th, txt=None):
    """Строка канала внизу. Форма и цвет — свои на каждый аккаунт."""
    d = ImageDraw.Draw(img, "RGBA")
    y = H - 168
    st = th["footstyle"]
    label = "@lingofydeutsch"
    sub = txt or th["tgline"]
    if st == "pill":
        d.rounded_rectangle((110, y, W - 110, y + 112), radius=56,
                            fill=th["ink"] + (235,))
        ctext(d, W / 2, y + 16, label, font(th["f_bold"], 46), th["on"] + (255,))
        ctext(d, W / 2, y + 68, sub, font(th["f_reg"], 28), th["on"] + (190,))
    elif st == "rule":
        d.line((150, y - 6, W - 150, y - 6), fill=th["accent"] + (255,), width=4)
        ctext(d, W / 2, y + 14, label, font(th["f_bold"], 48), th["ink"] + (255,))
        ctext(d, W / 2, y + 72, sub, font(th["f_reg"], 28), th["ink"] + (170,))
    elif st == "tag":
        bw = 560
        d.rectangle((W / 2 - bw / 2, y, W / 2 + bw / 2, y + 60),
                    fill=th["accent"] + (255,))
        ctext(d, W / 2, y + 8, label, font(th["f_bold"], 42), th["on"] + (255,))
        ctext(d, W / 2, y + 76, sub, font(th["f_reg"], 28), th["ink"] + (190,))
    elif st == "box":
        d.rounded_rectangle((120, y - 4, W - 120, y + 116), radius=22,
                            outline=th["accent"] + (255,), width=4)
        ctext(d, W / 2, y + 12, label, font(th["f_bold"], 46), th["ink"] + (255,))
        ctext(d, W / 2, y + 70, sub, font(th["f_reg"], 28), th["ink"] + (175,))
    else:                                     # plain
        ctext(d, W / 2, y + 10, label, font(th["f_bold"], 50), th["ink"] + (255,))
        ctext(d, W / 2, y + 74, sub, font(th["f_reg"], 29), th["ink"] + (165,))


# ─────────────────────────── аккаунты ───────────────────────────
# bg: ("solid"|"paper"|"grid"|"anim:<вид>", палитра)
# on: цвет текста поверх заливки акцентом или чернилами
# voice: (id русского, имя, id немецкого, имя) — одна пара на аккаунт,
#        чтобы три ролика канала звучали одним и тем же человеком

ACC = {
    "A": {
        "brand": 6620452, "handle": "lingofy.deutsch",
        "fmt": "quiz", "mus_off": 12.0,
        "f_bold": "inter_black", "f_semi": "inter_semi", "f_reg": "inter_med",
        "bg": ("anim:aurora", [(18, 20, 52), (40, 34, 96), (120, 160, 255)]),
        "ink": (255, 255, 255), "on": (20, 22, 52),
        "accent": (255, 201, 84), "accent2": (124, 162, 255),
        "radius": 30, "badge": "circle", "footstyle": "pill",
        "tgline": "разбор дня в телеграме",
        "voice": ("TeHM1srC510U976rvUis", "Zlata — быстрая и яркая",
                  "uvysWDLbKpA4XvpD3GI6", "Leonie"),
    },
    "B": {
        "brand": 6627103, "handle": "lingofydeutsch.1",
        "fmt": "parse", "mus_off": 24.0,
        "f_bold": "lora_bold", "f_semi": "lora_semi", "f_reg": "lora_reg",
        "bg": ("paper", [(247, 240, 226), (223, 210, 188), (198, 88, 72),
                         (206, 194, 174)]),
        "ink": (44, 36, 30), "on": (247, 240, 226),
        "accent": (176, 62, 48), "accent2": (104, 122, 86),
        "radius": 10, "badge": "none", "footstyle": "rule",
        "tgline": "фраза с разбором каждый день",
        "voice": ("xcVbjGhhLIoKi3va6mAe", "Viktoriya — объясняет с интересом",
                  "yamcvgNdKmgh0Ron7Bsz", "Hans — спокойный разбор"),
    },
    "C": {
        "brand": 6690247, "handle": "lingofy.de8",
        "fmt": "chat", "mus_off": 37.0,
        "f_bold": "mono_bold", "f_semi": "mono_bold", "f_reg": "mono_reg",
        "bg": ("grid", [(14, 17, 22), (28, 34, 44), (20, 58, 70)]),
        "ink": (236, 242, 248), "on": (12, 20, 24),
        "accent": (46, 214, 170), "accent2": (92, 110, 134),
        "radius": 14, "badge": "none", "footstyle": "tag",
        "tgline": "живые диалоги в телеграме",
        "voice": ("L6qAUOfLV8LhJlH6aFfN", "Михаил — живой разговорный",
                  "lDqWFcxBxWhu05tao5Ls", "Marcel — дружелюбный"),
    },
    "D": {
        "brand": 7336479, "handle": "lingofydeutsch4",
        "fmt": "fix", "mus_off": 50.0,
        "f_bold": "cond_bold", "f_semi": "cond_bold", "f_reg": "cond_reg",
        "bg": ("anim:wave", [(242, 243, 246), (214, 219, 230), (250, 250, 252)]),
        "ink": (24, 26, 32), "on": (250, 250, 252),
        "accent": (226, 58, 54), "accent2": (34, 162, 92),
        "radius": 0, "badge": "square", "footstyle": "box",
        "tgline": "ошибка дня и как её не делать",
        "voice": ("k9CgOpaXuoHsdMdv6om1", "Mark — уверенный и чёткий",
                  "xlbJQnFFGB01bv7HK5CZ", "Jonas — собранный"),
    },
    "E": {
        "brand": 7337272, "handle": "lingofy.deutsch8",
        "fmt": "card", "mus_off": 63.0,
        "f_bold": "lib_bold", "f_semi": "lib_bold", "f_reg": "lib_reg",
        "bg": ("solid", [(18, 42, 40), (32, 96, 82), (120, 232, 198)]),
        "ink": (240, 252, 246), "on": (14, 38, 36),
        "accent": (120, 232, 198), "accent2": (248, 214, 96),
        "radius": 44, "badge": "none", "footstyle": "plain",
        "tgline": "слово и пример каждый день",
        "voice": ("9QNFThQvNzOXfEbWsM74", "Masha — спокойная и ровная",
                  "XJWHuOvSoCriK1Q4wPAN", "Judith Maas"),
    },
}


def background(th, variant, k=0):
    """Фон кадра: статичный отдаётся копией, анимированный — петлёй."""
    kind, pal = th["bg"]
    if kind.startswith("anim:"):
        import anim
        return anim.frame(kind.split(":", 1)[1], pal[:3], k + variant * 7)
    if kind == "paper":
        base = paper(pal, variant)
    elif kind == "grid":
        base = grid(pal, variant)
    else:
        base = solid(pal, variant)
    return base.convert("RGBA")

"""Погода в Мюнхене через Open-Meteo (бесплатно, без ключа)."""
import datetime as dt
import logging
import os

import httpx

log = logging.getLogger("weather")

LAT = float(os.getenv("WEATHER_LAT", "48.1374"))
LON = float(os.getenv("WEATHER_LON", "11.5755"))
URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes → эмодзи и текст
CODES = {
    0: ("☀️", "ясно"), 1: ("🌤", "почти ясно"), 2: ("⛅", "переменная облачность"), 3: ("☁️", "пасмурно"),
    45: ("🌫", "туман"), 48: ("🌫", "изморозь, туман"),
    51: ("🌦", "лёгкая морось"), 53: ("🌦", "морось"), 55: ("🌧", "сильная морось"),
    56: ("🌧", "ледяная морось"), 57: ("🌧", "ледяная морось"),
    61: ("🌧", "небольшой дождь"), 63: ("🌧", "дождь"), 65: ("🌧", "сильный дождь"),
    66: ("🌧", "ледяной дождь"), 67: ("🌧", "сильный ледяной дождь"),
    71: ("🌨", "небольшой снег"), 73: ("🌨", "снег"), 75: ("❄️", "сильный снег"), 77: ("🌨", "снежная крупа"),
    80: ("🌦", "кратковременный дождь"), 81: ("🌧", "ливень"), 82: ("⛈", "сильный ливень"),
    85: ("🌨", "снегопад"), 86: ("❄️", "сильный снегопад"),
    95: ("⛈", "гроза"), 96: ("⛈", "гроза с градом"), 99: ("⛈", "сильная гроза с градом"),
}
WET = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99}


def fetch() -> dict:
    r = httpx.get(URL, timeout=15, params={
        "latitude": LAT, "longitude": LON, "timezone": "Europe/Berlin", "forecast_days": 2,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation",
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,"
                 "sunrise,sunset,weather_code",
    })
    r.raise_for_status()
    return r.json()


def _code(c) -> tuple[str, str]:
    return CODES.get(int(c), ("🌡", "—"))


def summary(day: dt.date, data: dict | None = None) -> dict:
    """Сводка на день: текущая погода, мин/макс, когда дождь, совет по одежде и велику."""
    data = data or fetch()
    d = day.isoformat()
    daily = data["daily"]
    i = daily["time"].index(d)
    cur = data.get("current", {})
    hourly = data["hourly"]

    rain_hours = []
    for t, p, c in zip(hourly["time"], hourly["precipitation_probability"], hourly["weather_code"]):
        if t.startswith(d) and 7 <= int(t[11:13]) <= 22 and ((p or 0) >= 50 or int(c) in WET):
            rain_hours.append(int(t[11:13]))

    tmin, tmax = daily["temperature_2m_min"][i], daily["temperature_2m_max"][i]
    return {
        "now_temp": cur.get("temperature_2m"), "feels": cur.get("apparent_temperature"),
        "now_code": cur.get("weather_code", daily["weather_code"][i]), "wind": cur.get("wind_speed_10m"),
        "tmin": tmin, "tmax": tmax, "day_code": daily["weather_code"][i],
        "rain_prob": daily["precipitation_probability_max"][i], "rain_sum": daily["precipitation_sum"][i],
        "rain_hours": rain_hours,
        "sunrise": daily["sunrise"][i][11:16], "sunset": daily["sunset"][i][11:16],
    }


def _ranges(hours: list[int]) -> str:
    if not hours:
        return ""
    out, start, prev = [], hours[0], hours[0]
    for h in hours[1:] + [None]:
        if h is not None and h == prev + 1:
            prev = h
            continue
        out.append(f"{start}–{prev + 1}" if prev != start else f"{start}–{start + 1}")
        if h is not None:
            start = prev = h
    return ", ".join(out)


def advice(w: dict) -> list[str]:
    tips = []
    feels = w["feels"] if w["feels"] is not None else w["tmin"]
    if feels is not None:
        if feels <= 0:
            tips.append("🧤 Мороз: шапка, перчатки, тёплая куртка")
        elif feels <= 7:
            tips.append("🧥 Холодно: тёплая куртка")
        elif feels <= 14:
            tips.append("🧥 Прохладно: куртка или худи")
        elif feels >= 25:
            tips.append("🩳 Жарко: одевайся легко, возьми воду")
    if w["rain_hours"]:
        tips.append(f"☂️ Дождь примерно {_ranges(w['rain_hours'])} ч — возьми зонт")
    if w["rain_hours"] or (w["wind"] or 0) >= 35 or (w["tmin"] is not None and w["tmin"] <= 0):
        tips.append("🚋 На велике сегодня не лучшая идея — трамвай")
    elif not w["rain_hours"] and (w["tmax"] or 0) >= 8:
        tips.append("🚲 Норм погода для велика")
    return tips


def fmt(w: dict) -> str:
    e_now, t_now = _code(w["now_code"])
    e_day, t_day = _code(w["day_code"])
    lines = []
    if w["now_temp"] is not None:
        lines.append(f"{e_now} Сейчас {w['now_temp']:.0f}° (ощущается {w['feels']:.0f}°), {t_now}")
    lines.append(f"{e_day} Днём {w['tmin']:.0f}…{w['tmax']:.0f}°, {t_day}"
                 + (f", дождь до {w['rain_prob']}%" if (w["rain_prob"] or 0) >= 30 else ""))
    lines.append(f"🌅 Рассвет {w['sunrise']} · закат {w['sunset']}")
    lines += advice(w)
    return "\n".join(lines)


def today_text(day: dt.date) -> str:
    try:
        return fmt(summary(day))
    except Exception as e:  # noqa: BLE001
        log.warning("погода недоступна: %s", e)
        return "🌡 Погода сейчас не загрузилась"

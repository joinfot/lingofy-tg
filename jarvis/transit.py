"""Расчёт дороги через MVG: когда выходить и когда начинать собираться."""
import datetime as dt
import logging
import os

import httpx

from config import cfg

log = logging.getLogger("transit")

BASE = "https://www.mvg.de/api/bgw-pt/v3"
HEADERS = {"accept": "application/json, text/plain, */*",
           "user-agent": "Mozilla/5.0 (personal assistant bot)"}

HOME = cfg("home_address", "")
PLACES = {
    "school": {"name": "Berufsschule", "address": cfg("school_address", ""),
               "fallback_min": 35},
    "store": {"name": cfg("store_name", "Работа"), "address": cfg("store_address", ""),
              "fallback_min": 30},
    "hq": {"name": cfg("hq_name", "Офис"), "address": cfg("hq_address", ""),
           "fallback_min": 45},
}
READY_MIN = int(os.getenv("READY_MINUTES", "30"))     # сборы до выхода
BUFFER_MIN = int(os.getenv("ARRIVE_BUFFER", "5"))     # приехать за N минут до начала
# Предпочитать маршруты, где первым едешь этой линией (из my_config.json).
# Пусто — просто самый быстрый маршрут.
FIRST_LINE = str(cfg("first_line", "")).strip()
# Пересадочная станция, через которую тоже пробуем строить маршрут
VIA_STATION = str(cfg("via_station", "")).strip()
ALL_TYPES = "SCHIFF,UBAHN,TRAM,SBAHN,BUS,REGIONAL_BUS,BAHN"
NO_UBAHN = "SCHIFF,TRAM,SBAHN,BUS,REGIONAL_BUS,BAHN"

TYPE_RU = {"UBAHN": "U-Bahn", "SBAHN": "S-Bahn", "TRAM": "трамвай", "BUS": "автобус",
           "REGIONAL_BUS": "автобус", "BAHN": "поезд", "SCHIFF": "паром"}

_coords_cache: dict[str, tuple[float, float]] = {}
_station_cache: dict[str, str] = {}


def _get(path: str, params: dict):
    r = httpx.get(BASE + path, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def geocode(address: str) -> tuple[float, float]:
    if address not in _coords_cache:
        res = _get("/locations", {"query": address, "locationTypes": "ADDRESS,STATION"})
        if not res:
            raise ValueError(f"MVG не нашёл адрес: {address}")
        _coords_cache[address] = (res[0]["latitude"], res[0]["longitude"])
    return _coords_cache[address]


def station_id(name: str) -> str:
    if name not in _station_cache:
        res = _get("/locations", {"query": name, "locationTypes": "STATION"})
        if not res or not res[0].get("globalId"):
            raise ValueError(f"MVG не нашёл станцию: {name}")
        _station_cache[name] = res[0]["globalId"]
    return _station_cache[name]


def _t(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def parse_connection(c: dict) -> dict:
    """Превращает соединение MVG в понятный вид."""
    parts = c["parts"]
    legs = []
    for p in parts:
        line = p.get("line") or {}
        ttype = line.get("transportType", "")
        frm, to = p["from"], p["to"]
        dep = _t(frm.get("plannedDeparture"))
        arr = _t(to.get("plannedArrival") or to.get("plannedDeparture"))
        delay = frm.get("departureDelayInMinutes") or 0
        walk = ttype in ("PEDESTRIAN", "FUSSWEG", "") or line.get("network") == "unknown"
        legs.append({"walk": walk, "label": line.get("label", ""), "type": TYPE_RU.get(ttype, ttype),
                     "from": frm.get("name", ""), "to": to.get("name", ""), "dep": dep, "arr": arr,
                     "delay": delay, "dest": line.get("destination", "")})
    first_ride = next((l for l in legs if not l["walk"]), None)
    last = legs[-1]
    arr = last["arr"]
    if last["walk"] and last["arr"] is None and len(legs) > 1:
        arr = legs[-2]["arr"]
    return {"leave": legs[0]["dep"], "arrive": arr, "legs": legs, "first_ride": first_ride}


def best_route(dest_key: str, arrive_by: dt.datetime) -> dict:
    """Самое позднее соединение, которое привозит не позже arrive_by."""
    olat, olon = geocode(HOME)
    dlat, dlon = geocode(PLACES[dest_key]["address"])
    params = {
        "originLatitude": olat, "originLongitude": olon,
        "destinationLatitude": dlat, "destinationLongitude": dlon,
        "routingDateTime": arrive_by.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "routingDateTimeIsArrival": "true",
        "transportTypes": ALL_TYPES,
        "routeType": "LEAST_TIME", "changeSpeed": "NORMAL",
    }
    # Несколько запросов: обычный, без U-Bahn и через пересадочную станцию — потом выбираем
    variants = [params]
    if FIRST_LINE:
        variants.append({**params, "transportTypes": NO_UBAHN})
        if VIA_STATION:
            try:
                variants.append({**params, "viaStationGlobalId": station_id(VIA_STATION)})
            except Exception as e:  # noqa: BLE001
                log.warning("станция %s не найдена: %s", VIA_STATION, e)
    raw, errors = [], []
    for v in variants:
        try:
            raw += _get("/routes", v) or []
        except Exception as e:  # noqa: BLE001
            errors.append(e)
    if not raw and errors:
        raise errors[0]
    conns = [parse_connection(c) for c in raw]
    conns = [c for c in conns if c["leave"] and c["arrive"]]
    if not conns:
        raise ValueError("MVG не вернул маршрутов")

    def in_time(cs):
        return [c for c in cs if c["arrive"] <= arrive_by + dt.timedelta(minutes=1)]

    preferred = [c for c in conns if FIRST_LINE and c["first_ride"] and c["first_ride"]["label"] == FIRST_LINE]
    for pool in (in_time(preferred), in_time(conns)):
        if pool:
            return max(pool, key=lambda c: c["leave"])
    return min(conns, key=lambda c: c["arrive"])


def destination_for(date: dt.date, kind: str, start: str | None, place: str | None) -> str | None:
    if place in PLACES:
        return place
    if kind == "school":
        return "school"
    if kind == "work":
        # По четвергам смены 9–18 — в Zentrale
        return "hq" if date.weekday() == 3 and start == "09:00" else "store"
    return None


def plan(date: dt.date, kind: str, start: str, place: str | None, tz) -> dict | None:
    """План дороги на день. Возвращает None, если ехать никуда не надо."""
    dest = destination_for(date, kind, start, place)
    if not dest or not start:
        return None
    h, m = map(int, start.split(":"))
    start_dt = dt.datetime.combine(date, dt.time(h, m), tzinfo=tz)
    arrive_by = start_dt - dt.timedelta(minutes=BUFFER_MIN)
    out = {"dest": dest, "dest_name": PLACES[dest]["name"], "start": start_dt, "route": None}
    try:
        r = best_route(dest, arrive_by)
        leave = r["leave"].astimezone(tz)
        out.update(route=r, leave=leave, arrive=r["arrive"].astimezone(tz))
    except Exception as e:  # noqa: BLE001 — нет связи с MVG: считаем примерно
        log.warning("MVG недоступен: %s", e)
        leave = arrive_by - dt.timedelta(minutes=PLACES[dest]["fallback_min"])
        out.update(leave=leave, arrive=arrive_by, error=str(e))
    out["get_ready"] = out["leave"] - dt.timedelta(minutes=READY_MIN)
    return out


def fmt(p: dict, tz, header: bool = True) -> str:
    lines = []
    if header:
        lines.append(f"📍 {p['dest_name']}, начало в {p['start']:%H:%M}")
    lines.append(f"🚿 Начать собираться: {p['get_ready']:%H:%M}")
    lines.append(f"🚪 Выйти: {p['leave']:%H:%M}")
    r = p.get("route")
    if r:
        for l in r["legs"]:
            if l["walk"] or not l["dep"]:
                continue
            delay = f" (+{l['delay']} мин задержка!)" if l["delay"] else ""
            lines.append(f"🚇 {l['type']} {l['label']} в {l['dep'].astimezone(tz):%H:%M} от {l['from']}"
                         f" → {l['to']}{delay}")
        lines.append(f"✅ На месте: {p['arrive']:%H:%M}")
    else:
        lines.append("⚠️ Расписание MVG не загрузилось, время примерное")
    return "\n".join(lines)

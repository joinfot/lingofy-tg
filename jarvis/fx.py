"""Курс гривны к евро из открытого API monobank (без ключа). Кэш на 6 часов."""
import json
import logging
import os
import time
import urllib.request

log = logging.getLogger("fx")
_cache = {"t": 0.0, "uah_per_eur": None}


def uah_per_eur() -> float:
    """Сколько гривен в одном евро (курс продажи monobank). Бросает исключение, если узнать не удалось."""
    if _cache["uah_per_eur"] and time.time() - _cache["t"] < 6 * 3600:
        return _cache["uah_per_eur"]
    try:
        req = urllib.request.Request("https://api.monobank.ua/bank/currency", headers={"User-Agent": "jarvis"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        row = next(x for x in data if x.get("currencyCodeA") == 978 and x.get("currencyCodeB") == 980)
        rate = row.get("rateSell") or row.get("rateCross")
        _cache.update(t=time.time(), uah_per_eur=float(rate))
        return float(rate)
    except Exception as e:  # noqa: BLE001
        manual = os.getenv("UAH_PER_EUR")
        if manual:
            return float(manual)
        raise RuntimeError(f"не удалось получить курс EUR/UAH: {e}") from e


def to_eur(amount: float, currency: str) -> float:
    currency = (currency or "EUR").upper()
    if currency in ("EUR", "€"):
        return round(float(amount), 2)
    if currency in ("UAH", "₴", "ГРН"):
        return round(float(amount) / uah_per_eur(), 2)
    raise ValueError(f"валюта {currency} не поддерживается")

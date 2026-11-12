"""Личные настройки: читаются из my_config.json рядом с ботом (этот файл есть только на твоём ноуте,
в GitHub не попадает). Переменные из .env имеют приоритет."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
_path = os.path.join(BASE, "my_config.json")
CONF = {}
if os.path.exists(_path):
    with open(_path, encoding="utf-8") as _f:
        CONF = json.load(_f)


def cfg(key: str, default=None):
    """Сначала .env (КЛЮЧ_ЗАГЛАВНЫМИ), потом my_config.json (ключ_строчными), потом default."""
    env = os.getenv(key.upper())
    if env not in (None, ""):
        return env
    return CONF.get(key.lower(), default)


def load_local_json(name: str, default):
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return default

"""Самообновление Джарвиса из GitHub (папка jarvis/ в репозитории).

Раз в несколько минут смотрит последний коммит, который менял папку jarvis/. Если он новый —
скачивает код, кладёт поверх (личные файлы, .env и базу не трогает) и завершает процесс;
start_jarvis.bat сразу запускает бота заново уже с новым кодом.
"""
import io
import json
import logging
import os
import urllib.request
import zipfile

log = logging.getLogger("updater")

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.getenv("GITHUB_REPO", "joinfot/lingofy-tg")
SUBDIR = os.getenv("GITHUB_SUBDIR", "jarvis").strip("/")
BRANCH = os.getenv("GITHUB_BRANCH", "main")
TOKEN = os.getenv("GITHUB_TOKEN", "")  # нужен только для приватного репозитория
VERSION_FILE = os.path.join(BASE, "VERSION")
# личное и рабочее — никогда не перезаписываем
KEEP = {".env", "assistant.db", "assistant.db-journal", "start_jarvis.bat", "VERSION",
        "my_config.json", "my_expenses.json", "schedule.json", "seed.json"}


def enabled() -> bool:
    return os.getenv("AUTO_UPDATE", "1") != "0" and bool(REPO)


def _get(url: str) -> bytes:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "jarvis-updater"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def local_version() -> str:
    try:
        return open(VERSION_FILE, encoding="utf-8").read().strip()
    except FileNotFoundError:
        return ""


def remote_version() -> str:
    q = f"?sha={BRANCH}&per_page=1" + (f"&path={SUBDIR}" if SUBDIR else "")
    data = json.loads(_get(f"https://api.github.com/repos/{REPO}/commits{q}"))
    return data[0]["sha"]


def update_if_needed() -> str | None:
    """Возвращает новый sha, если код обновлён (надо перезапуститься), иначе None."""
    if not enabled():
        return None
    sha = remote_version()
    if sha == local_version():
        return None
    blob = _get(f"https://api.github.com/repos/{REPO}/zipball/{sha}")
    prefix = SUBDIR + "/" if SUBDIR else ""
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for info in z.infolist():
            parts = info.filename.split("/", 1)  # первая папка — «owner-repo-sha»
            if len(parts) < 2 or info.is_dir() or not parts[1].startswith(prefix):
                continue
            rel = parts[1][len(prefix):]
            if not rel or rel in KEEP or rel.startswith((".git", "__pycache__")):
                continue
            dest = os.path.join(BASE, *rel.split("/"))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(z.read(info))
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(sha)
    log.info("обновлён до %s", sha[:7])
    return sha

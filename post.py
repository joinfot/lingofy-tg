"""Публикует в Telegram посты из queue.json, время которых наступило.
Уже опубликованные id хранятся в posted.json (бот коммитит его обратно)."""
import json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ.get("CHAT_ID", "@lingofydeutsch")
MAX_LATE = timedelta(hours=6)  # не публиковать посты, опоздавшие больше чем на 6 ч

def api(method, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/{method}",
                                 data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if not res.get("ok"):
        raise RuntimeError(res)
    return res

def send(p):
    t = p["type"]
    if t == "photo":
        api("sendPhoto", {"chat_id": CHAT, "photo": p["photo"], "caption": p["caption"], "parse_mode": "HTML"})
    elif t == "text":
        api("sendMessage", {"chat_id": CHAT, "text": p["text"], "parse_mode": "HTML"})
    elif t == "quiz":
        api("sendPoll", {"chat_id": CHAT, "question": p["question"], "options": p["options"],
                         "type": "quiz", "correct_option_id": p["correct"], "explanation": p.get("explanation", "")})
    else:
        raise ValueError(t)

def main():
    queue = json.load(open("queue.json", encoding="utf-8"))
    posted = json.load(open("posted.json", encoding="utf-8")) if os.path.exists("posted.json") else []
    now = datetime.now(timezone.utc)
    force = sys.argv[1:]  # можно передать id, чтобы опубликовать немедленно
    changed = False
    for p in sorted(queue, key=lambda x: x["at"]):
        if p["id"] in posted:
            continue
        at = datetime.fromisoformat(p["at"])
        due = p["id"] in force or (at <= now and (p.get("catch_up") or now - at <= MAX_LATE))
        if not due:
            continue
        try:
            send(p); posted.append(p["id"]); changed = True
            print("posted", p["id"])
        except Exception as e:
            print("FAILED", p["id"], e)
    if changed:
        json.dump(posted, open("posted.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

main()

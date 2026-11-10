"""Публикует в Telegram посты из queue.json, время которых наступило.
Уже опубликованные id хранятся в posted.json (бот коммитит его обратно)."""
import json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ.get("CHAT_ID", "@lingofydeutsch")
# GitHub запускает крон не каждые 15 минут, как заявлено в расписании, а
# фактически раз в 6-8 часов. С окном в 6 часов посты, попавшие между
# запусками, молча терялись: 9 ноября так пропали утренний и вечерний.
# Поэтому окно сделано суточным, но публикация разрешена только в живые
# часы — иначе опоздавший вечерний пост ушёл бы в три ночи.
MAX_LATE = timedelta(hours=24)
HOURS = (7, 22)        # по Берлину: раньше и позже не публикуем
TZ = timezone(timedelta(hours=1))


def awake(now):
    h = now.astimezone(TZ).hour
    return HOURS[0] <= h < HOURS[1]

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
        res = api("sendPhoto", {"chat_id": CHAT, "photo": p["photo"], "caption": p["caption"], "parse_mode": "HTML"})
    elif t == "text":
        res = api("sendMessage", {"chat_id": CHAT, "text": p["text"], "parse_mode": "HTML"})
    elif t == "quiz":
        res = api("sendPoll", {"chat_id": CHAT, "question": p["question"], "options": p["options"],
                               "type": "quiz", "correct_option_id": p["correct"], "explanation": p.get("explanation", "")})
    elif t == "document":
        res = api("sendDocument", {"chat_id": CHAT, "document": p["document"], "caption": p.get("caption", ""),
                                   "parse_mode": "HTML"})
    else:
        raise ValueError(t)
    if p.get("pin"):
        try:
            api("pinChatMessage", {"chat_id": CHAT, "message_id": res["result"]["message_id"],
                                   "disable_notification": True})
        except Exception as e:
            print("PIN FAILED", p["id"], e)

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
        late = now - at
        due = p["id"] in force or (
            at <= now
            and (p.get("catch_up") or late <= MAX_LATE)
            # вовремя публикуем всегда, опоздавший ждёт живого часа
            and (late <= timedelta(minutes=30) or awake(now))
        )
        if not due:
            continue
        try:
            send(p); posted.append(p["id"]); changed = True
            print("posted", p["id"])
        except Exception as e:
            print("FAILED", p["id"], e)
    if changed:
        json.dump(posted, open("posted.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# без этой проверки импорт файла сразу начинал рассылать посты
if __name__ == "__main__":
    main()

"""Лид-магнит в @lingofydeutsch_bot.

Человек пишет боту (/start или что угодно) → бот проверяет подписку на канал →
подписан: присылает PDF; не подписан: просит подписаться и даёт кнопку «Я подписался».

Запускается по расписанию из GitHub Actions (leadbot.yml): забирает накопившиеся
сообщения через getUpdates, отвечает и сохраняет состояние в lead_state.json.
"""
import json
import os
import urllib.request

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ.get("CHAT_ID", "@lingofydeutsch")
STATE = "lead_state.json"
PDF_URL = "https://raw.githubusercontent.com/joinfot/lingofy-tg/main/files/100-fraz-dlya-zhizni-v-germanii.pdf"
CHANNEL_URL = "https://t.me/lingofydeutsch"

TXT_GIFT = ("🎁 Держи! «100 фраз для жизни в Германии»: врач, Bürgeramt, квартира, банк, работа.\n\n"
            "Сохрани себе 📌 А в канале каждый день новые фразы и мини-тесты.")
TXT_SUBSCRIBE = ("Привет! 👋 Здесь можно забрать бесплатный PDF «100 фраз для жизни в Германии» 🇩🇪\n\n"
                 "Чтобы получить файл, подпишись на канал Lingofy Deutsch и нажми «✅ Я подписался».")
TXT_STILL_NOT = "Пока не вижу подписки 🙈 Подпишись на канал и нажми кнопку ещё раз."


def api(method, payload):
    req = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/{method}",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if not res.get("ok"):
        raise RuntimeError(res)
    return res["result"]


def load():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"offset": 0, "file_id": None, "sent": []}


def subscribed(user_id):
    try:
        m = api("getChatMember", {"chat_id": CHANNEL, "user_id": user_id})
        return m["status"] in ("member", "administrator", "creator")
    except Exception as e:
        print("getChatMember failed", user_id, e)
        return False


def send_pdf(state, chat_id):
    doc = state.get("file_id") or PDF_URL
    msg = api("sendDocument", {"chat_id": chat_id, "document": doc, "caption": TXT_GIFT})
    state["file_id"] = msg["document"]["file_id"]  # дальше шлём по file_id, без скачивания
    if chat_id not in state["sent"]:
        state["sent"].append(chat_id)


def ask_subscribe(chat_id, text=TXT_SUBSCRIBE):
    api("sendMessage", {"chat_id": chat_id, "text": text, "reply_markup": {"inline_keyboard": [
        [{"text": "📢 Подписаться на канал", "url": CHANNEL_URL}],
        [{"text": "✅ Я подписался", "callback_data": "check"}],
    ]}})


def handle(state, upd):
    if "message" in upd:
        m = upd["message"]
        if m["chat"]["type"] != "private":
            return
        uid = m["from"]["id"]
        if subscribed(uid):
            send_pdf(state, m["chat"]["id"])
        else:
            ask_subscribe(m["chat"]["id"])
    elif "callback_query" in upd:
        q = upd["callback_query"]
        uid = q["from"]["id"]
        chat_id = q["message"]["chat"]["id"]
        ok = subscribed(uid)
        try:
            api("answerCallbackQuery", {"callback_query_id": q["id"],
                                        "text": "Отправляю PDF 🎁" if ok else "Подписка не найдена"})
        except Exception:
            pass  # кнопка могла устареть, ничего страшного
        if ok:
            send_pdf(state, chat_id)
        else:
            ask_subscribe(chat_id, TXT_STILL_NOT)


def main():
    state = load()
    updates = api("getUpdates", {"offset": state["offset"], "timeout": 0,
                                 "allowed_updates": ["message", "callback_query"]})
    for upd in updates:
        try:
            handle(state, upd)
        except Exception as e:
            print("FAILED update", upd.get("update_id"), e)
        state["offset"] = upd["update_id"] + 1
    print(f"обработано {len(updates)}, всего выдано PDF: {len(state['sent'])}")
    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


main()

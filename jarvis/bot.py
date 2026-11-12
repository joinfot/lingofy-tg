"""Личный ассистент в Telegram: расписание, задачи, напоминания, зал."""
import asyncio
import datetime as dt
import json
import logging
import os
import sqlite3
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

load_dotenv()
import transit  # noqa: E402  (читает настройки из .env)
import weather  # noqa: E402
import updater  # noqa: E402
import fx  # noqa: E402
from config import cfg, load_local_json  # noqa: E402
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("assistant")

TZ = ZoneInfo("Europe/Berlin")
BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE, "assistant.db"))
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
OWNER_ID = int(os.getenv("OWNER_ID") or 0)
MORNING = os.getenv("MORNING_TIME", "07:00")
EVENING = os.getenv("EVENING_TIME", "21:30")

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
WEEKDAYS_FULL = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября",
          "октября", "ноября", "декабря"]
EXAM_DATE = dt.date.fromisoformat(cfg("exam_date", "2099-01-01"))
WAREHOUSE_RENT = float(cfg("warehouse_rent", 0) or 0)
KIND_RU = {
    "work": "💼 работа", "school": "🎓 Berufsschule", "free": "🟢 свободен",
    "vacation": "🌴 отпуск", "exam": "📝 ЭКЗАМЕН", "prep": "📚 Prüfungsfrei",
    "holiday": "🟢 выходной", "other": "📌",
}


# ---------- база ----------
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS days(date TEXT PRIMARY KEY, kind TEXT, start TEXT, end TEXT, note TEXT);
        CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
            date TEXT, time TEXT, done INTEGER DEFAULT 0, created TEXT);
        CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL,
            fire_at TEXT NOT NULL, repeat TEXT DEFAULT 'none', active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS gym(date TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS commute_sent(date TEXT, kind TEXT, PRIMARY KEY(date, kind));
        CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL,
            amount REAL NOT NULL, category TEXT, note TEXT);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS food(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL,
            name TEXT, kcal REAL, protein REAL);
        CREATE TABLE IF NOT EXISTS items(code TEXT PRIMARY KEY, title TEXT, brand TEXT, size TEXT,
            price REAL, description TEXT, status TEXT DEFAULT 'черновик', account TEXT,
            sold_price REAL, created TEXT, updated TEXT);
        """)
        cols = [r[1] for r in con.execute("PRAGMA table_info(days)")]
        if "place" not in cols:
            con.execute("ALTER TABLE days ADD COLUMN place TEXT")
        path = os.path.join(BASE, "schedule.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for d, v in json.load(f).items():
                    # OR IGNORE: правки, сделанные через чат, не затираются при перезапуске
                    con.execute("INSERT OR IGNORE INTO days(date,kind,start,end,note,place) VALUES(?,?,?,?,?,?)",
                                (d, v["kind"], v.get("start"), v.get("end"), v.get("note"), v.get("place")))


EXPENSE_CATS = ["еда", "продукты", "транспорт", "шмотки/товар", "покупки", "зал", "развлечения", "связь/подписки", "другое"]

_exp = load_local_json("my_expenses.json", {})  # личные стартовые траты — только на ноуте
EARLY_EXPENSES = [tuple(x) for x in _exp.get("early", [])]
EXPENSE_BATCHES = {k: [tuple(x) for x in v] for k, v in _exp.get("batches", {}).items()}


def load_extras():
    """Один раз: план подготовки к экзамену (задачи по дням) и первые расходы."""
    with db() as con:
        if not con.execute("SELECT 1 FROM meta WHERE key='expenses_seeded'").fetchone():
            for d, a, c, n in EARLY_EXPENSES:
                con.execute("INSERT INTO expenses(date,amount,category,note) VALUES(?,?,?,?)", (d, a, c, n))
            con.execute("INSERT INTO meta VALUES('expenses_seeded','1')")
        for key, rows in EXPENSE_BATCHES.items():
            if con.execute("SELECT 1 FROM meta WHERE key=?", (key,)).fetchone():
                continue
            try:
                conv = [(d, fx.to_eur(a, cur), cat, note + (f" ({a:.2f} ₴)" if cur == "UAH" else ""))
                        for d, a, cur, cat, note in rows]
            except Exception as e:  # noqa: BLE001 — нет курса: попробуем при следующем запуске
                log.warning("пакет трат %s отложен: %s", key, e)
                continue
            con.executemany("INSERT INTO expenses(date,amount,category,note) VALUES(?,?,?,?)", conv)
            con.execute("INSERT INTO meta VALUES(?, '1')", (key,))
        if not con.execute("SELECT 1 FROM meta WHERE key='fix_2026_11_12'").fetchone():
            # Сообщение от 12.11 21:23 потерялось (AI ответил пустым «Готово.») — применяем то, что он просил.
            for pat in ("Мб съездить", "Нормально поесть", "Посылки (если есть)"):
                con.execute("DELETE FROM tasks WHERE done=0 AND title LIKE ?", (f"%{pat}%",))
            for pat in ("Склад: вернуться", "Выставить шмотки", "Чекнуть шмотки", "Купить продукты"):
                con.execute("UPDATE tasks SET date='2026-11-13', time=NULL WHERE done=0 AND date<'2026-11-13' "
                            "AND title LIKE ?", (f"%{pat}%",))
            con.execute("UPDATE tasks SET date='2026-11-13' WHERE done=0 AND title LIKE '📚 Экзамен%' "
                        "AND date IN ('2026-11-10','2026-11-11')")
            if not con.execute("SELECT 1 FROM tasks WHERE date='2026-11-13' AND title LIKE '%Schulung%'").fetchone():
                con.execute("INSERT INTO tasks(title,date,time,created) VALUES('🎓 Schulung','2026-11-13','10:30',?)",
                            (dt.datetime.now(TZ).isoformat(),))
            for gd in ("2026-11-09", "2026-11-12"):
                con.execute("INSERT OR IGNORE INTO gym VALUES(?)", (gd,))
            con.execute("UPDATE tasks SET done=1 WHERE date='2026-11-12' AND title LIKE '%Зал%'")
            if not con.execute("SELECT 1 FROM food WHERE date='2026-11-12'").fetchone():
                con.executemany("INSERT INTO food(date,name,kcal,protein) VALUES('2026-11-12',?,?,?)",
                                [("Bockwurst (перед работой)", 300, 12), ("Döner (на работе)", 700, 35),
                                 ("пицца (после работы)", 900, 35)])
            for pat in ("Поставить бота", "Встретить Еву", "Проводить родителей", "Зал (по возможности)"):
                con.execute("UPDATE tasks SET done=1 WHERE done=0 AND date<'2026-11-12' AND title LIKE ?", (f"%{pat}%",))
            con.execute("UPDATE tasks SET date='2026-11-12' WHERE done=0 AND date<'2026-11-12' AND title LIKE '%Lingofy%'")
            if not con.execute("SELECT 1 FROM tasks WHERE date='2026-11-12' AND title LIKE '%Vinted%'").fetchone():
                con.execute("INSERT INTO tasks(title,date,created) VALUES('🔄 Перезалить вещи на Vinted','2026-11-12',?)",
                            (dt.datetime.now(TZ).isoformat(),))
            con.execute("INSERT INTO meta VALUES('fix_2026_11_12','1')")
        if not con.execute("SELECT 1 FROM meta WHERE key='exam_seeded'").fetchone() and EXAM_PLAN:
            # общие «Подготовка к экзамену» заменяем конкретными темами
            con.execute("DELETE FROM tasks WHERE done=0 AND title LIKE '%Подготовка к экзамену%'")
            for d, v in EXAM_PLAN["days"].items():
                short = v["topic"].split(":")[0].split(",")[0][:45]
                con.execute("INSERT INTO tasks(title,date,time,created) VALUES(?,?,?,?)",
                            (f"📚 Экзамен ({v['minutes']} мин): {short}", d, None, dt.datetime.now(TZ).isoformat()))
            con.execute("INSERT INTO meta VALUES('exam_seeded','1')")


def expenses_text(days: int) -> str:
    d0 = (today() - dt.timedelta(days=days - 1)).isoformat()
    with db() as con:
        rows = con.execute("SELECT category, SUM(amount) s, COUNT(*) c FROM expenses WHERE date>=? "
                           "GROUP BY category ORDER BY s DESC", (d0,)).fetchall()
        total = con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date>=?", (d0,)).fetchone()[0]
    if not rows:
        return "трат нет"
    return f"{total:.2f} €\n" + "\n".join(f"• {r['category']}: {r['s']:.2f} € ({r['c']})" for r in rows)


def spent_on(d: dt.date) -> float:
    with db() as con:
        return con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date=?", (d.isoformat(),)).fetchone()[0]


PROTEIN_GOAL = float(os.getenv("PROTEIN_GOAL", "150"))
KCAL_GOAL = float(os.getenv("KCAL_GOAL", "3000"))
CODE_PREFIX = os.getenv("NEW_CODE_PREFIX", "C")
ITEM_STATUSES = ["черновик", "сфоткан", "выставлен", "продан", "перефоткать"]


def food_day(d: dt.date) -> tuple[float, float]:
    with db() as con:
        r = con.execute("SELECT COALESCE(SUM(kcal),0), COALESCE(SUM(protein),0) FROM food WHERE date=?",
                        (d.isoformat(),)).fetchone()
    return r[0], r[1]


def food_line(d: dt.date) -> str:
    k, p = food_day(d)
    return f"🍗 Белок {p:.0f}/{PROTEIN_GOAL:.0f} г · 🔥 {k:.0f}/{KCAL_GOAL:.0f} ккал"


def next_code() -> str:
    with db() as con:
        rows = con.execute("SELECT code FROM items WHERE code LIKE ?", (CODE_PREFIX + "%",)).fetchall()
    nums = [int(r[0][len(CODE_PREFIX):]) for r in rows if r[0][len(CODE_PREFIX):].isdigit()]
    return f"{CODE_PREFIX}{(max(nums) + 1) if nums else 1:04d}"


def items_text() -> str:
    with db() as con:
        st = con.execute("SELECT status, COUNT(*) c FROM items GROUP BY status").fetchall()
        acc = con.execute("SELECT account, COUNT(*) c FROM items WHERE status='выставлен' GROUP BY account "
                          "ORDER BY c DESC").fetchall()
        d0 = (today() - dt.timedelta(days=30)).isoformat()
        sold = con.execute("SELECT COUNT(*), COALESCE(SUM(sold_price),0) FROM items WHERE status='продан' "
                           "AND updated>=?", (d0,)).fetchone()
        redo = con.execute("SELECT code, title FROM items WHERE status='перефоткать' ORDER BY code LIMIT 30").fetchall()
    if not st:
        return "Вещей в учёте пока нет. Кинь фото вещи — сделаю объявление и заведу код."
    out = ["📦 Вещи по статусам: " + ", ".join(f"{r['status']} {r['c']}" for r in st)]
    if acc:
        out.append("🛍 Выставлено по аккаунтам: " + ", ".join(f"{r['account'] or '?'} {r['c']}" for r in acc))
    line = f"💰 Продано за 30 дней: {sold[0]} шт на {sold[1]:.2f} €"
    if WAREHOUSE_RENT:
        line += (f" (склад {WAREHOUSE_RENT:.0f} €/мес → " +
                 ("окупился ✅)" if sold[1] >= WAREHOUSE_RENT else f"не хватает {WAREHOUSE_RENT - sold[1]:.0f} €)"))
    out.append(line)
    if redo:
        out.append("📸 Перефоткать: " + ", ".join(f"{r['code']}" for r in redo))
    return "\n".join(out)


def last_entry(table: str) -> dt.date | None:
    with db() as con:
        r = con.execute(f"SELECT MAX(date) FROM {table}").fetchone()[0]
    return dt.date.fromisoformat(r) if r else None


def ago(d: dt.date | None) -> str:
    if not d:
        return "ещё ни разу"
    n = (today() - d).days
    return "сегодня" if n == 0 else "вчера" if n == 1 else f"{n} дн. назад ({d:%d.%m})"


def day_log(d: dt.date) -> str:
    with db() as con:
        food = con.execute("SELECT name, kcal, protein FROM food WHERE date=? ORDER BY id", (d.isoformat(),)).fetchall()
        exp = con.execute("SELECT amount, category, note FROM expenses WHERE date=? ORDER BY id", (d.isoformat(),)).fetchall()
    k, p = food_day(d)
    out = [f"📒 {WEEKDAYS[d.weekday()]} {d:%d.%m}", "", "🍽 Еда:"]
    out += [f"• {r['name']} — {r['kcal']:.0f} ккал, {r['protein']:.0f} г белка" for r in food] or ["• ничего не записано"]
    out.append(f"Итого: {k:.0f}/{KCAL_GOAL:.0f} ккал · белок {p:.0f}/{PROTEIN_GOAL:.0f} г")
    out += ["", "💸 Траты:"]
    out += [f"• {r['amount']:.2f} € — {r['note'] or r['category']}" for r in exp] or ["• ничего не записано"]
    out.append(f"Итого: {spent_on(d):.2f} €")
    return "\n".join(out)


def load_seed():
    """Один раз загружает стартовые задачи/напоминания из seed.json."""
    path = os.path.join(BASE, "seed.json")
    if not os.path.exists(path):
        return
    with db() as con:
        con.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
        if con.execute("SELECT 1 FROM meta WHERE key='seeded'").fetchone():
            return
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for t in data.get("tasks", []):
            con.execute("INSERT INTO tasks(title,date,time,created) VALUES(?,?,?,?)",
                        (t["title"], t.get("date"), t.get("time"), dt.datetime.now(TZ).isoformat()))
        for r in data.get("reminders", []):
            con.execute("INSERT INTO reminders(text,fire_at,repeat) VALUES(?,?,?)",
                        (r["text"], r["at"], r.get("repeat", "none")))
        for d, note in data.get("notes", {}).items():
            con.execute("UPDATE days SET note=? WHERE date=?", (note, d))
        con.execute("INSERT INTO meta VALUES('seeded','1')")


def now() -> dt.datetime:
    return dt.datetime.now(TZ)


def today() -> dt.date:
    return now().date()


def get_day(d: dt.date):
    with db() as con:
        return con.execute("SELECT * FROM days WHERE date=?", (d.isoformat(),)).fetchone()


def commute_plan(d: dt.date):
    r = get_day(d)
    if not r or r["kind"] not in ("work", "school") or not r["start"]:
        return None
    return transit.plan(d, r["kind"], r["start"], r["place"], TZ)


def commute_text(d: dt.date) -> str:
    p = commute_plan(d)
    return transit.fmt(p, TZ) if p else "в этот день ехать на работу/в школу не нужно"


# ---------- отображение ----------
def day_header(d: dt.date) -> str:
    with db() as con:
        r = con.execute("SELECT * FROM days WHERE date=?", (d.isoformat(),)).fetchone()
    head = f"{WEEKDAYS[d.weekday()]} {d:%d.%m}"
    if not r:
        return f"{head}: ❔ нет расписания"
    s = KIND_RU.get(r["kind"], r["kind"])
    if r["start"]:
        s += f" {r['start']}–{r['end']}"
    dest = transit.destination_for(d, r["kind"], r["start"], r["place"])
    if dest and r["kind"] == "work":
        s += f" @ {transit.PLACES[dest]['name']}"
    if r["note"]:
        s += f" ({r['note']})"
    return f"{head}: {s}"


def tasks_on(d: dt.date):
    with db() as con:
        return con.execute("SELECT * FROM tasks WHERE done=0 AND date=? ORDER BY time IS NULL, time, id",
                           (d.isoformat(),)).fetchall()


def overdue():
    with db() as con:
        return con.execute("SELECT * FROM tasks WHERE done=0 AND date<? ORDER BY date",
                           (today().isoformat(),)).fetchall()


def backlog():
    with db() as con:
        return con.execute("SELECT * FROM tasks WHERE done=0 AND date IS NULL ORDER BY id").fetchall()


def task_line(t) -> str:
    tm = f" ({t['time']})" if t["time"] else ""
    return f"• #{t['id']} {t['title']}{tm}"


def gym_week(d: dt.date) -> int:
    mon = d - dt.timedelta(days=d.weekday())
    with db() as con:
        return con.execute("SELECT COUNT(*) FROM gym WHERE date BETWEEN ? AND ?",
                           (mon.isoformat(), (mon + dt.timedelta(days=6)).isoformat())).fetchone()[0]


def gym_done(d: dt.date) -> bool:
    with db() as con:
        return con.execute("SELECT 1 FROM gym WHERE date=?", (d.isoformat(),)).fetchone() is not None


def overview(start: dt.date, days: int) -> str:
    out = []
    od = overdue()
    if od:
        out.append("⚠️ Просрочено:\n" + "\n".join(task_line(t) + f" [было на {t['date']}]" for t in od))
    for i in range(days):
        d = start + dt.timedelta(days=i)
        lines = [day_header(d)] + [task_line(t) for t in tasks_on(d)]
        if gym_done(d):
            lines.append("• 🏋️ зал ✅")
        out.append("\n".join(lines))
    bl = backlog()
    if bl:
        out.append("📥 Без даты:\n" + "\n".join(task_line(t) for t in bl))
    return "\n\n".join(out)


def reminders_text() -> str:
    with db() as con:
        rows = con.execute("SELECT * FROM reminders WHERE active=1 ORDER BY fire_at").fetchall()
    if not rows:
        return "нет активных напоминаний"
    return "\n".join(f"• #{r['id']} {r['fire_at']} — {r['text']}"
                     + ("" if r["repeat"] == "none" else f" (повтор: {r['repeat']})") for r in rows)


# ---------- инструменты для AI ----------
TOOLS = [
    {"name": "add_tasks", "description": "Добавить одну или несколько задач. Без date — в список «без даты».",
     "input_schema": {"type": "object", "properties": {"tasks": {"type": "array", "items": {
         "type": "object", "properties": {
             "title": {"type": "string"}, "date": {"type": "string", "description": "YYYY-MM-DD"},
             "time": {"type": "string", "description": "HH:MM"}}, "required": ["title"]}}},
         "required": ["tasks"]}},
    {"name": "complete_task", "description": "Отметить задачу выполненной.",
     "input_schema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "reschedule_task", "description": "Перенести задачу на другую дату/время (date=null — убрать дату).",
     "input_schema": {"type": "object", "properties": {"id": {"type": "integer"}, "date": {"type": ["string", "null"]},
                                                       "time": {"type": ["string", "null"]}}, "required": ["id"]}},
    {"name": "delete_task", "description": "Удалить задачу.",
     "input_schema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "add_reminder", "description": "Напоминание в конкретный момент. repeat: none, daily, weekly.",
     "input_schema": {"type": "object", "properties": {
         "text": {"type": "string"}, "at": {"type": "string", "description": "YYYY-MM-DD HH:MM"},
         "repeat": {"type": "string", "enum": ["none", "daily", "weekly"]}}, "required": ["text", "at"]}},
    {"name": "list_reminders", "description": "Показать активные напоминания.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "delete_reminder", "description": "Отключить напоминание.",
     "input_schema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    {"name": "set_day", "description": "Задать/изменить расписание дня (смена, школа, выходной и т.п.).",
     "input_schema": {"type": "object", "properties": {
         "date": {"type": "string"}, "kind": {"type": "string", "enum": list(KIND_RU)},
         "start": {"type": ["string", "null"]}, "end": {"type": ["string", "null"]},
         "note": {"type": ["string", "null"]},
         "place": {"type": ["string", "null"], "enum": ["school", "store", "hq", None],
                   "description": "Куда ехать: school, store (магазин), hq (центральный офис). Обычно не нужно — определяется само."}},
         "required": ["date", "kind"]}},
    {"name": "get_commute", "description": "Когда начать собираться, когда выходить и каким транспортом ехать (MVG) в этот день.",
     "input_schema": {"type": "object", "properties": {"date": {"type": "string"}}, "required": ["date"]}},
    {"name": "log_gym", "description": "Отметить, что был в зале в этот день.",
     "input_schema": {"type": "object", "properties": {"date": {"type": "string"}}, "required": ["date"]}},
    {"name": "add_expense", "description": "Записать трату. Вызывай всегда, когда он пишет, что что-то купил/потратил/съел за деньги.",
     "input_schema": {"type": "object", "properties": {
         "amount": {"type": "number", "description": "сумма в валюте currency"},
         "currency": {"type": "string", "enum": ["EUR", "UAH"], "description": "по умолчанию EUR; UAH — гривны с карты monobank"},
         "category": {"type": "string", "enum": EXPENSE_CATS},
         "note": {"type": "string"}, "date": {"type": "string", "description": "YYYY-MM-DD, по умолчанию сегодня"}},
         "required": ["amount", "category"]}},
    {"name": "expenses_report", "description": "Сводка трат за последние N дней по категориям.",
     "input_schema": {"type": "object", "properties": {"days": {"type": "integer"}}, "required": ["days"]}},
    {"name": "log_food", "description": "Записать съеденное (он работает на массу). Оценивай ккал и белок честно и примерно.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string"}, "kcal": {"type": "number"}, "protein": {"type": "number", "description": "граммы белка"},
         "date": {"type": "string"}}, "required": ["name", "kcal", "protein"]}},
    {"name": "food_report", "description": "Ккал и белок за сегодня/последние дни.",
     "input_schema": {"type": "object", "properties": {"days": {"type": "integer"}}, "required": ["days"]}},
    {"name": "item_save", "description": "Завести/обновить вещь для перепродажи (после фото). Без code — выдам новый.",
     "input_schema": {"type": "object", "properties": {
         "code": {"type": "string"}, "title": {"type": "string", "description": "заголовок Vinted на немецком"},
         "brand": {"type": "string"}, "size": {"type": "string"}, "price": {"type": "number"},
         "description": {"type": "string", "description": "описание на немецком"}}, "required": ["title"]}},
    {"name": "item_update", "description": "Сменить статус вещи: выставлен (на каком аккаунте), продан (за сколько), перефоткать и т.д.",
     "input_schema": {"type": "object", "properties": {
         "code": {"type": "string"}, "status": {"type": "string", "enum": ITEM_STATUSES},
         "account": {"type": "string"}, "sold_price": {"type": "number"}}, "required": ["code", "status"]}},
    {"name": "items_report", "description": "Сводка по вещам: статусы, аккаунты, продажи, что перефоткать.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_overview", "description": "Расписание и задачи на период (если нужно дальше 14 дней).",
     "input_schema": {"type": "object", "properties": {"start": {"type": "string"}, "days": {"type": "integer"}},
                      "required": ["start", "days"]}},
]


def run_tool(name: str, a: dict) -> str:
    with db() as con:
        if name == "add_tasks":
            ids = []
            for t in a["tasks"]:
                cur = con.execute("INSERT INTO tasks(title,date,time,created) VALUES(?,?,?,?)",
                                  (t["title"], t.get("date"), t.get("time"), now().isoformat()))
                ids.append(cur.lastrowid)
            return f"добавлены задачи: {ids}"
        if name == "complete_task":
            con.execute("UPDATE tasks SET done=1 WHERE id=?", (a["id"],))
            return "ок"
        if name == "reschedule_task":
            con.execute("UPDATE tasks SET date=?, time=? WHERE id=?", (a.get("date"), a.get("time"), a["id"]))
            return "ок"
        if name == "delete_task":
            con.execute("DELETE FROM tasks WHERE id=?", (a["id"],))
            return "ок"
        if name == "add_reminder":
            dt.datetime.strptime(a["at"], "%Y-%m-%d %H:%M")  # проверка формата
            cur = con.execute("INSERT INTO reminders(text,fire_at,repeat) VALUES(?,?,?)",
                              (a["text"], a["at"], a.get("repeat", "none")))
            return f"напоминание #{cur.lastrowid}"
        if name == "list_reminders":
            return reminders_text()
        if name == "delete_reminder":
            con.execute("UPDATE reminders SET active=0 WHERE id=?", (a["id"],))
            return "ок"
        if name == "set_day":
            con.execute("INSERT OR REPLACE INTO days(date,kind,start,end,note,place) VALUES(?,?,?,?,?,?)",
                        (a["date"], a["kind"], a.get("start"), a.get("end"), a.get("note"), a.get("place")))
            con.execute("DELETE FROM commute_sent WHERE date=?", (a["date"],))
            _plan_cache.pop(a["date"], None)
            return "ок"
        if name == "log_gym":
            con.execute("INSERT OR IGNORE INTO gym VALUES(?)", (a["date"],))
            return "ок"
    if name == "log_food":
        with db() as con:
            con.execute("INSERT INTO food(date,name,kcal,protein) VALUES(?,?,?,?)",
                        (a.get("date") or today().isoformat(), a["name"], float(a["kcal"]), float(a["protein"])))
        return "записано. " + food_line(dt.date.fromisoformat(a.get("date") or today().isoformat()))
    if name == "food_report":
        out = []
        for i in range(int(a["days"])):
            d = today() - dt.timedelta(days=i)
            out.append(f"{d:%d.%m}: " + food_line(d))
        return "\n".join(out)
    if name == "item_save":
        code = (a.get("code") or "").strip().upper() or next_code()
        stamp = now().isoformat()
        with db() as con:
            con.execute("""INSERT INTO items(code,title,brand,size,price,description,status,created,updated)
                           VALUES(?,?,?,?,?,?,'сфоткан',?,?)
                           ON CONFLICT(code) DO UPDATE SET title=excluded.title, brand=excluded.brand,
                           size=excluded.size, price=excluded.price, description=excluded.description,
                           updated=excluded.updated""",
                        (code, a["title"], a.get("brand"), a.get("size"), a.get("price"), a.get("description"), stamp, stamp))
        return f"вещь сохранена под кодом {code}"
    if name == "item_update":
        code = a["code"].strip().upper()
        with db() as con:
            if not con.execute("SELECT 1 FROM items WHERE code=?", (code,)).fetchone():
                con.execute("INSERT INTO items(code,created) VALUES(?,?)", (code, now().isoformat()))
            con.execute("UPDATE items SET status=?, account=COALESCE(?,account), sold_price=COALESCE(?,sold_price), "
                        "updated=? WHERE code=?",
                        (a["status"], a.get("account"), a.get("sold_price"), now().isoformat(), code))
        return f"{code}: {a['status']}"
    if name == "items_report":
        return items_text()
    if name == "add_expense":
        cur = a.get("currency", "EUR")
        eur = fx.to_eur(float(a["amount"]), cur)
        note = a.get("note", "") + (f" ({float(a['amount']):.2f} ₴)" if cur == "UAH" else "")
        with db() as con:
            con.execute("INSERT INTO expenses(date,amount,category,note) VALUES(?,?,?,?)",
                        (a.get("date") or today().isoformat(), eur, a["category"], note))
        return f"записано {eur:.2f} €. Сегодня всего: {spent_on(today()):.2f} €"
    if name == "expenses_report":
        return expenses_text(int(a["days"]))
    if name == "get_commute":
        return commute_text(dt.date.fromisoformat(a["date"]))
    if name == "get_overview":
        return overview(dt.date.fromisoformat(a["start"]), min(int(a["days"]), 45))
    return "неизвестный инструмент"


# ---------- AI ----------
client = None
if os.getenv("ANTHROPIC_API_KEY"):
    from anthropic import Anthropic
    client = Anthropic()

history: list[dict] = []


def system_prompt() -> str:
    n = now()
    return f"""Ты — Джарвис, личный ассистент владельца (как Джарвис у Тони Старка): умный, чёткий, с лёгким юмором. Пиши по-русски, коротко, по-дружески, без воды.
Ты не только планировщик. Он может спросить тебя ЧТО УГОДНО — про немецкий, экзамен, бюрократию, еду, зал, деньги, шмотки,
да хоть «что посмотреть вечером» — и ты отвечаешь по существу, как умный друг, сам, без отсылок «спроси у кого-то».
Если вопрос про то, что происходит сейчас (цены, новости, часы работы, погода где-то) и есть веб-поиск — поищи.
Инструменты для дел/еды/трат вызывай только когда он реально что-то сообщает или просит; на обычный вопрос просто отвечай.
Если он пишет коротко («ну и че», «и?») — пойми из контекста, что он ждёт, и ответь нормально.
Сейчас: {WEEKDAYS[n.weekday()]} {n:%d.%m.%Y %H:%M} (Мюнхен).

{cfg("profile", "")}
Вопросы «во сколько выходить/как ехать» — через инструмент get_commute. По плану подготовки к экзамену каждый день своя тема, объясняй по-русски с немецкими терминами. Любые траты, которые он упоминает, записывай через add_expense (несколько трат — несколько вызовов).
Цель по еде: {PROTEIN_GOAL:.0f} г белка и {KCAL_GOAL:.0f} ккал в день. Когда пишет, что съел, — log_food
(примерная честная оценка) и коротко скажи, сколько белка осталось и что можно доесть.
Если он пишет еду С ЦЕНОЙ («кебаб 8€», «Lidl 12,50 — курица, рис») — вызови И log_food, И add_expense.
Если в одном сообщении несколько вещей — по вызову на каждую. Если не сказал, когда — значит сегодня; «вчера» — вчерашняя дата.
ВСЕГДА заканчивай ответ текстом для него — никогда не отвечай пустым сообщением. После записи еды/трат отвечай коротко в формате:
✅ записал: …
🍽 сегодня: N ккал, белок N г (осталось N г)
💸 сегодня: N € · неделя: N €
Вещи для перепродажи: «выставил C0003 на аккаунт X», «продал A0123 за 45» → item_update.

ЕСЛИ ПРИШЛО ФОТО — пойми, что на нём:
1) Вещь/одежда/обувь/аксессуар для перепродажи → item_save и ответ, готовый к копированию в Vinted:
   🏷 Titel (немецкий, бренд + тип + цвет + размер, до 60 символов)
   📝 Beschreibung (немецкий, 3–5 строк: Zustand, Material/Maße только если видно на фото или бирке — НЕ выдумывай)
   💶 цена: реальный ориентир для б/у на Vinted DE (диапазон + что поставить)
   🔖 код вещи (если код есть в подписи к фото — используй его) и «напиши код на бирке».
2) Еда → log_food с оценкой ккал/белка.
3) План смен (Monatsübersicht / Schichtplan) → найди строку «{cfg("schedule_row", "его имя")}» и для КАЖДОГО дня вызови set_day.
   Правила: {cfg("shift_rules", "")}
4) Скрин банка (monobank и т.п.) → add_expense на КАЖДОЕ списание (минус), пополнения/плюсы НЕ записывай.
   Суммы в гривнах — currency="UAH" (я сам переведу в евро по курсу). Даты бери из заголовков («Сьогодні», «Вчора», «10 листопада»).
   Категории: супермаркеты → продукты, кафе/döner/рестораны → еда, подписки → связь/подписки, Deutsche Post/DHL → шмотки/товар.
   Если на скрине может быть часть, которую он уже присылал, — сначала проверь expenses_report и не дублируй.
5) Иначе — помоги по ситуации (письмо от Behörde: переведи и скажи, что делать; ценник; чек → add_expense). Главная проблема — бросает дела на полпути, поэтому важны маленькие посильные шаги.

Расписание и дела на 14 дней:
{overview(n.date(), 14)}

Зал на этой неделе: {gym_week(n.date())} из 2–3.

Правила:
- Любые изменения (задачи, напоминания, смены, зал) делай только через инструменты, потом коротко подтверди.
- Большие цели («сфоткать 200 вещей») разбивай на порции и раскидывай по дням под расписание:
  свободные дни — склад и объёмные дела; длинная смена — максимум одна мелочь; после школы — лёгкий вечер.
- Зал ставь в выходные или после ранних смен так, чтобы выходило 2–3 раза в неделю.
- В день не больше 3 главных задач. Если день перегружен — скажи и предложи перенос.
- Перед экзаменом закладывай немного подготовки.
- Когда он перечисляет, что хочет сделать («сегодня зал, отфоткать вещи, поесть, купить еду»), добавь КАЖДЫЙ пункт
  отдельной задачей на нужный день и расставь время по свободным окнам с учётом смены/школы и дороги.
  Покупки объединяй в одну задачу «🛒 купить: …». Еду/приёмы пищи ставь в разумное время. Если он сам назвал время — бери его.
  В ответе покажи план дня по порядку со временем.
- Если дата или время неясны — выбери разумное и скажи, что выбрал.
- Формат: YYYY-MM-DD, HH:MM. В ответах можно ссылаться на задачи по #номеру."""


WEB_SEARCH = {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}
_web_ok = os.getenv("WEB_SEARCH", "1") != "0"


def _create(sys_prompt, convo):
    """Запрос к AI. Пробуем с веб-поиском; если он недоступен для аккаунта — навсегда отключаем и повторяем."""
    global _web_ok
    tools = TOOLS + ([WEB_SEARCH] if _web_ok else [])
    try:
        return client.messages.create(model=MODEL, max_tokens=16000, system=sys_prompt, tools=tools, messages=convo)
    except Exception as e:  # noqa: BLE001
        if _web_ok and "web_search" in str(e):
            log.warning("веб-поиск недоступен, работаю без него: %s", e)
            _web_ok = False
            return client.messages.create(model=MODEL, max_tokens=16000, system=sys_prompt, tools=TOOLS, messages=convo)
        raise


def describe_action(name: str, a: dict, out: str) -> str:
    """Человеческое описание вызова инструмента — на случай, если AI не написал ответ."""
    try:
        if name == "add_tasks":
            return "добавил: " + ", ".join(t["title"] + (f" ({t['date']}" + (f" {t['time']}" if t.get("time") else "") + ")"
                                                         if t.get("date") else "") for t in a["tasks"])
        if name == "complete_task":
            return f"отметил выполненным #{a['id']}"
        if name == "delete_task":
            return f"удалил #{a['id']}"
        if name == "reschedule_task":
            return f"перенёс #{a['id']} на {a.get('date') or 'без даты'}" + (f" {a['time']}" if a.get("time") else "")
        if name == "add_reminder":
            return f"напомню {a['at']}: {a['text']}"
        if name == "set_day":
            return f"расписание {a['date']}: {KIND_RU.get(a['kind'], a['kind'])} {a.get('start') or ''}–{a.get('end') or ''}".rstrip("– ")
        if name == "log_gym":
            return f"зал засчитан ({a['date']}) 💪"
        if name == "log_food":
            return f"еда: {a['name']} — {a['kcal']:.0f} ккал, {a['protein']:.0f} г белка"
        if name == "add_expense":
            return f"трата: {a['amount']} {a.get('currency', 'EUR')} — {a.get('note') or a['category']}"
    except Exception:  # noqa: BLE001
        pass
    return f"{name}: {out[:80]}"


def quick_status() -> str:
    d = today()
    return f"{food_line(d)}\n💸 Сегодня: {spent_on(d):.2f} €"


def ask_claude(text: str, image: bytes | None = None, media_type: str = "image/jpeg") -> str:
    if client is None:
        return "AI не подключён — добавь ANTHROPIC_API_KEY в .env. Пока работают /today, /week, /tasks."
    history.append({"role": "user", "content": ("[фото] " + text) if image else text})
    msgs = history[-20:]
    while msgs and msgs[0]["role"] != "user":
        msgs = msgs[1:]
    convo = list(msgs)
    if image:  # картинку отправляем только в текущий запрос, в историю — текстовую пометку
        import base64
        convo[-1] = {"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type,
                                         "data": base64.b64encode(image).decode()}},
            {"type": "text", "text": text or "Что на фото? Действуй по правилам для фото."}]}
    sys_prompt = system_prompt()  # один и тот же на весь цикл, иначе API ругается на thinking-блоки
    actions: list[str] = []
    try:
        for _ in range(12):
            resp = _create(sys_prompt, convo)
            if resp.stop_reason == "tool_use":
                convo.append({"role": "assistant", "content": resp.content})
                results = []
                for b in resp.content:
                    if b.type == "tool_use":
                        try:
                            out = run_tool(b.name, b.input)
                        except Exception as e:  # noqa: BLE001
                            out = f"Ошибка: {e}"
                        log.info("tool %s %s -> %s", b.name, b.input, out[:200])
                        actions.append(describe_action(b.name, b.input, out))
                        results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
                convo.append({"role": "user", "content": results})
                continue
            answer = "".join(b.text for b in resp.content if b.type == "text").strip()
            if not answer:  # модель всё сделала, но не написала текст — рассказываем сами
                log.warning("пустой ответ AI (stop=%s), actions=%d", resp.stop_reason, len(actions))
                answer = ("✅ Сделал:\n" + "\n".join(f"• {a}" for a in actions)) if actions else \
                    "🤔 Не понял, что сделать. Напиши чуть иначе."
                answer += "\n\n" + quick_status()
            history.append({"role": "assistant", "content": answer})
            return answer
        answer = ("✅ Сделал:\n" + "\n".join(f"• {a}" for a in actions) + "\n\n" + quick_status()) if actions \
            else "Запутался, сформулируй попроще 🙏"
    except Exception:  # noqa: BLE001
        log.exception("Claude error")
        history.clear()  # сбросить историю, чтобы ошибка не повторялась
        answer = "🤖 AI сейчас не ответил, попробуй ещё раз через минуту."
    history.append({"role": "assistant", "content": answer})
    return answer


# ---------- кнопки ----------
def day_keyboard(d: dt.date, with_gym: bool) -> InlineKeyboardMarkup | None:
    rows = [[InlineKeyboardButton(f"✅ {t['title'][:28]}", callback_data=f"done:{t['id']}"),
             InlineKeyboardButton("➡️ завтра", callback_data=f"tmr:{t['id']}")] for t in tasks_on(d)]
    if with_gym and not gym_done(d):
        rows.append([InlineKeyboardButton("🏋️ Был в зале", callback_data=f"gym:{d.isoformat()}")])
    return InlineKeyboardMarkup(rows) if rows else None


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.from_user.id != OWNER_ID:
        await q.answer()
        return
    action, val = q.data.split(":", 1)
    with db() as con:
        if action == "done":
            con.execute("UPDATE tasks SET done=1 WHERE id=?", (int(val),))
            msg = "Красава ✅"
        elif action == "tmr":
            tmr = (today() + dt.timedelta(days=1)).isoformat()
            con.execute("UPDATE tasks SET date=? WHERE id=?", (tmr, int(val)))
            msg = "Перенёс на завтра"
        elif action == "gym":
            con.execute("INSERT OR IGNORE INTO gym VALUES(?)", (val,))
            msg = f"Зал засчитан 💪 ({gym_week(dt.date.fromisoformat(val))} на этой неделе)"
        else:
            msg = "?"
    await q.answer(msg)
    kb = q.message.reply_markup
    if kb:
        rows = [r for r in kb.inline_keyboard if all(b.callback_data != q.data for b in r)]
        await q.edit_message_reply_markup(InlineKeyboardMarkup(rows) if rows else None)


# ---------- команды и сообщения ----------
async def send_long(bot, chat_id, text, kb=None):
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)] or ["…"]
    for i, c in enumerate(chunks):
        await bot.send_message(chat_id, c, reply_markup=kb if i == len(chunks) - 1 else None)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not OWNER_ID:
        await update.message.reply_text(f"Твой Telegram ID: {uid}\nВпиши его в .env как OWNER_ID и перезапусти бота.")
        return
    if uid != OWNER_ID:
        return
    await update.message.reply_text(
        "Джарвис на связи 🤖 Я знаю твоё расписание и веду твои дела.\n\n"
        "Просто пиши мне обычным текстом:\n"
        "• «надо сфоткать 60 вещей до конца месяца»\n"
        "• «напомни завтра в 10 отправить посылку»\n"
        "• «в среду работаю с 10 до 19»\n"
        "• «сегодня хочу зал, отфоткать вещи, поесть и купить еду» — распределю по времени\n"
        "• «был в зале» / «что у меня завтра?»\n"
        "• «во сколько завтра выходить?»\n\n"
        "В рабочие и школьные дни сам напомню, когда собираться и когда выходить, с учётом задержек MVG.\n\n"
        f"Каждое утро — дата, погода, дорога и дела на день (в {MORNING} или раньше, если рано выходить). Вечером в {EVENING} — итог.\n"
        "🍽💸 Пиши, что съел и сколько потратил: «кебаб 8 €», «вчера Lidl 12,50 — курица, рис». Я считаю калории, белок и деньги.\n\n"
        "Команды: /day (сегодня: еда и траты) /food /money /today /week /exam /report /route")


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = today()
    await send_long(context.bot, update.effective_chat.id, overview(d, 1), day_keyboard(d, True))


async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_long(context.bot, update.effective_chat.id,
                    overview(today(), 7) + f"\n\n🏋️ Зал на этой неделе: {gym_week(today())}/3")


async def cmd_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_long(context.bot, update.effective_chat.id, overview(today(), 30))


async def cmd_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = today()
    r = get_day(d)
    if not r or not r["start"] or now() > dt.datetime.combine(d, dt.time(*map(int, r["start"].split(":"))), tzinfo=TZ):
        d = d + dt.timedelta(days=1)
    text = await asyncio.to_thread(commute_text, d)
    await update.message.reply_text(f"{day_header(d)}\n\n{text}")


def _split_items(text: str) -> list[str]:
    import re
    return [x.strip(" .-•") for x in re.split(r"[,;\n]+", text) if x.strip(" .-•")]


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/add зал, фото вещей, купить еду — сразу на сегодня (работает и без AI).
    /add завтра: ... — на завтра."""
    text = (update.message.text.split(maxsplit=1) + [""])[1].strip()
    d = today()
    low = text.lower()
    if low.startswith("завтра"):
        d = d + dt.timedelta(days=1)
        text = text[6:].lstrip(" :,-")
    items = _split_items(text)
    if not items:
        await update.message.reply_text("Напиши так: /add зал, отфоткать вещи, купить еду\nили /add завтра: посылки, зал")
        return
    run_tool("add_tasks", {"tasks": [{"title": t, "date": d.isoformat()} for t in items]})
    await send_long(context.bot, update.effective_chat.id,
                    f"Добавил на {WEEKDAYS[d.weekday()]} {d:%d.%m} ✅\n\n" + overview(d, 1), day_keyboard(d, d == today()))


async def cmd_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(reminders_text())


async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    msg = update.message
    if msg.photo:
        f = await msg.photo[-1].get_file()
        mt = "image/jpeg"
    else:  # фото, отправленное «файлом»
        f = await msg.document.get_file()
        mt = msg.document.mime_type or "image/jpeg"
    data = bytes(await f.download_as_bytearray())
    answer = await asyncio.to_thread(ask_claude, msg.caption or "", data, mt)
    await send_long(context.bot, update.effective_chat.id, answer)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    answer = await asyncio.to_thread(ask_claude, update.message.text)
    await send_long(context.bot, update.effective_chat.id, answer)


# ---------- автоматические задания ----------
async def ensure_brief(context: ContextTypes.DEFAULT_TYPE):
    """Утренний бриф всегда приходит ПЕРВЫМ: если что-то хочет написать утром раньше брифа — сначала бриф."""
    d, n = today(), now()
    if 4 <= n.hour < 12 and _mark(d, "brief"):
        await send_brief(context, d)


async def job_reminders(context: ContextTypes.DEFAULT_TYPE):
    stamp = now().strftime("%Y-%m-%d %H:%M")
    with db() as con:
        rows = con.execute("SELECT * FROM reminders WHERE active=1 AND fire_at<=?", (stamp,)).fetchall()
    if rows:
        await ensure_brief(context)
    for r in rows:
        await context.bot.send_message(OWNER_ID, f"⏰ {r['text']}")
        with db() as con:
            if r["repeat"] == "none":
                con.execute("UPDATE reminders SET active=0 WHERE id=?", (r["id"],))
            else:
                step = dt.timedelta(days=1 if r["repeat"] == "daily" else 7)
                nxt = dt.datetime.strptime(r["fire_at"], "%Y-%m-%d %H:%M")
                while nxt.strftime("%Y-%m-%d %H:%M") <= stamp:
                    nxt += step
                con.execute("UPDATE reminders SET fire_at=? WHERE id=?", (nxt.strftime("%Y-%m-%d %H:%M"), r["id"]))


_plan_cache: dict[str, tuple[dt.datetime, dict | None]] = {}


def _cached_plan(d: dt.date, max_age_min: int):
    key = d.isoformat()
    hit = _plan_cache.get(key)
    if hit and (now() - hit[0]).total_seconds() < max_age_min * 60:
        return hit[1]
    p = commute_plan(d)
    _plan_cache[key] = (now(), p)
    return p


def _mark(d: dt.date, kind: str) -> bool:
    """True, если сообщение этого типа сегодня ещё не отправлялось (и сразу помечает)."""
    with db() as con:
        cur = con.execute("INSERT OR IGNORE INTO commute_sent VALUES(?,?)", (d.isoformat(), kind))
        return cur.rowcount == 1


CHECKINS = [t.strip() for t in os.getenv("CHECKIN_TIMES", "12:30,17:00").split(",") if t.strip()]
SLEEP_HOURS = float(os.getenv("SLEEP_HOURS", "7.5"))
LEADS = sorted((int(x) for x in os.getenv("LEAD_MINUTES", "60,15").split(",") if x.strip()), reverse=True)


def _at(d: dt.date, hm: str) -> dt.datetime:
    h, m = map(int, hm.split(":"))
    return dt.datetime.combine(d, dt.time(h, m), tzinfo=TZ)


async def job_tasks(context: ContextTypes.DEFAULT_TYPE):
    """Напоминания по задачам со временем: заранее (LEADS) и в момент. Не будят раньше времени подъёма."""
    d, n = today(), now()
    timed = [t for t in tasks_on(d) if t["time"]]
    if not timed:
        return
    w = await asyncio.to_thread(wake_time, d)
    for t in timed:
        at = _at(d, t["time"])
        for lead in (LEADS if not w or n >= w else []):  # по умолчанию за 60 и за 15 минут
            if at - dt.timedelta(minutes=lead) <= n < at and _mark(d, f"t{t['id']}-{lead}"):
                await ensure_brief(context)
                left = int((at - n).total_seconds() // 60)
                when = f"{left // 60} ч {left % 60} мин" if left >= 60 else f"{left} мин"
                await context.bot.send_message(OWNER_ID, f"⏰ Через {when}: {t['title']} ({t['time']})")
                for smaller in LEADS:  # не дублировать, если опоздали к раннему напоминанию
                    if smaller < lead and left <= smaller:
                        _mark(d, f"t{t['id']}-{smaller}")
                break
        if at <= n < at + dt.timedelta(minutes=30) and _mark(d, f"t{t['id']}-0"):
            await ensure_brief(context)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Сделал", callback_data=f"done:{t['id']}"),
                                        InlineKeyboardButton("➡️ Завтра", callback_data=f"tmr:{t['id']}")]])
            await context.bot.send_message(OWNER_ID, f"▶️ Пора: {t['title']}", reply_markup=kb)


async def job_checkins(context: ContextTypes.DEFAULT_TYPE):
    """Днём: что осталось на сегодня (если что-то осталось)."""
    d, n = today(), now()
    for hm in CHECKINS:
        at = _at(d, hm)
        if at <= n < at + dt.timedelta(hours=2) and _mark(d, f"check-{hm}"):
            open_tasks = tasks_on(d)
            if not open_tasks:
                continue
            r = get_day(d)
            busy = ""
            if r and r["end"] and r["kind"] in ("work", "school") and n < _at(d, r["end"]):
                busy = f"\n(после {r['end']}, когда освободишься)"
            text = f"👀 На сегодня ещё осталось ({len(open_tasks)}):{busy}\n" + "\n".join(task_line(t) for t in open_tasks)
            await send_long(context.bot, OWNER_ID, text, day_keyboard(d, True))


def wake_time(d: dt.date) -> dt.datetime | None:
    """Во сколько вставать: перед сборами или за 45 мин до самой ранней задачи со временем."""
    cands = []
    p = _cached_plan(d, 180)
    if p:
        cands.append(p["get_ready"])
    timed = [t for t in tasks_on(d) if t["time"]]
    if timed:
        cands.append(min(_at(d, t["time"]) for t in timed) - dt.timedelta(minutes=45))
    return min(cands) if cands else None


async def job_bedtime(context: ContextTypes.DEFAULT_TYPE):
    """За 30 минут до отбоя — «пора закругляться»."""
    n = now()
    tomorrow = (n + dt.timedelta(hours=6)).date() if n.hour >= 18 else n.date()
    w = await asyncio.to_thread(wake_time, tomorrow)
    if not w:
        return
    bed = w - dt.timedelta(hours=SLEEP_HOURS)
    if bed - dt.timedelta(minutes=30) <= n < bed + dt.timedelta(minutes=60) and _mark(tomorrow, "bedtime"):
        await context.bot.send_message(
            OWNER_ID, f"😴 Через {max(0, int((bed - n).total_seconds() // 60))} мин пора спать (в {bed:%H:%M}).\n"
                      f"Завтра вставать в {w:%H:%M}. Положи телефон, собери вещи на утро 👕")


async def job_commute(context: ContextTypes.DEFAULT_TYPE):
    d, n = today(), now()
    if n.hour < 4 or n.hour > 15:
        return
    p = await asyncio.to_thread(_cached_plan, d, 60)
    if not p or n > p["leave"]:
        return
    if n >= p["get_ready"] and _mark(d, "ready"):
        await ensure_brief(context)
        await context.bot.send_message(OWNER_ID, "🚿 Пора собираться!\n\n" + transit.fmt(p, TZ))
    if n >= p["leave"] - dt.timedelta(minutes=15) and _mark(d, "leave15"):
        fresh = await asyncio.to_thread(_cached_plan, d, 0)  # свежие данные с задержками
        if fresh:
            await context.bot.send_message(
                OWNER_ID, f"🚪 Через {max(1, int((fresh['leave'] - now()).total_seconds() // 60))} мин выходить!\n\n"
                + transit.fmt(fresh, TZ, header=False))


def build_brief(d: dt.date) -> str:
    """Утренний бриф: дата, погода, день, дорога, дела, зал, экзамен."""
    parts = [f"☀️ Доброе утро! Сегодня {WEEKDAYS_FULL[d.weekday()]}, {d.day} {MONTHS[d.month - 1]}"]
    parts.append(weather.today_text(d))

    day = day_header(d).split(": ", 1)[1]
    p = commute_plan(d)
    block = f"📅 {day}"
    if p:
        block += "\n" + transit.fmt(p, TZ, header=False)
    parts.append(block)

    od, ts = overdue(), tasks_on(d)
    if ts or od:
        lines = ["📝 Дела на сегодня:"] + [task_line(t) for t in ts]
        if od:
            lines += ["⚠️ Хвосты с прошлых дней:"] + [task_line(t) for t in od]
        parts.append("\n".join(lines))
    else:
        parts.append("📝 Дел на сегодня нет — напиши, что хочешь сделать")

    y = d - dt.timedelta(days=1)
    yk, yp = food_day(y)
    money = f"📒 Вчера: {yk:.0f} ккал, белок {yp:.0f} г · потрачено {spent_on(y):.2f} €"
    le = last_entry("expenses")
    if not le or (d - le).days >= 2:
        money += f"\n✍️ Траты последний раз записывал {ago(le)} — скинь, что тратил"
    parts.append(money)

    g = gym_week(d)
    gym = f"🏋️ Зал на этой неделе: {g}/3"
    if g < 2 and d.weekday() >= 3:
        gym += " — пора догонять"
    parts.append(gym)

    left = (EXAM_DATE - d).days
    if 0 < left <= 21:
        parts.append(f"📝 До экзамена {left} дн.")
    elif left == 0:
        parts.append("📝 СЕГОДНЯ ЭКЗАМЕН. Удачи, ты всё сможешь 💪")
    return "\n\n".join(parts)


def brief_time(d: dt.date) -> dt.datetime:
    """Обычно MORNING_TIME, но не позже чем за 10 минут до начала сборов."""
    h, m = map(int, MORNING.split(":"))
    t = dt.datetime.combine(d, dt.time(h, m), tzinfo=TZ)
    p = _cached_plan(d, 180)
    if p:
        t = min(t, p["get_ready"] - dt.timedelta(minutes=10))
    w = wake_time(d)  # ранние дела: бриф сразу после подъёма
    if w:
        t = min(t, w)
    return t


async def send_brief(context: ContextTypes.DEFAULT_TYPE, d: dt.date):
    text = await asyncio.to_thread(build_brief, d)
    await send_long(context.bot, OWNER_ID, text, day_keyboard(d, True))
    if client and tasks_on(d):
        plan = await asyncio.to_thread(
            ask_claude, "[авто, утро] Расставь мои дела на сегодня по времени с учётом смены/школы, дороги "
                        "и погоды. ОБЯЗАТЕЛЬНО проставь каждой задаче без времени время через reschedule_task "
                        "(дата сегодняшняя) — по нему я получу напоминания днём. Ответ коротко, списком со "
                        "временем. Одна строка мотивации в конце.")
        await send_long(context.bot, OWNER_ID, plan)


async def job_brief(context: ContextTypes.DEFAULT_TYPE):
    d, n = today(), now()
    if n.hour < 4 or n.hour >= 12:
        return
    t = await asyncio.to_thread(brief_time, d)
    if n >= t and _mark(d, "brief"):
        await send_brief(context, d)


async def cmd_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_brief(context, today())


async def job_evening_check(context: ContextTypes.DEFAULT_TYPE):
    """Итог дня: в EVENING_TIME или сразу после, если ноут спал (до 2 ночи)."""
    d, n = today(), now()
    h, m = map(int, EVENING.split(":"))
    if n.time() >= dt.time(h, m) and _mark(d, "evening"):
        await job_evening(context)


async def job_hello(context: ContextTypes.DEFAULT_TYPE):
    d = today()
    ai = "🧠 AI: подключён" if client else "🧠 AI: нет ключа — понимаю только команды (/add, /today…)"
    t = await asyncio.to_thread(brief_time, d + dt.timedelta(days=1) if now().hour >= 12 else d)
    await context.bot.send_message(
        OWNER_ID, f"🤖 Джарвис запущен.\n{ai}\n☀️ Следующий утренний бриф: {t:%d.%m %H:%M}\n"
                  f"🔄 Автообновление: {'вкл, версия ' + (updater.local_version()[:7] or 'новая') if updater.enabled() else 'выкл'}\n"
                  "⚠️ Работаю, только пока ноут включён и не спит.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await job_hello(context)


async def job_evening(context: ContextTypes.DEFAULT_TYPE):
    d = today()
    open_tasks = tasks_on(d)
    text = "🌙 Итог дня\n\n"
    text += ("Остались задачи — отметь, что сделал, остальное перенесу:" if open_tasks
             else "Все задачи на сегодня закрыты 🔥")
    text += f"\n\n🏋️ Зал на этой неделе: {gym_week(d)}/3"
    text += "\n" + food_line(d)
    if food_day(d)[0] == 0 and spent_on(d) == 0:
        text += "\n✍️ Сегодня ни еды, ни трат не записано. Напиши одним сообщением, что ел и сколько потратил."
    elif food_day(d)[0] == 0:
        text += "\n✍️ Еду сегодня не записывал. Что ел?"
    text += f"\n💸 Потрачено сегодня: {spent_on(d):.2f} € · за 7 дней: {expenses_text(7).splitlines()[0]}"
    tomorrow = d + dt.timedelta(days=1)
    text += "\n\nЗавтра: " + day_header(tomorrow).split(": ", 1)[1]
    try:
        w = await asyncio.to_thread(weather.summary, tomorrow)
        e, t = weather._code(w["day_code"])
        text += f"\n{e} {w['tmin']:.0f}…{w['tmax']:.0f}°, {t}" + (" ☂️ зонт!" if w["rain_hours"] else "")
    except Exception:  # noqa: BLE001
        pass
    p = await asyncio.to_thread(commute_plan, tomorrow)
    if p:
        text += "\n\n" + transit.fmt(p, TZ, header=False)
        text += f"\n😴 Чтобы выспаться (8 ч), ляг до {(p['get_ready'] - dt.timedelta(hours=8)):%H:%M}"
    await send_long(context.bot, OWNER_ID, text, day_keyboard(d, True))


def parse_hm(s: str) -> dt.time:
    h, m = map(int, s.split(":"))
    return dt.time(h, m, tzinfo=TZ)


EXAM_PLAN = None
_p = os.path.join(BASE, "exam_plan.json")
if os.path.exists(_p):
    with open(_p, encoding="utf-8") as _f:
        EXAM_PLAN = json.load(_f)
QUIZ_TIME = os.getenv("QUIZ_TIME", "19:30")


def exam_topic(d: dt.date):
    return (EXAM_PLAN or {}).get("days", {}).get(d.isoformat())


def make_exam_lesson(topic: dict) -> dict | None:
    """AI: короткая шпаргалка + 5 вопросов. Отдельный запрос, без истории чата."""
    if client is None:
        return None
    prompt = (f"Подготовь урок к Verkäufer Abschlussprüfung (IHK). Bereich: {topic['area']}. Тема: {topic['topic']}.\n"
              "Ученик — Azubi, русскоязычный, живёт в Германии. Верни ТОЛЬКО JSON без markdown:\n"
              '{"cheat": "шпаргалка 6-10 строк: по-русски, немецкие термины в скобках, формулы/схемы если есть, '
              'один пример с числами если тема про расчёты", '
              '"questions": [{"q": "вопрос (до 250 символов, немецкий термин + русский)", '
              '"options": ["4 варианта, каждый до 90 символов"], "correct": 0, "explain": "до 180 символов"}]}\n'
              "Ровно 5 вопросов, как на настоящем экзамене IHK, правильный ответ в разных позициях. "
              "Только проверенные факты немецкого права и коммерческого счёта; если в расчёте есть числа — пересчитай.")
    try:
        for attempt in range(2):
            r = client.messages.create(model=MODEL, max_tokens=16000, messages=[{"role": "user", "content": prompt}])
            txt = "".join(b.text for b in r.content if b.type == "text").strip()
            txt = txt[txt.find("{"): txt.rfind("}") + 1]
            try:
                data = json.loads(txt)
                if data.get("questions"):
                    return data
            except json.JSONDecodeError:
                log.warning("exam lesson: не JSON (попытка %d, stop=%s): %s", attempt + 1, r.stop_reason, txt[:200])
        return None
    except Exception:  # noqa: BLE001
        log.exception("exam lesson failed")
        return None


async def send_exam(context: ContextTypes.DEFAULT_TYPE, d: dt.date):
    t = exam_topic(d)
    left = (EXAM_DATE - d).days
    if not t:
        await context.bot.send_message(OWNER_ID, f"📚 На сегодня темы нет. До экзамена {left} дн.")
        return
    head = f"📚 Экзамен через {left} дн. · {t['area']}\nТема дня ({t['minutes']} мин): {t['topic']}"
    lesson = await asyncio.to_thread(make_exam_lesson, t)
    if not lesson:
        await context.bot.send_message(OWNER_ID, head + "\n\n(AI не ответил — повтори тему по учебнику, /exam чтобы попробовать ещё раз)")
        return
    await send_long(context.bot, OWNER_ID, head + "\n\n📝 Шпаргалка:\n" + lesson.get("cheat", ""))
    for i, q in enumerate(lesson.get("questions", [])[:5], 1):
        try:
            opts = [str(o)[:100] for o in q["options"]][:10]
            await context.bot.send_poll(OWNER_ID, f"{i}/5. {q['q']}"[:300], opts, type="quiz",
                                        correct_option_id=int(q["correct"]), is_anonymous=True,
                                        explanation=str(q.get("explain", ""))[:200])
        except Exception:  # noqa: BLE001
            log.exception("poll failed")


def exam_send_time(d: dt.date) -> dt.datetime:
    """Вечером: в QUIZ_TIME, но не раньше чем через 1,5 ч после смены/школы."""
    t = _at(d, QUIZ_TIME)
    r = get_day(d)
    if r and r["end"]:
        t = max(t, _at(d, r["end"]) + dt.timedelta(minutes=90))
    return t


async def job_exam(context: ContextTypes.DEFAULT_TYPE):
    d, n = today(), now()
    if not exam_topic(d) or n.hour >= 23:
        return
    if n >= exam_send_time(d) and _mark(d, "exam"):
        await send_exam(context, d)


async def cmd_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _mark(today(), "exam")  # вечером второй раз не пришлёт
    await update.message.reply_text("Готовлю урок… ⏳")
    await send_exam(context, today())


async def cmd_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = today()
    days = "\n".join(f"• {WEEKDAYS[x.weekday()]} {x:%d.%m}: {spent_on(x):.2f} €"
                     for x in (d - dt.timedelta(days=i) for i in range(6, -1, -1)))
    await update.message.reply_text(
        f"💸 Последний раз записывал траты: {ago(last_entry('expenses'))}\n\n"
        f"По дням:\n{days}\n\n7 дней: {expenses_text(7)}\n\n30 дней: {expenses_text(30)}\n\n"
        "Записать: «кебаб 8 €» или «Lidl 12,50»")


async def cmd_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = today()
    if context.args and context.args[0].lower() in ("вчера", "yesterday", "y"):
        d -= dt.timedelta(days=1)
    await update.message.reply_text(day_log(d))


async def job_update(context: ContextTypes.DEFAULT_TYPE, manual: bool = False):
    try:
        sha = await asyncio.to_thread(updater.update_if_needed)
    except Exception as e:  # noqa: BLE001
        log.warning("update check failed: %s", e)
        if manual:
            await context.bot.send_message(OWNER_ID, f"⚠️ Не смог проверить обновления: {e}")
        return
    if sha:
        await context.bot.send_message(OWNER_ID, f"🔄 Джарвис обновился ({sha[:7]}), перезапускаюсь…")
        await asyncio.sleep(2)
        os._exit(0)  # start_jarvis.bat запустит заново уже с новым кодом
    elif manual:
        await context.bot.send_message(OWNER_ID, f"✅ Уже последняя версия ({updater.local_version()[:7] or '—'})")


async def cmd_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not updater.enabled():
        await update.message.reply_text("Автообновление выключено (AUTO_UPDATE=0 в .env)")
        return
    await job_update(context, manual=True)


WEEKLY_TIME = os.getenv("WEEKLY_TIME", "20:00")


def weekly_report(d: dt.date) -> str:
    mon = d - dt.timedelta(days=d.weekday())
    a, b = mon.isoformat(), d.isoformat()
    with db() as con:
        done = con.execute("SELECT COUNT(*) FROM tasks WHERE done=1 AND date BETWEEN ? AND ?", (a, b)).fetchone()[0]
        left = con.execute("SELECT COUNT(*) FROM tasks WHERE done=0 AND date BETWEEN ? AND ?", (a, b)).fetchone()[0]
        prot = con.execute("SELECT COALESCE(SUM(protein),0), COUNT(DISTINCT date) FROM food WHERE date BETWEEN ? AND ?",
                           (a, b)).fetchone()
        sold = con.execute("SELECT COUNT(*), COALESCE(SUM(sold_price),0) FROM items WHERE status='продан' "
                           "AND substr(updated,1,10) BETWEEN ? AND ?", (a, b)).fetchone()
        shot = con.execute("SELECT COUNT(*) FROM items WHERE substr(created,1,10) BETWEEN ? AND ?", (a, b)).fetchone()[0]
    g = gym_week(d)
    total = done + left
    lines = [f"📊 Итог недели {mon:%d.%m}–{d:%d.%m}",
             f"✅ Дела: {done} из {total}" + (" 🔥" if total and done / total >= 0.7 else ""),
             f"🏋️ Зал: {g}/3" + (" — красава" if g >= 2 else " — на следующей неделе догоняем"),
             f"🍗 Белок в среднем: {prot[0] / prot[1]:.0f} г/день" if prot[1] else "🍗 Еду не записывал",
             f"💸 Траты: {expenses_text(7).splitlines()[0]}",
             f"📸 Новых вещей сфоткано: {shot} · 💰 продано: {sold[0]} на {sold[1]:.2f} €"]
    left_exam = (EXAM_DATE - d).days
    if left_exam > 0:
        lines.append(f"📝 До экзамена {left_exam} дн.")
    lines.append("\nНапиши, что главное на следующую неделю, — раскидаю по дням.")
    return "\n".join(lines)


async def job_weekly(context: ContextTypes.DEFAULT_TYPE):
    d, n = today(), now()
    if d.weekday() == 6 and n >= _at(d, WEEKLY_TIME) and n.hour < 23 and _mark(d, "weekly"):
        await send_long(context.bot, OWNER_ID, weekly_report(d))


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(weekly_report(today()))


async def cmd_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(items_text())


async def cmd_food(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = today()
    with db() as con:
        rows = con.execute("SELECT name, kcal, protein FROM food WHERE date=? ORDER BY id", (d.isoformat(),)).fetchall()
    body = "\n".join(f"• {r['name']}: {r['kcal']:.0f} ккал, {r['protein']:.0f} г белка" for r in rows) or "пока ничего"
    k, p = food_day(d)
    week = "\n".join(f"• {WEEKDAYS[x.weekday()]} {x:%d.%m}: {food_day(x)[0]:.0f} ккал, белок {food_day(x)[1]:.0f} г"
                     for x in (d - dt.timedelta(days=i) for i in range(6, -1, -1)))
    await update.message.reply_text(f"🍽 Сегодня:\n{body}\n\n{food_line(d)}\n"
                                    f"Осталось: {max(0, PROTEIN_GOAL - p):.0f} г белка, {max(0, KCAL_GOAL - k):.0f} ккал\n\n"
                                    f"За неделю:\n{week}\n\nПоследняя запись еды: {ago(last_entry('food'))}")


def main():
    init_db()
    load_seed()
    load_extras()
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
    app.add_handler(CommandHandler("start", cmd_start))
    if OWNER_ID:
        me = filters.User(user_id=OWNER_ID)
        app.add_handler(CommandHandler("today", cmd_today, filters=me))
        app.add_handler(CommandHandler("week", cmd_week, filters=me))
        app.add_handler(CommandHandler("tasks", cmd_tasks, filters=me))
        app.add_handler(CommandHandler("reminders", cmd_reminders, filters=me))
        app.add_handler(CommandHandler("route", cmd_route, filters=me))
        app.add_handler(CommandHandler("add", cmd_add, filters=me))
        app.add_handler(CommandHandler("morning", cmd_morning, filters=me))
        app.add_handler(CommandHandler("status", cmd_status, filters=me))
        app.add_handler(CommandHandler("money", cmd_money, filters=me))
        app.add_handler(CommandHandler("exam", cmd_exam, filters=me))
        app.add_handler(CommandHandler("update", cmd_update, filters=me))
        app.add_handler(CommandHandler("report", cmd_report, filters=me))
        app.add_handler(CommandHandler("items", cmd_items, filters=me))
        app.add_handler(CommandHandler("food", cmd_food, filters=me))
        app.add_handler(CommandHandler("day", cmd_day, filters=me))
        app.add_handler(MessageHandler(me & filters.TEXT & ~filters.COMMAND, on_text))
        app.add_handler(MessageHandler(me & (filters.PHOTO | filters.Document.IMAGE), on_photo))
        app.add_handler(CallbackQueryHandler(on_button))
        jq = app.job_queue
        jq.run_repeating(job_reminders, interval=60, first=5)
        jq.run_repeating(job_commute, interval=120, first=20)
        jq.run_repeating(job_tasks, interval=60, first=25)
        jq.run_repeating(job_checkins, interval=120, first=30)
        jq.run_repeating(job_bedtime, interval=120, first=35)
        jq.run_repeating(job_exam, interval=120, first=40)
        jq.run_repeating(job_weekly, interval=300, first=45)
        if updater.enabled():
            jq.run_repeating(job_update, interval=180, first=60)
        jq.run_repeating(job_brief, interval=60, first=10)
        jq.run_repeating(job_evening_check, interval=60, first=15)
        jq.run_once(job_hello, when=3)
    log.info("Бот запущен. OWNER_ID=%s, AI=%s", OWNER_ID or "не задан", "да" if client else "нет")
    if not OWNER_ID:
        print("\n!!! OWNER_ID не задан: бот НЕ будет ничего присылать сам.\n"
              "    Напиши боту /start, впиши ID в .env как OWNER_ID=... и перезапусти.\n")
    app.run_polling()


if __name__ == "__main__":
    main()

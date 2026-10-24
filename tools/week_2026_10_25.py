"""Собирает посты 25.10–01.11.2026 и дописывает их в queue.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from card import card

TZ = "+01:00"  # с 25.10 Германия на зимнем времени
FOOT = "\n\nСохрани, чтобы не забыть 📌\n<b>Lingofy Deutsch</b>"
FOOT2 = "\n\nСохрани, пригодится 📌\n<b>Lingofy Deutsch</b>"
WDT = "WORT DES TAGES"

def wort(day, word, ru, ex, exru, cap_body):
    return dict(id=f"{day}-m", at=f"{day}T08:45:00{TZ}", type="photo",
                photo=card(tag=WDT, de=word, ru=ru, ex=ex, exru=exru, note="Сохрани, чтобы не забыть"),
                caption=f"🇩🇪 <b>Wort des Tages</b>\n\n{cap_body}{FOOT}")

def quiz(day, q, options, correct, expl):
    return dict(id=f"{day}-q", at=f"{day}T13:00:00{TZ}", type="quiz",
                question=q, options=options, correct=correct, explanation=expl)

def evening(day, tag, de, ru, ex, exru, note, cap):
    return dict(id=f"{day}-e", at=f"{day}T19:00:00{TZ}", type="photo",
                photo=card(tag=tag, de=de, ru=ru, ex=ex, exru=exru, note=note), caption=cap)

P = []

# ---------- Вс 25.10 (пропущенные посты прошлого воскресенья) ----------
d = "2026-10-25"
P.append(wort(d, "die Sonntagsruhe", "воскресный покой", "Am Sonntag ist Ruhe angesagt.", "В воскресенье положено отдыхать.",
 "<b>die Sonntagsruhe</b> — воскресный покой 🤫🛋📌\n\n<i>Am Sonntag ist Ruhe angesagt.</i>\n— В воскресенье положено отдыхать.\n\n"
 "💡 <b>Использование</b>\nВ Германии по воскресеньям большинство магазинов закрыто, а шуметь — сверлить, пылесосить, выбрасывать стекло в контейнер — не принято. Это и есть Sonntagsruhe.\n\n"
 "<b>Примеры:</b>\n• in Ruhe — спокойно, не торопясь\n• Lass mich in Ruhe! — оставь меня в покое!\n• die Ruhezeit — время тишины (например, ночью)\n\n😌 Как проводишь свой Sonntag?"))
P.append(quiz(d, "🤝 Вставь правильно: «Ich helfe ___ Freund.»", ["meinen", "meinem", "mein"], 1,
 "helfen требует дательного падежа: Ich helfe meinem Freund. Как и по-русски: «помогаю (кому?) другу»."))
P.append(evening(d, "ТЕСТ", "5 вопросов", "сколько наберёшь?", "Ответы под спойлером", "Проверь себя по прошлым постам", "Сохрани и повтори",
 "🧠 <b>Тест: 5 вопросов</b>\n\nПо темам, которые уже были в канале. Ответь в голове, потом открой спойлер 👇\n\n"
 "1️⃣ Как одним словом сказать «радость предвкушения»?\n<tg-spoiler>die Vorfreude</tg-spoiler>\n\n"
 "2️⃣ Какой артикль у слова Mädchen?\n<tg-spoiler>das — слова на -chen среднего рода</tg-spoiler>\n\n"
 "3️⃣ На двери написано «Drücken». Что делать?\n<tg-spoiler>толкать от себя</tg-spoiler>\n\n"
 "4️⃣ Ich ___ nach München gefahren.\n<tg-spoiler>bin — глаголы движения с sein</tg-spoiler>\n\n"
 "5️⃣ Что значит «Hast du Bock?»\n<tg-spoiler>Хочешь? / Есть настрой?</tg-spoiler>\n\n"
 "🏆 5 из 5 — ты огонь! 3–4 — отлично! Меньше 3 — пролистай канал ещё раз 😉\n\nСохрани и повтори 📌\n<b>Lingofy Deutsch</b>"))

# ---------- Пн 26.10 ----------
d = "2026-10-26"
P.append(wort(d, "der Muskelkater", "боль в мышцах после спорта", "Nach dem Training habe ich Muskelkater.", "После тренировки у меня болят мышцы.",
 "<b>der Muskelkater</b> — боль в мышцах после нагрузки 💪😩📌\nДословно: «мышечный кот» 🐱\n\n<i>Nach dem Training habe ich Muskelkater.</i>\n— После тренировки у меня болят мышцы.\n\n"
 "💡 <b>Использование</b>\nПо-русски говорят «крепатура» или «мышцы болят», а немцы — одним словом.\n\n"
 "<b>Примеры:</b>\n• Muskelkater haben — когда болят мышцы\n• Ich habe Muskelkater in den Beinen. — у меня болят ноги после нагрузки\n• der Kater — ещё и похмелье (об этом в пятницу 😉)\n\n🏋️ Начинаешь неделю со спорта?"))
P.append(quiz(d, "🤔 Ложный друг: что значит «das Rezept»?", ["Только рецепт блюда", "И рецепт блюда, и рецепт врача", "Квитанция об оплате"], 1,
 "das Rezept — это и рецепт блюда, и рецепт от врача. Квитанция — die Quittung."))
P.append(evening(d, "ТЫ ПУТАЕШЬ ЭТО", "wenn или als?", "оба = «когда»", "Als ich Kind war, …", "Wenn ich Zeit habe, …", "als — один раз в прошлом",
 "🇩🇪 <b>wenn или als?</b> 🤯\n\nОба переводятся «когда», но правило простое 👇\n\n"
 "✅ <b>als</b> — один раз в прошлом (или один период)\n<i>Als ich Kind war, wohnte ich auf dem Land.</i> — Когда я был ребёнком, я жил в деревне.\n<i>Als ich nach Berlin kam, regnete es.</i> — Когда я приехал в Берлин, шёл дождь.\n\n"
 "✅ <b>wenn</b> — в настоящем, будущем и для повторяющихся событий в прошлом\n<i>Wenn ich Zeit habe, lese ich.</i> — Когда у меня есть время, я читаю.\n<i>Immer wenn ich sie sah, lächelte sie.</i> — Каждый раз, когда я её видел, она улыбалась.\n\n"
 "💡 <b>Лайфхак:</b> один раз в прошлом → als. Всё остальное → wenn.\nПосле обоих глагол уходит в конец.\n\n"
 "🧠 Проверь себя: ___ ich in Berlin war, habe ich Anna getroffen.\nОтвет: <tg-spoiler>Als</tg-spoiler>" + FOOT))

# ---------- Вт 27.10 ----------
d = "2026-10-27"
P.append(wort(d, "die Schnapsidee", "безумная идея", "Das war eine Schnapsidee!", "Это была безумная идея!",
 "<b>die Schnapsidee</b> — безумная, дурацкая идея 🥃🤪📌\nДословно: «идея после шнапса» — такая, что трезвому в голову не придёт.\n\n<i>Das war eine Schnapsidee!</i>\n— Это была безумная идея!\n\n"
 "💡 <b>Использование</b>\nРазговорное слово. Часто про спонтанные планы, которые звучали круто только в моменте.\n\n"
 "<b>Примеры:</b>\n• eine Schnapsidee haben — придумать безумную идею\n• Was für eine Schnapsidee! — ну и бредовая идея!\n• Die Idee ist gar nicht so schlecht. — идея вовсе не такая уж плохая\n\n😅 Какая твоя самая большая Schnapsidee?"))
P.append(quiz(d, "📚 Какой артикль у слова «Problem»?", ["der", "die", "das"], 2,
 "das Problem. Многие слова на -em греческого происхождения среднего рода: das Problem, das System."))
P.append(evening(d, "МИНИ-ДИАЛОГ", "In der Apotheke", "в аптеке", "Haben Sie etwas dagegen?", "У вас есть что-нибудь от этого?", "Сохрани, пригодится",
 "💊 <b>Мини-диалог: In der Apotheke</b> (в аптеке)\n\n"
 "👩‍⚕️ <i>Guten Tag! Was kann ich für Sie tun?</i>\n— Добрый день! Чем могу помочь?\n\n"
 "🙋 <i>Ich habe Kopfschmerzen. Haben Sie etwas dagegen?</i>\n— У меня болит голова. У вас есть что-нибудь от этого?\n\n"
 "👩‍⚕️ <i>Ja, da kann ich Ihnen etwas empfehlen.</i>\n— Да, могу вам кое-что посоветовать.\n\n"
 "🙋 <i>Brauche ich dafür ein Rezept?</i>\n— Мне нужен для этого рецепт?\n\n"
 "👩‍⚕️ <i>Nein, das ist rezeptfrei.</i>\n— Нет, это без рецепта.\n\n"
 "🙋 <i>Gut, dann nehme ich das. Danke!</i>\n— Хорошо, тогда возьму. Спасибо!\n\n"
 "👩‍⚕️ <i>Gern. Gute Besserung!</i>\n— Пожалуйста. Выздоравливайте!\n\n"
 "💡 <b>Запомни:</b> Haben Sie etwas gegen…? • rezeptfrei • Gute Besserung!" + FOOT2))

# ---------- Ср 28.10 ----------
d = "2026-10-28"
P.append(wort(d, "der Drahtesel", "велосипед (в шутку)", "Ich fahre mit meinem Drahtesel.", "Я еду на своём велике.",
 "<b>der Drahtesel</b> — велосипед (шутливо) 🚲😄📌\nДословно: «проволочный осёл».\n\n<i>Ich fahre mit meinem Drahtesel zur Arbeit.</i>\n— Я езжу на работу на своём велике.\n\n"
 "💡 <b>Использование</b>\nРазговорное и немного старомодное, звучит с юмором. Обычное слово — das Fahrrad или das Rad.\n\n"
 "<b>Примеры:</b>\n• das Fahrrad / das Rad — велосипед\n• Rad fahren — кататься на велосипеде\n• mit dem Rad — на велосипеде\n\n🚲 Ездишь на Drahtesel или на автобусе?"))
P.append(quiz(d, "📞 Как правильно: «Я позвоню тебе завтра»?", ["Ich anrufe dich morgen.", "Ich rufe dich morgen an.", "Ich rufe dich morgen auf."], 1,
 "anrufen — отделяемый глагол: Ich rufe dich morgen an. А aufrufen — вызывать (например, по имени)."))
P.append(evening(d, "ТАБЛИЧКИ В ГЕРМАНИИ", "Nur Barzahlung", "только наличные", "Geöffnet / Geschlossen", "открыто / закрыто", "Сохрани, пригодится",
 "🚧 <b>6 надписей, которые встречаются в магазинах и на улице</b>\n\n"
 "💶 <b>Nur Barzahlung</b> — только наличные\n🟢 <b>Geöffnet / Geschlossen</b> — открыто / закрыто\n🚪 <b>Notausgang</b> — запасный выход\n"
 "🔒 <b>Zutritt nur für Personal</b> — вход только для персонала\n🙅 <b>Bitte nicht berühren</b> — пожалуйста, не трогайте\n📦 <b>Ausverkauft</b> — распродано\n\n"
 "💡 <b>Фишка:</b> в Германии до сих пор встречаются места, где берут только наличные — табличка Nur Barzahlung спасает от неловкости на кассе 😅\n\n"
 "🧠 Проверь себя: что значит «Ausverkauft»?\nОтвет: <tg-spoiler>распродано</tg-spoiler>" + FOOT2))

# ---------- Чт 29.10 ----------
d = "2026-10-29"
P.append(wort(d, "Na?", "ну что? как дела?", "Na, alles klar?", "Ну что, всё в порядке?",
 "<b>Na?</b> — ну что? / как дела? 👋😏📌\n\n<i>Na, alles klar?</i>\n— Ну что, всё в порядке?\n\n"
 "💡 <b>Использование</b>\nКороткое разговорное приветствие для друзей и знакомых. Ответить можно тоже коротко: «Na?» или «Gut, und dir?». С начальником и в официальных ситуациях лучше не использовать.\n\n"
 "<b>Примеры:</b>\n• Na, wie geht's? — ну, как дела?\n• Na und? — ну и что?\n• Na ja… — ну-у… (сомнение)\n\n😉 Na, учишь немецкий сегодня?"))
P.append(quiz(d, "🏫 Ложный друг: что значит «das Gymnasium»?", ["Спортзал", "Гимназия (школа)", "Бассейн"], 1,
 "das Gymnasium — гимназия, школа с выходом на аттестат. Спортзал — die Turnhalle или das Fitnessstudio."))
P.append(evening(d, "A ИЛИ B?", "lernen или studieren?", "учить или учиться в вузе", "Ich lerne Deutsch.", "Ich studiere Medizin.", "studieren — в университете",
 "🇩🇪 <b>lernen или studieren?</b> 🎓\n\nОба про учёбу, но разница большая 👇\n\n"
 "✅ <b>lernen</b> — учить что-то, заниматься, готовиться\n<i>Ich lerne Deutsch.</i> — Я учу немецкий.\n<i>Ich lerne für die Prüfung.</i> — Я готовлюсь к экзамену.\n\n"
 "✅ <b>studieren</b> — учиться в университете, изучать специальность\n<i>Ich studiere Medizin.</i> — Я учусь на медицинском.\n<i>Sie studiert in München.</i> — Она учится (в вузе) в Мюнхене.\n\n"
 "⚠️ «Ich studiere Deutsch» тоже возможно — но это значит «изучаю германистику в университете», а не «учу язык на курсах».\n\n"
 "🧠 Проверь себя: Ich ___ Informatik an der Uni.\nОтвет: <tg-spoiler>studiere</tg-spoiler>" + FOOT))

# ---------- Пт 30.10 ----------
d = "2026-10-30"
P.append(wort(d, "der Kater", "похмелье (и кот)", "Ich habe heute einen Kater.", "У меня сегодня похмелье.",
 "<b>der Kater</b> — похмелье 🤕 (а ещё кот 🐈)📌\n\n<i>Ich habe heute einen Kater.</i>\n— У меня сегодня похмелье.\n\n"
 "💡 <b>Использование</b>\nКонтекст подскажет, о чём речь: о коте или о тяжёлом утре после вечеринки 😅 Помнишь Muskelkater из понедельника? Тоже «кот»!\n\n"
 "<b>Примеры:</b>\n• einen Kater haben — страдать от похмелья\n• der Kater / die Katze — кот / кошка\n• der Muskelkater — боль в мышцах после спорта\n\n🍻 Пятница! Главное — без Kater в субботу 😉"))
P.append(quiz(d, "🛒 Как правильно: «Я купил хлеб»?", ["Ich bin Brot gekauft.", "Ich habe Brot gekauft.", "Ich habe Brot gekaufen."], 1,
 "kaufen — с haben и правильным причастием gekauft: Ich habe Brot gekauft."))
P.append(evening(d, "СЛЕНГ", "Läuft bei dir!", "у тебя всё круто!", "Was geht?", "Чё как? / Как дела?", "разговорное, с друзьями",
 "😎 <b>Сленг на пятницу, часть 2</b>\n\nПродолжаем живой немецкий 👇\n\n"
 "🔥 <b>Läuft bei dir!</b> — у тебя всё круто! / тебе везёт!\n<i>Neuer Job, neue Wohnung — läuft bei dir!</i> — Новая работа, новая квартира — у тебя всё на мази!\n\n"
 "👋 <b>Was geht?</b> — чё как? / как дела?\n<i>Hey, was geht?</i> — Привет, как сам?\n\n"
 "😮‍💨 <b>fix und fertig sein</b> — быть без сил\n<i>Nach der Woche bin ich fix und fertig.</i> — После такой недели я выжат.\n\n"
 "🤷 <b>Na und?</b> — ну и что?\n<i>Es regnet. — Na und?</i> — Идёт дождь. — Ну и что?\n\n"
 "⚠️ Всё это — разговорный стиль: с друзьями отлично, в официальных ситуациях лучше без него 😉" + FOOT2))

# ---------- Сб 31.10 ----------
d = "2026-10-31"
P.append(wort(d, "gruselig", "жуткий, страшный", "Der Film war richtig gruselig.", "Фильм был по-настоящему жутким.",
 "<b>gruselig</b> — жуткий, страшный 👻🎃📌\n\n<i>Der Film war richtig gruselig.</i>\n— Фильм был по-настоящему жутким.\n\n"
 "💡 <b>Использование</b>\nСегодня Halloween — идеальный день для этого слова. А ещё 31 октября — Reformationstag, в части федеральных земель Германии это выходной.\n\n"
 "<b>Примеры:</b>\n• Das ist ja gruselig! — вот это жуть!\n• der Gruselfilm — фильм ужасов\n• sich gruseln — бояться, испытывать жуть\n\n🎃 Празднуешь Halloween?"))
P.append(quiz(d, "👻 Как сказать по-немецки «Мне страшно» / «Я боюсь»?", ["Ich bin Angst.", "Ich habe Angst.", "Ich mache Angst."], 1,
 "Angst haben — бояться: Ich habe Angst. А «Ich mache (dir) Angst» — я (тебя) пугаю."))
P.append(evening(d, "5 ФРАЗ", "Herbstwetter", "осенняя погода", "Es regnet in Strömen.", "Льёт как из ведра.", "Сохрани, пригодится",
 "🍂 <b>5 фраз про осеннюю погоду</b>\n\n"
 "1️⃣ <i>Es regnet in Strömen.</i> — Льёт как из ведра.\n2️⃣ <i>Es ist neblig.</i> — Туманно.\n3️⃣ <i>Was für ein Schmuddelwetter!</i> — Ну и мерзкая погода!\n"
 "4️⃣ <i>Zieh dich warm an!</i> — Оденься потеплее!\n5️⃣ <i>Die Uhr wird umgestellt.</i> — Часы переводят.\n\n"
 "💡 <b>Фишка:</b> на прошлой неделе Германия перешла на зимнее время — часы перевели на час назад.\n\n"
 "🧠 Проверь себя: как сказать «Оденься потеплее!»?\nОтвет: <tg-spoiler>Zieh dich warm an!</tg-spoiler>" + FOOT2))

# ---------- Вс 01.11 ----------
d = "2026-11-01"
P.append(wort(d, "ausschlafen", "выспаться", "Am Sonntag schlafe ich aus.", "В воскресенье я высыпаюсь.",
 "<b>ausschlafen</b> — выспаться, поспать вдоволь 😴☀️📌\n\n<i>Am Sonntag schlafe ich aus.</i>\n— В воскресенье я высыпаюсь.\n\n"
 "💡 <b>Использование</b>\nОтделяемый глагол: приставка aus уходит в конец. Не путай с verschlafen — проспать!\n\n"
 "<b>Примеры:</b>\n• Ich habe gut ausgeschlafen. — Я хорошо выспался.\n• Endlich ausschlafen! — наконец-то можно выспаться!\n• verschlafen — проспать (опоздать)\n\n☕ Удалось сегодня ausschlafen?"))
P.append(quiz(d, "🚌 Вставь правильно: «Ich warte ___ den Bus.»", ["auf", "für", "an"], 0,
 "warten auf + винительный падеж: Ich warte auf den Bus. «für» здесь не подходит."))
P.append(evening(d, "НЕДЕЛЬНЫЙ ТЕСТ", "5 вопросов", "сколько наберёшь?", "Ответы под спойлером", "Проверь себя по итогам недели", "Сохрани и повтори",
 "🧠 <b>Недельный тест: 5 вопросов</b>\n\nВсё, что было в канале на этой неделе. Ответь в голове, потом открой спойлер 👇\n\n"
 "1️⃣ Как одним словом сказать «боль в мышцах после спорта»?\n<tg-spoiler>der Muskelkater</tg-spoiler>\n\n"
 "2️⃣ Какой артикль у слова Problem?\n<tg-spoiler>das</tg-spoiler>\n\n"
 "3️⃣ «Я позвоню тебе завтра»: Ich ___ dich morgen ___.\n<tg-spoiler>rufe … an</tg-spoiler>\n\n"
 "4️⃣ Что значит das Gymnasium?\n<tg-spoiler>гимназия (школа), а не спортзал</tg-spoiler>\n\n"
 "5️⃣ ___ ich Kind war, wohnte ich auf dem Land. (als или wenn?)\n<tg-spoiler>Als — один раз/период в прошлом</tg-spoiler>\n\n"
 "🏆 5 из 5 — ты огонь! 3–4 — отлично! Меньше 3 — пролистай посты этой недели ещё раз 😉\n\nСохрани и повтори 📌\n<b>Lingofy Deutsch</b>"))

root = os.path.join(os.path.dirname(__file__), "..")
qp = os.path.join(root, "queue.json")
queue = json.load(open(qp, encoding="utf-8"))
ids = {p["id"] for p in queue}
queue += [p for p in P if p["id"] not in ids]
json.dump(queue, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(P), "posts; queue size", len(queue))
for p in P:
    if p["type"] == "photo":
        assert len(p["caption"]) <= 1024, (p["id"], len(p["caption"]))
    else:
        assert len(p["explanation"]) <= 200 and len(p["question"]) <= 300, p["id"]

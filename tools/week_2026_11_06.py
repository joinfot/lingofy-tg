"""Собирает посты 06.11–15.11.2026 и дописывает их в queue.json.

Очередь кончилась 1 ноября, поэтому канал молчал с 2-го. Здесь десять дней
подряд по три поста: утром слово дня, днём квиз, вечером разбор. Два
воскресенья закрываются недельным тестом.

Темы не повторяют ни прошлую неделю, ни сегодняшние ролики.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from card import card

TZ = "+01:00"
FOOT = "\n\nСохрани, чтобы не забыть 📌\n<b>Lingofy Deutsch</b>"
FOOT2 = "\n\nСохрани, пригодится 📌\n<b>Lingofy Deutsch</b>"
WDT = "WORT DES TAGES"


def wort(day, word, ru, ex, exru, cap_body):
    return dict(id=f"{day}-m", at=f"{day}T08:45:00{TZ}", type="photo",
                photo=card(tag=WDT, de=word, ru=ru, ex=ex, exru=exru,
                           note="Сохрани, чтобы не забыть"),
                caption=f"🇩🇪 <b>Wort des Tages</b>\n\n{cap_body}{FOOT}")


def quiz(day, q, options, correct, expl):
    return dict(id=f"{day}-q", at=f"{day}T13:00:00{TZ}", type="quiz",
                question=q, options=options, correct=correct, explanation=expl)


def evening(day, tag, de, ru, ex, exru, note, cap):
    return dict(id=f"{day}-e", at=f"{day}T19:00:00{TZ}", type="photo",
                photo=card(tag=tag, de=de, ru=ru, ex=ex, exru=exru, note=note),
                cap_len_check=True, caption=cap)


P = []

# ---------- Пт 06.11 ----------
d = "2026-11-06"
P.append(wort(d, "die Gemütlichkeit", "уют, тёплая атмосфера",
              "Hier herrscht eine schöne Gemütlichkeit.",
              "Здесь по-настоящему уютно.",
 "<b>die Gemütlichkeit</b> — уют, тёплая атмосфера 🕯🛋📌\n\n"
 "<i>Hier herrscht eine schöne Gemütlichkeit.</i>\n— Здесь по-настоящему уютно.\n\n"
 "💡 <b>Использование</b>\nЭто не про мебель, а про ощущение: тепло, спокойно, "
 "никто никуда не спешит. Слово часто называют непереводимым — ближе всего "
 "русское «уют», но немецкое шире: оно и про компанию, и про настроение.\n\n"
 "<b>Примеры:</b>\n• gemütlich — уютный, неспешный\n"
 "• Mach es dir gemütlich! — располагайся, чувствуй себя как дома\n"
 "• ein gemütlicher Abend — тихий вечер в хорошей компании\n\n"
 "🕯 Что для тебя Gemütlichkeit?"))
P.append(quiz(d, "🎵 Вставь предлог: «Ich interessiere mich ___ Musik.»",
              ["für", "an", "auf"], 0,
 "sich interessieren идёт только с für: Ich interessiere mich für Musik. "
 "Предлог тут часть глагола, по смыслу его не подобрать."))
P.append(evening(d, "ТЫ ПУТАЕШЬ ЭТО", "kennen или wissen?", "оба = «знать»",
                 "Ich kenne ihn.", "Ich weiß, wo er wohnt.",
                 "kennen — про знакомство",
 "🇩🇪 <b>kennen или wissen?</b> 🤔\n\nОба переводятся «знать», но делят работу "
 "чётко 👇\n\n"
 "✅ <b>kennen</b> — быть знакомым с кем-то или чем-то. После него идёт "
 "существительное.\n<i>Ich kenne ihn seit zehn Jahren.</i> — Я знаю его "
 "десять лет.\n<i>Kennst du dieses Lied?</i> — Знаешь эту песню?\n\n"
 "✅ <b>wissen</b> — знать факт. После него обычно придаточное: dass, wo, "
 "wann, warum.\n<i>Ich weiß, dass er kommt.</i> — Я знаю, что он придёт.\n"
 "<i>Weißt du, wo der Bahnhof ist?</i> — Знаешь, где вокзал?\n\n"
 "💡 <b>Лайфхак:</b> можешь подставить «знаком с» — значит kennen. "
 "Можешь подставить «в курсе, что» — значит wissen.\n\n"
 "🧠 Проверь себя: ___ du, wie spät es ist?\nОтвет: <tg-spoiler>Weißt</tg-spoiler>"
 + FOOT))

# ---------- Сб 07.11 ----------
d = "2026-11-07"
P.append(wort(d, "der Ohrwurm", "песня, застрявшая в голове",
              "Dieses Lied ist ein echter Ohrwurm.",
              "Эта песня намертво застряла в голове.",
 "<b>der Ohrwurm</b> — песня, которая застряла в голове 🎧🔁📌\n"
 "Дословно: «ушной червь» 🐛\n\n"
 "<i>Dieses Lied ist ein echter Ohrwurm.</i>\n— Эта песня намертво застряла "
 "в голове.\n\n"
 "💡 <b>Использование</b>\nПо-русски нужна целая фраза, по-немецки — одно "
 "слово. Так же устроены многие немецкие находки: длинное понятие "
 "упаковывают в одно существительное.\n\n"
 "<b>Примеры:</b>\n• einen Ohrwurm haben — не мочь выкинуть песню из головы\n"
 "• Der Ohrwurm geht nicht weg. — Песня не отпускает.\n"
 "• Achtung, Ohrwurm-Gefahr! — Осторожно, привяжется!\n\n"
 "🎧 Какая песня у тебя сейчас Ohrwurm?"))
P.append(quiz(d, "🕖 Сколько времени, если говорят «Viertel vor acht»?",
              ["7:45", "8:15", "7:15"], 0,
 "vor — «до»: четверть до восьми, то есть 7:45. Viertel nach acht было бы 8:15."))
P.append(evening(d, "ЖИЗНЬ В ГЕРМАНИИ", "Sonntag", "всё закрыто",
                 "Die Geschäfte sind sonntags zu.",
                 "По воскресеньям магазины закрыты.", "Планируй покупки заранее",
 "🇩🇪 <b>Воскресенье в Германии: что закрыто</b> 🛒\n\n"
 "Главное правило недели для новичка: в воскресенье обычные магазины не "
 "работают. Это закреплено законом о часах торговли, детали различаются по "
 "землям.\n\n"
 "🔒 <b>Закрыто:</b> супермаркеты, Drogerie, мебельные, одежда, "
 "строительные.\n\n"
 "🔓 <b>Обычно открыто:</b>\n• магазины на вокзалах и в аэропортах\n"
 "• заправки (Tankstelle) — там же базовый набор продуктов\n"
 "• пекарни — часто несколько часов утром\n"
 "• аптека по дежурству (Notdienst) — список висит на двери любой аптеки\n"
 "• в Берлине ещё Spätis — маленькие лавки допоздна\n\n"
 "📅 Пару раз в год бывают verkaufsoffene Sonntage — воскресенья, когда "
 "магазины открыты. Даты объявляет город.\n\n"
 "💡 Поэтому суббота в Германии — день больших закупок. Вечером в субботу "
 "в супермаркете очередь, и это нормально." + FOOT2))

# ---------- Вс 08.11 ----------
d = "2026-11-08"
P.append(wort(d, "das Fernweh", "тяга к дальним странам",
              "Ich habe schon wieder Fernweh.", "Меня снова тянет уехать.",
 "<b>das Fernweh</b> — тоска по далёким местам ✈️🗺📌\n"
 "Противоположность слову Heimweh — тоска по дому 🏡\n\n"
 "<i>Ich habe schon wieder Fernweh.</i>\n— Меня снова тянет уехать.\n\n"
 "💡 <b>Использование</b>\nfern — далёкий, das Weh — боль. Получается «боль "
 "по далёкому». Немцы собирают такие слова из двух корней, и смысл читается "
 "насквозь.\n\n"
 "<b>Примеры:</b>\n• Fernweh bekommen — затосковать по дороге\n"
 "• das Heimweh — тоска по дому\n"
 "• die Reiselust — охота путешествовать\n\n"
 "🗺 Куда тянет тебя?"))
P.append(quiz(d, "🤨 Ложный друг: что значит немецкое «bekommen»?",
              ["получать", "становиться", "приходить"], 0,
 "bekommen — получать: Ich bekomme ein Paket. «Становиться» — werden. "
 "Английское become сбивает с толку именно здесь."))
P.append(evening(d, "НЕДЕЛЬНЫЙ ТЕСТ", "5 вопросов", "сколько наберёшь?",
                 "Ответы под спойлером", "Проверь себя по итогам недели",
                 "Сохрани и повтори",
 "🧠 <b>Недельный тест: 5 вопросов</b>\n\nПо темам этой недели. Ответь в "
 "голове, потом открой спойлер 👇\n\n"
 "1️⃣ Как одним словом сказать «песня застряла в голове»?\n"
 "<tg-spoiler>der Ohrwurm</tg-spoiler>\n\n"
 "2️⃣ kennen или wissen: ___ du, wo der Bahnhof ist?\n"
 "<tg-spoiler>Weißt — дальше идёт придаточное</tg-spoiler>\n\n"
 "3️⃣ Viertel vor acht — это сколько?\n<tg-spoiler>7:45</tg-spoiler>\n\n"
 "4️⃣ Что значит bekommen?\n<tg-spoiler>получать, а не «становиться»</tg-spoiler>\n\n"
 "5️⃣ Ich interessiere mich ___ Musik.\n<tg-spoiler>für</tg-spoiler>\n\n"
 "🏆 5 из 5 — ты огонь! 3–4 — отлично! Меньше 3 — пролистай посты недели "
 "ещё раз 😉\n\nСохрани и повтори 📌\n<b>Lingofy Deutsch</b>"))

# ---------- Пн 09.11 ----------
d = "2026-11-09"
P.append(wort(d, "verschlimmbessern", "сделать хуже, улучшая",
              "Ich wollte helfen und habe es verschlimmbessert.",
              "Хотел помочь, а сделал только хуже.",
 "<b>verschlimmbessern</b> — сделать хуже, пытаясь улучшить 🔧😬📌\n"
 "Склеено из verschlimmern (ухудшить) и verbessern (улучшить)\n\n"
 "<i>Ich wollte helfen und habe es verschlimmbessert.</i>\n"
 "— Хотел помочь, а сделал только хуже.\n\n"
 "💡 <b>Использование</b>\nСлово шутливое, но совершенно обычное в речи. "
 "Отлично ложится на ремонт, правки в тексте и попытки починить wifi.\n\n"
 "<b>Примеры:</b>\n• Das hast du jetzt verschlimmbessert. — Ты сделал только "
 "хуже.\n• die Verschlimmbesserung — такое «улучшение»\n"
 "• verbessern — улучшать (нормальный глагол)\n\n"
 "🔧 Было такое?"))
P.append(quiz(d, "🚆 Вставь предлог: «Ich bin ___ Berlin gefahren.»",
              ["nach", "in", "zu"], 0,
 "С городами и странами без артикля — nach: nach Berlin, nach Deutschland. "
 "«in die Schweiz» — исключение, там артикль есть."))
P.append(evening(d, "ТЫ ПУТАЕШЬ ЭТО", "legen или liegen?", "класть или лежать",
                 "Ich lege das Buch auf den Tisch.",
                 "Das Buch liegt auf dem Tisch.", "Действие → Akkusativ",
 "🇩🇪 <b>legen или liegen? stellen или stehen?</b> 📚\n\n"
 "Пары, на которых спотыкаются даже на B1. Разница в одном: кто-то делает "
 "действие или предмет просто находится 👇\n\n"
 "✅ <b>legen / stellen</b> — кто-то кладёт или ставит. Есть движение, "
 "значит Akkusativ.\n<i>Ich lege das Buch auf <b>den</b> Tisch.</i> — Я кладу "
 "книгу на стол.\n<i>Ich stelle die Flasche in <b>den</b> Kühlschrank.</i> — "
 "Я ставлю бутылку в холодильник.\n\n"
 "✅ <b>liegen / stehen</b> — предмет просто там. Движения нет, значит "
 "Dativ.\n<i>Das Buch liegt auf <b>dem</b> Tisch.</i> — Книга лежит на столе.\n"
 "<i>Die Flasche steht in <b>dem</b> Kühlschrank.</i> — Бутылка стоит в "
 "холодильнике.\n\n"
 "💡 <b>Лайфхак:</b> спроси себя «куда?» или «где?». Куда — Akkusativ, "
 "где — Dativ.\n\n"
 "🧠 Проверь: Der Schlüssel liegt auf ___ Tisch.\n"
 "Ответ: <tg-spoiler>dem</tg-spoiler>" + FOOT))

# ---------- Вт 10.11 ----------
d = "2026-11-10"
P.append(wort(d, "der innere Schweinehund", "внутренняя лень",
              "Ich muss meinen inneren Schweinehund überwinden.",
              "Мне надо побороть свою лень.",
 "<b>der innere Schweinehund</b> — внутренняя лень 🐷🛋📌\n"
 "Дословно: «внутренняя свинья-собака»\n\n"
 "<i>Ich muss meinen inneren Schweinehund überwinden.</i>\n"
 "— Мне надо побороть свою лень.\n\n"
 "💡 <b>Использование</b>\nТот самый голос, который предлагает остаться дома. "
 "Слово почти всегда идёт с глаголом überwinden — преодолеть.\n\n"
 "<b>Примеры:</b>\n• den inneren Schweinehund besiegen — победить свою лень\n"
 "• Mein Schweinehund war heute stärker. — Сегодня лень победила.\n"
 "• sich aufraffen — всё-таки собраться и сделать\n\n"
 "🐷 Кто сегодня победил?"))
P.append(quiz(d, "🚌 Множественное число от «der Bus»?",
              ["die Busse", "die Büsse", "die Busen"], 0,
 "der Bus — die Busse. Удвоенная s пишется, потому что гласная перед ней "
 "короткая."))
P.append(evening(d, "КАК СКАЗАТЬ ВЕЖЛИВО", "Könnten Sie …?", "самая мягкая форма",
                 "Könnten Sie mir helfen?", "Вы не могли бы мне помочь?",
                 "Konjunktiv смягчает просьбу",
 "🇩🇪 <b>Как попросить так, чтобы звучало вежливо</b> 🙏\n\n"
 "Разница между «дай» и «не мог бы ты» в немецком делается одной формой "
 "глагола 👇\n\n"
 "🔸 <b>Прямо:</b>\n<i>Hilf mir.</i> — Помоги мне.\n"
 "<i>Ich will einen Kaffee.</i> — Я хочу кофе.\n\n"
 "🔹 <b>Вежливо:</b>\n<i>Könnten Sie mir helfen?</i> — Вы не могли бы мне "
 "помочь?\n<i>Ich hätte gern einen Kaffee.</i> — Я хотел бы кофе.\n"
 "<i>Würden Sie bitte das Fenster schließen?</i> — Не закроете окно?\n\n"
 "💡 <b>Три заготовки на все случаи:</b>\n"
 "• <b>Könnten Sie …?</b> — просьба о действии\n"
 "• <b>Ich hätte gern …</b> — заказ в кафе, магазине, у стойки\n"
 "• <b>Wäre es möglich, …?</b> — что-то посложнее, в учреждении\n\n"
 "Это Konjunktiv II. Учить его целиком не обязательно — эти три формы "
 "закрывают почти всё.\n\n"
 "🧠 Как вежливо попросить счёт?\n"
 "<tg-spoiler>Könnten wir bitte zahlen?</tg-spoiler>" + FOOT))

# ---------- Ср 11.11 ----------
d = "2026-11-11"
P.append(wort(d, "Alaaf und Helau", "карнавальные возгласы",
              "Am 11.11. um 11:11 Uhr geht es los.",
              "11 ноября в 11:11 всё начинается.",
 "<b>Alaaf</b> и <b>Helau</b> — карнавальные возгласы 🎭🎺📌\n\n"
 "<i>Am 11.11. um 11:11 Uhr geht es los.</i>\n— 11 ноября в 11:11 всё "
 "начинается.\n\n"
 "💡 <b>Использование</b>\nСегодня в 11:11 открывается карнавальный сезон — "
 "его называют Session. Возглас зависит от города: в Кёльне кричат "
 "<b>Kölle Alaaf</b>, в Дюссельдорфе и Майнце — <b>Helau</b>. Перепутать "
 "местами — старая шутка между городами.\n\n"
 "<b>Примеры:</b>\n• die Session — карнавальный сезон\n"
 "• der Karneval, die Fastnacht, der Fasching — одно и то же в разных "
 "регионах\n• Rosenmontag — главный день с шествиями, уже в феврале\n\n"
 "🎭 Alaaf или Helau?"))
P.append(quiz(d, "🎭 Как кричат на карнавале в Кёльне?",
              ["Alaaf", "Helau", "Hoppla"], 0,
 "В Кёльне — Kölle Alaaf. Helau кричат в Дюссельдорфе и Майнце. "
 "Hoppla к карнавалу отношения не имеет."))
P.append(evening(d, "ЖИЗНЬ В ГЕРМАНИИ", "die Session", "карнавальный сезон",
                 "Am 11.11. beginnt die Session.",
                 "11 ноября начинается сезон.", "Главное — в феврале",
 "🇩🇪 <b>Карнавал: что сегодня началось</b> 🎭\n\n"
 "Сегодня в 11:11 открылся карнавальный сезон. Дальше до февраля затишье, "
 "а самое громкое впереди 👇\n\n"
 "📍 <b>Где это главное событие года:</b> Кёльн, Дюссельдорф, Майнц и "
 "вообще Рейнская область. В Баварии это Fasching, на юго-западе — "
 "Fastnacht. В Берлине и на севере почти незаметно.\n\n"
 "📅 <b>Ключевые дни (февраль 2027):</b>\n"
 "• <b>Weiberfastnacht</b> — четверг, женский день карнавала; по традиции "
 "отрезают мужчинам галстуки\n"
 "• <b>Rosenmontag</b> — понедельник, большие шествия\n"
 "• <b>Aschermittwoch</b> — среда, всё заканчивается\n\n"
 "🗣 <b>Слова:</b>\n• der Umzug — шествие\n• die Kamelle — конфеты, которые "
 "бросают с платформ\n• das Kostüm — костюм\n• die Bützchen — шуточные "
 "поцелуи в щёку\n\n"
 "💡 В эти дни во многих конторах Рейнской области сокращённый день или "
 "выходной — но это решает работодатель, законом не закреплено." + FOOT2))

# ---------- Чт 12.11 ----------
d = "2026-11-12"
P.append(wort(d, "die Schadenfreude", "злорадство",
              "Ein bisschen Schadenfreude war dabei.",
              "Немного злорадства всё-таки было.",
 "<b>die Schadenfreude</b> — радость от чужой неудачи 😈😅📌\n"
 "der Schaden — вред, die Freude — радость\n\n"
 "<i>Ein bisschen Schadenfreude war dabei.</i>\n— Немного злорадства "
 "всё-таки было.\n\n"
 "💡 <b>Использование</b>\nСлово ушло из немецкого в другие языки как есть — "
 "в английском его тоже пишут Schadenfreude. Своего слова там не нашлось.\n\n"
 "<b>Примеры:</b>\n• schadenfroh — злорадный\n"
 "• Schadenfreude ist die schönste Freude. — поговорка: злорадство — самая "
 "сладкая радость\n• sich freuen über — радоваться чему-то (нейтрально)\n\n"
 "😅 Признавайся, бывает?"))
P.append(quiz(d, "💼 Что значит «Feierabend machen»?",
              ["закончить рабочий день", "устроить вечеринку",
               "взять отгул"], 0,
 "Feierabend — конец рабочего дня. «Ich mache Feierabend» значит «я "
 "заканчиваю работу», а не «я праздную»."))
P.append(evening(d, "ТЫ ПУТАЕШЬ ЭТО", "noch или schon?", "ещё или уже",
                 "Ich bin noch hier.", "Bist du schon da?",
                 "erst — только, позже чем ждали",
 "🇩🇪 <b>schon, noch, erst — три слова про время</b> ⏳\n\n"
 "Они не синонимы, и дело не в оттенке, а в том, как ты смотришь на срок 👇\n\n"
 "✅ <b>schon</b> — уже, раньше, чем ожидалось\n<i>Bist du schon da?</i> — "
 "Ты уже там? (думал, будешь позже)\n\n"
 "✅ <b>noch</b> — ещё, пока не закончилось\n<i>Ich bin noch im Büro.</i> — "
 "Я ещё в офисе.\n<i>noch nicht</i> — ещё не\n<i>nicht mehr</i> — уже не\n\n"
 "✅ <b>erst</b> — только, позже чем ожидалось или не больше чем\n"
 "<i>Ich komme erst um acht.</i> — Я приду только в восемь.\n"
 "<i>Ich lerne erst ein Jahr Deutsch.</i> — Я учу немецкий всего год.\n\n"
 "💡 <b>Лайфхак:</b> «Es ist ___ neun Uhr». Удивлён, что уже девять — schon. "
 "Жалеешь, что всего девять — erst.\n\n"
 "🧠 Проверь: Ich wohne ___ zwei Monate hier, alles ist neu.\n"
 "Ответ: <tg-spoiler>erst</tg-spoiler>" + FOOT))

# ---------- Пт 13.11 ----------
d = "2026-11-13"
P.append(wort(d, "das Kopfkino", "кино в голове",
              "Bei dem Wort hatte ich sofort Kopfkino.",
              "От этого слова у меня сразу включилось кино в голове.",
 "<b>das Kopfkino</b> — кино в голове 🎬🧠📌\n"
 "der Kopf — голова, das Kino — кино\n\n"
 "<i>Bei dem Wort hatte ich sofort Kopfkino.</i>\n— От этого слова у меня "
 "сразу включилось кино в голове.\n\n"
 "💡 <b>Использование</b>\nКогда воображение само достраивает картинку: по "
 "рассказу, по фразе, по звуку за стеной. Разговорное, в учебниках не "
 "встретится.\n\n"
 "<b>Примеры:</b>\n• Kopfkino haben — живо представлять себе что-то\n"
 "• Sofort Kopfkino! — сразу картинка перед глазами!\n"
 "• sich etwas vorstellen — представлять себе (нейтрально)\n\n"
 "🎬 Что включает Kopfkino у тебя?"))
P.append(quiz(d, "🕷 Вставь предлог: «Ich habe Angst ___ Spinnen.»",
              ["vor", "von", "für"], 0,
 "Angst haben идёт с vor + Dativ: Angst vor Spinnen, Angst vor dem Hund. "
 "Предлог тут часть выражения."))
P.append(evening(d, "ТРАДИЦИИ", "Daumen drücken", "пожелать удачи",
                 "Ich drücke dir die Daumen!", "Держу за тебя кулачки!",
                 "Пальцы не скрещивают",
 "🇩🇪 <b>Как пожелать удачи по-немецки</b> 🤞\n\n"
 "Привычный жест со скрещёнными пальцами в Германии не в ходу. Вместо "
 "этого зажимают большой палец в кулак 👇\n\n"
 "✅ <b>Ich drücke dir die Daumen!</b> — Держу за тебя кулачки!\n"
 "Дословно «жму большие пальцы». Так говорят перед экзаменом, "
 "собеседованием, приёмом у врача.\n\n"
 "✅ <b>Toi, toi, toi!</b> — тоже пожелание удачи. Пришло из театра, "
 "где напрямую желать удачи считалось дурной приметой.\n\n"
 "✅ <b>Viel Erfolg!</b> — нейтральное «успехов», годится и в письме.\n"
 "✅ <b>Viel Glück!</b> — удачи, когда многое зависит от случая.\n\n"
 "💡 Разница тонкая: <b>Erfolg</b> — там, где всё зависит от тебя "
 "(экзамен, проект). <b>Glück</b> — там, где от везения (лотерея, "
 "погода в отпуске).\n\n"
 "🤞 Кому сегодня надо Daumen drücken?" + FOOT2))

# ---------- Сб 14.11 ----------
d = "2026-11-14"
P.append(wort(d, "der Stammtisch", "постоянный стол, свои люди",
              "Jeden Donnerstag ist Stammtisch.",
              "Каждый четверг собираемся своей компанией.",
 "<b>der Stammtisch</b> — стол для своих 🍺🪑📌\n"
 "der Stamm — здесь «постоянный», der Tisch — стол\n\n"
 "<i>Jeden Donnerstag ist Stammtisch.</i>\n— Каждый четверг собираемся своей "
 "компанией.\n\n"
 "💡 <b>Использование</b>\nДва значения сразу: сам стол в трактире, "
 "закреплённый за постоянными гостями (бывает табличка "
 "<i>Stammtisch</i> — за него не садятся случайные посетители), и сама "
 "компания, которая там собирается.\n\n"
 "<b>Примеры:</b>\n• der Stammgast — постоянный гость\n"
 "• das Stammlokal — любимое заведение\n"
 "• zum Stammtisch gehen — идти на посиделки со своими\n\n"
 "🍺 Есть у тебя своё место?"))
P.append(quiz(d, "🚆 Вставь форму: «Der Zug ___ heute ___.» (ausfallen)",
              ["fällt … aus", "ausfällt …", "fällt … ab"], 0,
 "ausfallen — отделяемый глагол: Der Zug fällt heute aus. Приставка aus "
 "уезжает в самый конец."))
P.append(evening(d, "ЖИЗНЬ В ГЕРМАНИИ", "Mülltrennung", "разделение мусора",
                 "Papier kommt in die blaue Tonne.",
                 "Бумага идёт в синий бак.", "Пять потоков, не считая Pfand",
 "🇩🇪 <b>Мусор в Германии: куда что</b> ♻️\n\n"
 "Для новичка это первый бытовой квест. Цвета баков различаются по городам, "
 "но потоки везде одни 👇\n\n"
 "🔵 <b>Papier</b> — бумага, картон, газеты. Не класть: чеки, грязный "
 "картон из-под пиццы.\n\n"
 "🟡 <b>Gelber Sack / Gelbe Tonne</b> — упаковка: пластик, фольга, "
 "тетрапак, консервные банки.\n\n"
 "🟤 <b>Biomüll</b> — пищевые отходы, кожура, кофейная гуща, бумажные "
 "полотенца без химии.\n\n"
 "⚫️ <b>Restmüll</b> — всё, что не подошло выше.\n\n"
 "🟢 <b>Altglas</b> — стекло по цветам: weiß, grün, braun. Контейнеры "
 "стоят на улице; ночью и в воскресенье выбрасывать не принято из-за "
 "шума.\n\n"
 "💰 <b>Pfand</b> — бутылки с залогом в мусор не идут: их сдают в автомат "
 "в супермаркете и забирают деньги.\n\n"
 "💡 Слова на упаковке: <b>Pfandfrei</b> — без залога, "
 "<b>Einweg</b> — одноразовая, <b>Mehrweg</b> — многооборотная." + FOOT2))

# ---------- Вс 15.11 ----------
d = "2026-11-15"
P.append(wort(d, "das Fingerspitzengefühl", "чутьё, такт",
              "Dafür braucht man Fingerspitzengefühl.",
              "Тут нужно чутьё.",
 "<b>das Fingerspitzengefühl</b> — чутьё, такт 🤲✨📌\n"
 "die Fingerspitze — кончик пальца, das Gefühl — чувство\n\n"
 "<i>Dafür braucht man Fingerspitzengefühl.</i>\n— Тут нужно чутьё.\n\n"
 "💡 <b>Использование</b>\nПро умение действовать осторожно и точно там, где "
 "легко задеть: тяжёлый разговор, переговоры, работа с людьми. Не про "
 "ловкость рук, а про чувство меры.\n\n"
 "<b>Примеры:</b>\n• mit Fingerspitzengefühl vorgehen — действовать "
 "деликатно\n• Ihm fehlt jedes Fingerspitzengefühl. — Ему совершенно не "
 "хватает такта.\n• das Feingefühl — почти то же самое\n\n"
 "🤲 Где тебе нужнее всего Fingerspitzengefühl?"))
P.append(quiz(d, "📅 Какого падежа требует предлог «seit»?",
              ["Dativ", "Akkusativ", "Genitiv"], 0,
 "seit всегда с Dativ: seit einem Jahr, seit zwei Jahren. Во множественном "
 "добавляется -n."))
P.append(evening(d, "НЕДЕЛЬНЫЙ ТЕСТ", "5 вопросов", "сколько наберёшь?",
                 "Ответы под спойлером", "Проверь себя по итогам недели",
                 "Сохрани и повтори",
 "🧠 <b>Недельный тест: 5 вопросов</b>\n\nПо темам этой недели. Ответь в "
 "голове, потом открой спойлер 👇\n\n"
 "1️⃣ legen или liegen: Das Buch ___ auf dem Tisch.\n"
 "<tg-spoiler>liegt — предмет просто находится там</tg-spoiler>\n\n"
 "2️⃣ Как вежливо попросить о помощи?\n"
 "<tg-spoiler>Könnten Sie mir helfen?</tg-spoiler>\n\n"
 "3️⃣ Ich wohne ___ zwei Monate hier, всё ещё новое.\n"
 "<tg-spoiler>erst</tg-spoiler>\n\n"
 "4️⃣ Как пожелать удачи перед экзаменом?\n"
 "<tg-spoiler>Ich drücke dir die Daumen! / Viel Erfolg!</tg-spoiler>\n\n"
 "5️⃣ Куда идёт Gelber Sack?\n"
 "<tg-spoiler>упаковка: пластик, фольга, тетрапак</tg-spoiler>\n\n"
 "🏆 5 из 5 — ты огонь! 3–4 — отлично! Меньше 3 — пролистай посты недели "
 "ещё раз 😉\n\nСохрани и повтори 📌\n<b>Lingofy Deutsch</b>"))

# ---------- запись ----------
for p in P:
    p.pop("cap_len_check", None)

root = os.path.join(os.path.dirname(__file__), "..")
qp = os.path.join(root, "queue.json")
queue = json.load(open(qp, encoding="utf-8"))
ids = {p["id"] for p in queue}
new = [p for p in P if p["id"] not in ids]
queue += new
json.dump(queue, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(new), "новых постов; в очереди", len(queue))

for p in P:
    if p["type"] == "photo":
        assert len(p["caption"]) <= 1024, (p["id"], len(p["caption"]))
    else:
        assert len(p["question"]) <= 300, (p["id"], "вопрос", len(p["question"]))
        assert len(p["explanation"]) <= 200, (p["id"], "пояснение",
                                              len(p["explanation"]))
        for o in p["options"]:
            assert len(o) <= 100, (p["id"], "вариант", o)
print("ограничения телеграма соблюдены")

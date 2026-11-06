# -*- coding: utf-8 -*-
"""Вторая партия: пятнадцать роликов на 7 ноября.

Та же раскладка — пять аккаунтов по три ролика, у каждого свой формат,
шрифт, фон и пара голосов. Меняется только содержание.

Ни одна тема не повторяет ни первую партию, ни квизы до неё, ни посты,
которые уже стоят в очереди телеграма. Вариант оформления внутри
аккаунта сдвинут на единицу, и окно в треке взято другое, чтобы день
ото дня было не одно и то же.

Немецкий здесь — то, что говорят. Где у фразы есть второй равноправный
вариант, он назван в пояснении, а не объявлен ошибкой.
"""

# A — квиз: (вопрос, [три варианта], номер верного, пояснение, что сказать по-немецки)
A1 = [
    ("«Я кладу книгу на стол»",
     ["Ich lege das Buch auf den Tisch", "Ich lege das Buch auf dem Tisch",
      "Ich lege das Buch auf der Tisch"], 0,
     "Есть движение — значит Akkusativ: auf den Tisch.",
     "Ich lege das Buch auf den Tisch."),
    ("«Книга лежит на столе»",
     ["Das Buch liegt auf dem Tisch", "Das Buch liegt auf den Tisch",
      "Das Buch liegt auf der Tisch"], 0,
     "Движения нет, только место — значит Dativ: auf dem Tisch.",
     "Das Buch liegt auf dem Tisch."),
    ("«Я иду в кино»",
     ["Ich gehe ins Kino", "Ich gehe im Kino", "Ich gehe in dem Kino"], 0,
     "ins = in das. Идём куда-то, поэтому Akkusativ.", "Ich gehe ins Kino."),
    ("«Я сижу в кино»",
     ["Ich sitze im Kino", "Ich sitze ins Kino", "Ich sitze in das Kino"], 0,
     "im = in dem. Сидим где-то, поэтому Dativ.", "Ich sitze im Kino."),
    ("«Повесь куртку в шкаф»",
     ["Häng die Jacke in den Schrank", "Häng die Jacke im Schrank",
      "Häng die Jacke in der Schrank"], 0,
     "Вешаем внутрь — движение, Akkusativ.", "Häng die Jacke in den Schrank."),
    ("«Куртка висит в шкафу»",
     ["Die Jacke hängt im Schrank", "Die Jacke hängt in den Schrank",
      "Die Jacke hängt in der Schrank"], 0,
     "Висит на месте — Dativ. Тот же предлог, другой падеж.",
     "Die Jacke hängt im Schrank."),
]

A2 = [
    ("«Я помогаю другу»",
     ["Ich helfe meinem Freund", "Ich helfe meinen Freund",
      "Ich helfe mein Freund"], 0,
     "helfen идёт с Dativ — как и в русском «помогаю кому».",
     "Ich helfe meinem Freund."),
    ("«Мне нравится эта песня»",
     ["Das Lied gefällt mir", "Das Lied gefällt mich",
      "Ich gefalle das Lied"], 0,
     "gefallen переворачивает фразу: нравится песня, а не я.",
     "Das Lied gefällt mir."),
    ("«Эта сумка принадлежит мне»",
     ["Die Tasche gehört mir", "Die Tasche gehört mich",
      "Die Tasche gehört meiner"], 0,
     "gehören — тоже Dativ, без всякого предлога.", "Die Tasche gehört mir."),
    ("«Я благодарю тебя»",
     ["Ich danke dir", "Ich danke dich", "Ich danke dein"], 0,
     "danken с Dativ, хотя по-русски «благодарю кого».", "Ich danke dir."),
    ("«Куртка тебе идёт»",
     ["Die Jacke steht dir", "Die Jacke steht dich",
      "Die Jacke steht deine"], 0,
     "stehen в значении «идёт, к лицу» — с Dativ. По размеру подходит — passen, тоже Dativ.",
     "Die Jacke steht dir."),
    ("«Ответь мне»",
     ["Antworte mir", "Antworte mich", "Antworte an mich"], 0,
     "antworten с Dativ и без предлога: antworte mir.", "Antworte mir."),
]

A3 = [
    ("Что такое der Handschuh?",
     ["перчатка", "наручные часы", "рукопожатие"], 0,
     "Hand + Schuh — «ботинок для руки». Немцы собирают слова насквозь.",
     "der Handschuh"),
    ("Что такое der Staubsauger?",
     ["пылесос", "пыльная буря", "пепельница"], 0,
     "Staub — пыль, saugen — всасывать.", "der Staubsauger"),
    ("Что такое das Feuerzeug?",
     ["зажигалка", "пожарная машина", "костёр"], 0,
     "Feuer — огонь, Zeug — штуковина. Пожарная машина — das Feuerwehrauto.",
     "das Feuerzeug"),
    ("Что такое der Krankenwagen?",
     ["скорая помощь", "инвалидное кресло", "больничная койка"], 0,
     "krank — больной, Wagen — машина.", "der Krankenwagen"),
    ("Что такое die Schildkröte?",
     ["черепаха", "жаба", "дорожный знак"], 0,
     "Schild — щит, Kröte — жаба. Получилась «щитожаба».", "die Schildkröte"),
    ("Что такое der Reißverschluss?",
     ["молния на одежде", "порванный шов", "засов"], 0,
     "reißen — рвать, Verschluss — застёжка.", "der Reißverschluss"),
]

def _spread(rows):
    """Разносит правильный ответ по буквам.

    Писать варианты удобно, когда верный идёт первым, но смотреть такой квиз
    нельзя: к третьему вопросу видно, что ответ всегда «А», и дальше никто не
    думает. Сдвиг фиксированный, не случайный, — чтобы пересборка давала тот
    же ролик, что уже проверен глазами.
    """
    shift = [1, 2, 0, 2, 0, 1]
    out = []
    for i, r in enumerate(rows):
        s = shift[i % len(shift)]
        opts = [None, None, None]
        for j, o in enumerate(r[1]):
            opts[(j + s) % 3] = o
        out.append((r[0], opts, (r[2] + s) % 3) + tuple(r[3:]))
    return out


A1, A2, A3 = _spread(A1), _spread(A2), _spread(A3)


# B — разбор: (фраза, перевод, [(кусок, подпись), ...])
B1 = [
    ("Ich möchte ein Paket schicken.", "Я хотел бы отправить посылку.",
     [("Ich möchte", "вежливое «я хотел бы»"),
      ("ein Paket", "посылку — Akkusativ"),
      ("schicken.", "отправить, инфинитив уходит в конец")]),
    ("Wie lange dauert der Versand?", "Сколько идёт отправление?",
     [("Wie lange", "как долго"),
      ("dauert", "длится"),
      ("der Versand?", "пересылка, отправка")]),
    ("Ich brauche eine Sendungsnummer.", "Мне нужен трек-номер.",
     [("Ich brauche", "мне нужно — brauchen с Akkusativ"),
      ("eine Sendungsnummer.", "Sendung — отправление, Nummer — номер")]),
    ("Können Sie das als Einschreiben schicken?",
     "Можете отправить это заказным?",
     [("Können Sie", "вежливый вопрос с модальным глаголом"),
      ("das als Einschreiben", "als без артикля: «в качестве заказного»"),
      ("schicken?", "смысловой глагол в конец")]),
    ("Die Sendung ist unterwegs verloren gegangen.",
     "Отправление потерялось в пути.",
     [("Die Sendung", "отправление"),
      ("ist", "verloren gehen идёт с sein"),
      ("unterwegs", "в пути"),
      ("verloren gegangen.", "причастие в самом конце")]),
]

B2 = [
    ("Ich habe drei Jahre als Entwickler gearbeitet.",
     "Я три года работал разработчиком.",
     [("Ich habe", "перфект строится с haben"),
      ("drei Jahre", "сколько времени — Akkusativ, без предлога"),
      ("als Entwickler", "als в значении «в качестве», артикль не нужен"),
      ("gearbeitet.", "причастие уезжает в конец")]),
    ("Was sind Ihre Stärken?", "В чём ваши сильные стороны?",
     [("Was sind", "глагол на втором месте"),
      ("Ihre Stärken?", "die Stärke — сила, сильная сторона")]),
    ("Ich bin ab Januar verfügbar.", "Я свободен с января.",
     [("Ich bin", "связка sein"),
      ("ab Januar", "ab — начиная с, месяц без артикля"),
      ("verfügbar.", "доступен, свободен — в конце")]),
    ("Wie sieht die Einarbeitung aus?", "Как устроено введение в должность?",
     [("Wie sieht", "от aussehen, первая часть на месте глагола"),
      ("die Einarbeitung", "введение в курс дела на новой работе"),
      ("aus?", "приставка уезжает в конец")]),
    ("Ich würde mich über eine Rückmeldung freuen.",
     "Буду рад обратной связи.",
     [("Ich würde mich", "Konjunktiv — самая вежливая форма"),
      ("über eine Rückmeldung", "sich freuen über + Akkusativ"),
      ("freuen.", "смысловой глагол в конце")]),
]

B3 = [
    ("Ich möchte meinen Vertrag kündigen.", "Я хочу расторгнуть договор.",
     [("Ich möchte", "вежливее, чем ich will"),
      ("meinen Vertrag", "договор — Akkusativ"),
      ("kündigen.", "расторгнуть, подать отказ")]),
    ("Wann läuft die Kündigungsfrist ab?", "Когда истекает срок отказа?",
     [("Wann läuft", "от ablaufen — истекать"),
      ("die Kündigungsfrist", "срок, до которого надо подать отказ"),
      ("ab?", "приставка в конец")]),
    ("Bitte bestätigen Sie die Kündigung schriftlich.",
     "Подтвердите расторжение письменно.",
     [("Bitte bestätigen Sie", "вежливое повеление на Sie"),
      ("die Kündigung", "расторжение"),
      ("schriftlich.", "письменно — одним словом")]),
    ("Der Vertrag verlängert sich automatisch.",
     "Договор продлевается автоматически.",
     [("Der Vertrag", "договор"),
      ("verlängert sich", "возвратный глагол: продлевается сам"),
      ("automatisch.", "автоматически")]),
    ("Ich widerspreche der Verlängerung.", "Я возражаю против продления.",
     [("Ich widerspreche", "widersprechen идёт с Dativ"),
      ("der Verlängerung.", "продлению — Dativ, без предлога")]),
]

# C — переписка: (кто 0/1, немецкая реплика, перевод)
C1 = [
    (0, "Guten Morgen, ich komme heute später.",
     "Доброе утро, я сегодня опоздаю."),
    (1, "Was ist denn los?", "А что случилось?"),
    (0, "Die S-Bahn fällt aus.", "Электричку отменили."),
    (1, "Wie lange brauchst du?", "Сколько тебе нужно времени?"),
    (0, "Etwa eine halbe Stunde.", "Примерно полчаса."),
    (1, "Okay, ich sage Bescheid.", "Хорошо, я предупрежу."),
    (0, "Danke dir!", "Спасибо тебе!"),
    (1, "Kein Stress, komm gut an.", "Без паники, добирайся спокойно."),
    (0, "Das Meeting um zehn schaffe ich.", "На встречу в десять успею."),
    (1, "Super, wir warten.", "Отлично, подождём."),
    (0, "Bis gleich!", "До скорого!"),
    (1, "Bis gleich!", "До скорого!"),
]

C2 = [
    (0, "Hallo Frau Weber, eine kurze Frage.",
     "Здравствуйте, госпожа Вебер, короткий вопрос."),
    (1, "Ja, gerne.", "Да, пожалуйста."),
    (0, "Können wir den Termin verschieben?", "Можем перенести встречу?"),
    (1, "Natürlich. Auf wann denn?", "Конечно. А на когда?"),
    (0, "Ginge Donnerstag auch?", "Четверг тоже подошёл бы?"),
    (1, "Donnerstag ist leider voll.", "Четверг, к сожалению, занят."),
    (0, "Und Freitag früh?", "А в пятницу утром?"),
    (1, "Freitag um neun geht.", "В пятницу в девять можно."),
    (0, "Perfekt, danke für Ihr Verständnis.",
     "Отлично, спасибо за понимание."),
    (1, "Ich trage es gleich ein.", "Сейчас внесу в календарь."),
    (0, "Bis Freitag!", "До пятницы!"),
    (1, "Bis dann!", "До встречи!"),
]

C3 = [
    (0, "Hallo, ist die Jacke noch da?", "Здравствуйте, куртка ещё есть?"),
    (1, "Ja, sie ist noch zu haben.", "Да, ещё в наличии."),
    (0, "Welche Größe ist das?", "Какой это размер?"),
    (1, "Größe M, kaum getragen.", "Размер M, почти не ношена."),
    (0, "Gibt es Mängel?", "Есть дефекты?"),
    (1, "Nur ein kleiner Kratzer am Reißverschluss.",
     "Только маленькая царапина на молнии."),
    (0, "Würden Sie vierzig Euro nehmen?", "Возьмёте сорок евро?"),
    (1, "Fünfundvierzig, dann schicke ich heute los.",
     "Сорок пять, и я отправлю сегодня."),
    (0, "Einverstanden.", "Согласен."),
    (1, "Zahlung per Überweisung?", "Оплата переводом?"),
    (0, "Ja, schicken Sie mir die Daten.", "Да, пришлите реквизиты."),
    (1, "Mache ich, danke!", "Сделаю, спасибо!"),
]

# D — ошибка → верно: (неверно, верно, пояснение)
D1 = [
    ("Ich fahre zu dem Bahnhof.", "Ich fahre zum Bahnhof.",
     "zu + dem сливается в zum. Раздельно говорят, только когда нужно "
     "указать на конкретный вокзал."),
    ("Wir treffen uns an dem Montag.", "Wir treffen uns am Montag.",
     "С днями недели всегда am: am Montag, am Wochenende."),
    ("Ich bin in dem Kino.", "Ich bin im Kino.",
     "in + dem = im. Раздельная форма звучит книжно и в обычной речи не идёт."),
    ("Sie geht zu der Arbeit.", "Sie geht zur Arbeit.",
     "zu + der = zur. Слияние здесь обязательно."),
    ("Das Geschäft ist bei dem Bahnhof.", "Das Geschäft ist beim Bahnhof.",
     "bei + dem = beim. Та же логика, что у zum и im."),
]

D2 = [
    ("Was du machst?", "Was machst du?",
     "После вопросительного слова сразу идёт глагол, потом подлежащее."),
    ("Wo du wohnst?", "Wo wohnst du?",
     "Глагол стоит вторым и в вопросе тоже."),
    ("Warum du nicht kommst?", "Warum kommst du nicht?",
     "Глагол на второе место, nicht уезжает в конец."),
    ("Wann wir treffen uns?", "Wann treffen wir uns?",
     "Возвратное uns идёт после подлежащего, а не перед ним."),
    ("Du kommst morgen?", "Kommst du morgen?",
     "В вопросе без вопросительного слова глагол идёт первым. С интонацией "
     "поймут и первый вариант, но нейтральная форма — эта."),
]

D3 = [
    ("Ich sehe ihm.", "Ich sehe ihn.",
     "sehen требует Akkusativ: ihn. Форма ihm — это Dativ."),
    ("Ich helfe ihn.", "Ich helfe ihm.",
     "helfen наоборот требует Dativ: ihm."),
    ("Kannst du mich helfen?", "Kannst du mir helfen?",
     "Та же пара: helfen с Dativ, значит mir."),
    ("Ich rufe dir an.", "Ich rufe dich an.",
     "anrufen идёт с Akkusativ: ich rufe dich an."),
    ("Das gehört mich.", "Das gehört mir.",
     "gehören с Dativ и без предлога."),
]

# E — карточки: (слово, перевод, пример, перевод примера)
E1 = [
    ("die Rechnung", "счёт к оплате", "Die Rechnung kommt per Post.",
     "Счёт придёт по почте."),
    ("die Mahnung", "напоминание о просрочке",
     "Nach zwei Wochen kommt eine Mahnung.",
     "Через две недели приходит напоминание."),
    ("die Lastschrift", "списание со счёта", "Ich zahle per Lastschrift.",
     "Я плачу списанием со счёта."),
    ("der Dauerauftrag", "постоянное поручение банку",
     "Die Miete läuft über einen Dauerauftrag.",
     "Аренда уходит постоянным платежом."),
    ("das Guthaben", "остаток, деньги на счету",
     "Auf der Karte ist noch Guthaben.", "На карте ещё есть деньги."),
    ("die Rückerstattung", "возврат денег",
     "Die Rückerstattung dauert zehn Tage.", "Возврат идёт десять дней."),
]

E2 = [
    ("der Sprachkurs", "языковой курс", "Ich besuche einen Sprachkurs.",
     "Я хожу на языковой курс."),
    ("die Prüfung", "экзамен", "Die Prüfung ist nächste Woche.",
     "Экзамен на следующей неделе."),
    ("bestehen", "сдать экзамен", "Ich habe die Prüfung bestanden.",
     "Я сдал экзамен."),
    ("durchfallen", "провалить экзамен", "Er ist leider durchgefallen.",
     "Он, к сожалению, провалился."),
    ("das Zeugnis", "свидетельство, аттестат",
     "Das Zeugnis bekommst du per Post.", "Свидетельство придёт по почте."),
    ("die Hausaufgabe", "домашнее задание",
     "Hast du die Hausaufgaben gemacht?", "Ты сделал домашку?"),
]

E3 = [
    ("glatt", "скользкий", "Vorsicht, die Straße ist glatt.",
     "Осторожно, дорога скользкая."),
    ("streuen", "посыпать солью или песком", "Der Hausmeister streut Salz.",
     "Дворник посыпает солью."),
    ("die Winterreifen", "зимние шины",
     "Faustregel: von Oktober bis Ostern.",
     "Негласное правило: с октября до Пасхи."),
    ("der Nebel", "туман", "Morgens liegt oft Nebel.",
     "По утрам часто стоит туман."),
    ("frieren", "мёрзнуть", "Ich friere an den Händen.",
     "У меня мёрзнут руки."),
    ("der Schneeregen", "мокрый снег", "Draußen ist Schneeregen.",
     "На улице мокрый снег."),
]


# ─────────────── пятнадцать роликов ───────────────
# mus_off — своё окно в треке, не такое, как вчера

V = [
    dict(key="f1_wohin", acc="A", variant=1, rows=A1, mus_off=16.0,
         title="Куда или где", hook="Куда или где? Один предлог, два падежа",
         hook_de="Wechselpräpositionen: wohin oder wo?",
         sub="шесть пар на проверку",
         end="Сколько из шести?", end_de="Wie viele hast du richtig?"),
    dict(key="f2_dativverben", acc="A", variant=2, rows=A2, mus_off=16.0,
         title="Глаголы с Dativ", hook="Шесть глаголов, которые требуют Dativ",
         hook_de="Verben mit Dativ — sechs Stück",
         sub="их просто учат списком",
         end="Где ошибся?", end_de="Wo lagst du daneben?"),
    dict(key="f3_komposita", acc="A", variant=0, rows=A3, mus_off=16.0,
         title="Слово из двух", hook="Угадаешь слово по двум половинкам?",
         hook_de="Komposita: zwei Wörter, ein Sinn",
         sub="шесть составных слов",
         end="Сколько угадал?", end_de="Wie viele hast du erraten?"),

    dict(key="g1_post", acc="B", variant=1, rows=B1, mus_off=28.0,
         title="На почте", hook="Пять фраз для похода на почту",
         hook_de="Fünf Sätze für die Post",
         sub="посылка, трек-номер, заказное",
         end="Сохрани перед отправкой", end_de="Merk dir diese Sätze."),
    dict(key="g2_bewerbung", acc="B", variant=2, rows=B2, mus_off=28.0,
         title="Собеседование", hook="Пять фраз для собеседования",
         hook_de="Fünf Sätze fürs Vorstellungsgespräch",
         sub="опыт, сильные стороны, сроки",
         end="Пригодится на первом же", end_de="Das brauchst du sofort."),
    dict(key="g3_kuendigung", acc="B", variant=0, rows=B3, mus_off=28.0,
         title="Расторгнуть договор", hook="Пять фраз, чтобы расторгнуть договор",
         hook_de="Fünf Sätze für die Kündigung",
         sub="сроки, подтверждение, продление",
         end="Это спасает деньги", end_de="Das spart dir Geld."),

    dict(key="h1_verspaetung", acc="C", variant=1, rows=C1, mus_off=41.0,
         title="Опаздываю на работу", hook="Опаздываешь на работу. Что писать?",
         hook_de="Ich komme heute später",
         sub="двенадцать реплик, по делу и коротко",
         end="Скопируй себе", end_de="Nimm diese Sätze mit."),
    dict(key="h2_verschieben", acc="C", variant=2, rows=C2, mus_off=41.0,
         title="Перенести встречу", hook="Как перенести встречу и не обидеть",
         hook_de="Einen Termin verschieben",
         sub="вежливо, на Sie",
         end="Сохрани до следующего раза", end_de="Heb dir das auf."),
    dict(key="h3_kleinanzeigen", acc="C", variant=0, rows=C3, mus_off=41.0,
         title="Продать вещь", hook="Продаёшь вещь. Как вести переписку",
         hook_de="Verkaufen auf Kleinanzeigen",
         sub="размер, дефекты, торг, оплата",
         end="Торгуйся спокойно", end_de="Handeln ist normal."),

    dict(key="i1_verschmelzung", acc="D", variant=1, rows=D1, mus_off=54.0,
         title="zum, im, zur", hook="Пять фраз, где забывают слить предлог",
         hook_de="zu dem oder zum? Die Verschmelzung",
         sub="мелочь, которая сразу слышна",
         end="Где говорил раздельно?", end_de="Wo hast du getrennt?"),
    dict(key="i2_fragen", acc="D", variant=2, rows=D2, mus_off=54.0,
         title="Вопросы", hook="Пять вопросов, заданных не в том порядке",
         hook_de="Fragen: wo steht das Verb?",
         sub="глагол стоит не там",
         end="Сколько узнал за собой?", end_de="Wie viele kennst du?"),
    dict(key="i3_pronomen", acc="D", variant=0, rows=D3, mus_off=54.0,
         title="ihn или ihm", hook="Пять фраз, где путают ihn и ihm",
         hook_de="Akkusativ oder Dativ beim Pronomen",
         sub="глагол решает, какой падеж",
         end="Какую говорил сам?", end_de="Welche kam dir bekannt vor?"),

    dict(key="j1_geld", acc="E", variant=1, rows=E1, mus_off=62.0,
         title="Счета и деньги", hook="Шесть слов из немецких счетов",
         hook_de="Sechs Wörter rund ums Konto",
         sub="переворачивай и проверяй",
         end="Какое слово новое?", end_de="Welches Wort war neu?"),
    dict(key="j2_lernen", acc="E", variant=2, rows=E2, mus_off=62.0,
         title="Курсы и экзамены", hook="Шесть слов про учёбу и экзамены",
         hook_de="Sechs Wörter für Kurs und Prüfung",
         sub="сдал, провалил, аттестат",
         end="Когда у тебя Prüfung?", end_de="Wann ist deine Prüfung?"),
    dict(key="j3_winter", acc="E", variant=0, rows=E3, mus_off=62.0,
         title="Зима за окном", hook="Шесть слов про зиму и гололёд",
         hook_de="Sechs Wörter für den Winter",
         sub="скользко, туман, шины",
         end="Уже переобулся?", end_de="Schon Winterreifen drauf?"),
]

BY = {v["key"]: v for v in V}


def cfg(key):
    """Готовый конфиг ролика: содержание плюс оформление его аккаунта."""
    import acc as A
    v = dict(BY[key])
    th = dict(A.ACC[v["acc"]])
    if "mus_off" in v:
        th["mus_off"] = v["mus_off"]
    v["th"] = th
    return v

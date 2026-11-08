# -*- coding: utf-8 -*-
"""Третья партия: пятнадцать роликов на 8 ноября.

Темы сверены со всеми 436 прошлыми роликами и с очередью телеграма до
15 ноября — ни одна не повторяется. Там, где тема близка к уже выходившей,
взят другой угол: не «квартира», а сдача квартиры; не «счета», а расчётный
листок; не «числа», а даты и порядковые.

Немецкий здесь — то, что говорят. Где у фразы есть второй равноправный
вариант, он назван в пояснении, а не объявлен ошибкой.
"""

# A — квиз: (вопрос, [три варианта], номер верного, пояснение, что сказать по-немецки)
A1 = [
    ("«Иди сюда» — другу",
     ["Komm her!", "Kommst du her!", "Kommen her!"], 0,
     "В повелительном на du окончание отпадает: komm, geh, mach.",
     "Komm her!"),
    ("«Дай мне ручку» — другу",
     ["Gib mir den Stift!", "Geb mir den Stift!", "Gebe mir den Stift!"], 0,
     "У geben в du-форме e меняется на i, и в повелительном тоже: du gibst, gib!",
     "Gib mir den Stift."),
    ("«Езжайте прямо» — вежливо",
     ["Fahren Sie geradeaus!", "Fahrt Sie geradeaus!", "Fahre Sie geradeaus!"], 0,
     "На Sie берётся инфинитив, и Sie идёт сразу после глагола.",
     "Fahren Sie geradeaus."),
    ("«Будь спокоен» — другу",
     ["Sei ruhig!", "Bist ruhig!", "Sein ruhig!"], 0,
     "sein — единственный неправильный: sei, seid, seien Sie.",
     "Sei ruhig."),
    ("«Читай громче» — другу",
     ["Lies lauter!", "Lese lauter!", "Liest lauter!"], 0,
     "У lesen e меняется на ie: du liest, lies!",
     "Lies lauter."),
    ("«Подождите немного» — вежливо",
     ["Warten Sie bitte kurz!", "Wartet Sie bitte kurz!", "Warte Sie bitte kurz!"], 0,
     "Та же схема: инфинитив плюс Sie. Bitte смягчает почти всё.",
     "Warten Sie bitte kurz."),
]

A2 = [
    ("«Я знаю его»",
     ["Ich kenne ihn", "Ich weiß ihn", "Ich kann ihn"], 0,
     "kennen — о людях и местах: лично знаком, бывал.",
     "Ich kenne ihn."),
    ("«Я знаю, где он живёт»",
     ["Ich weiß, wo er wohnt", "Ich kenne, wo er wohnt",
      "Ich kann, wo er wohnt"], 0,
     "wissen — о факте, и дальше почти всегда придаточное.",
     "Ich weiß, wo er wohnt."),
    ("«Я умею плавать»",
     ["Ich kann schwimmen", "Ich weiß schwimmen", "Ich kenne schwimmen"], 0,
     "Умение — только können. В русском тут тоже не «знаю».",
     "Ich kann schwimmen."),
    ("«Ты знаешь этот город?»",
     ["Kennst du diese Stadt?", "Weißt du diese Stadt?",
      "Kannst du diese Stadt?"], 0,
     "Город — место, значит kennen.",
     "Kennst du diese Stadt?"),
    ("«Я не знаю» — в ответ на вопрос",
     ["Ich weiß nicht", "Ich kenne nicht", "Ich kann nicht"], 0,
     "Коротко и без дополнения — всегда ich weiß nicht.",
     "Ich weiß nicht."),
    ("«Я знаю немецкий»",
     ["Ich kann Deutsch", "Ich weiß Deutsch", "Ich kenne Deutsch"], 0,
     "Про язык говорят können: владею, могу говорить.",
     "Ich kann Deutsch."),
]

A3 = [
    ("«Сегодня третье мая»",
     ["Heute ist der dritte Mai", "Heute ist der drei Mai",
      "Heute ist dritte Mai"], 0,
     "Число — порядковое, и артикль обязателен: der dritte.",
     "Heute ist der dritte Mai."),
    ("«Я приеду первого июня»",
     ["Ich komme am ersten Juni", "Ich komme am erste Juni",
      "Ich komme an ersten Juni"], 0,
     "am = an dem, дальше Dativ, поэтому ersten с -en.",
     "Ich komme am ersten Juni."),
    ("«Восьмое ноября»",
     ["der achte November", "der achtte November", "der acht November"], 0,
     "acht плюс -te, с одной t. До девятнадцатого суффикс -te.",
     "der achte November"),
    ("«С первого января»",
     ["ab dem ersten Januar", "ab den ersten Januar", "ab der erste Januar"], 0,
     "ab идёт с Dativ: ab dem ersten.",
     "ab dem ersten Januar"),
    ("«Двадцатое»",
     ["der zwanzigste", "der zwanzigte", "der zwanzige"], 0,
     "С двадцати суффикс меняется на -ste: zwanzigste, dreißigste.",
     "der zwanzigste"),
    ("Шапка письма: «Мюнхен, 8 ноября 2026»",
     ["München, den 8. November 2026", "München, der 8. November 2026",
      "München, am 8. November 2026"], 0,
     "В шапке письма стоит Akkusativ: den. Точка после цифры заменяет -te.",
     "München, den achten November."),
]


def _spread(rows):
    """Разносит правильный ответ по буквам.

    Писать варианты удобно, когда верный идёт первым, но смотреть такой квиз
    нельзя: к третьему вопросу видно, что ответ всегда «А», и дальше никто не
    думает. Сдвиг фиксированный, не случайный, — чтобы пересборка давала тот
    же ролик, что уже проверен глазами.
    """
    shift = [2, 0, 1, 1, 2, 0]
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
    ("Ich kann heute leider nicht kommen.", "Я сегодня, к сожалению, не смогу прийти.",
     [("Ich kann", "модальный глагол на втором месте"),
      ("heute leider", "сначала время, потом оценка"),
      ("nicht kommen.", "смысловой глагол уезжает в конец")]),
    ("Ich bin krankgeschrieben.", "У меня больничный.",
     [("Ich bin", "состояние через sein"),
      ("krankgeschrieben.", "от krankschreiben — «выписать больничный»")]),
    ("Ich reiche die Krankmeldung nach.", "Справку донесу позже.",
     [("Ich reiche", "от nachreichen — донести позже"),
      ("die Krankmeldung", "сам документ — Akkusativ"),
      ("nach.", "приставка уезжает в самый конец")]),
    ("Ab wann brauche ich ein Attest?", "С какого дня нужна справка от врача?",
     [("Ab wann", "с какого момента"),
      ("brauche ich", "после обстоятельства глагол встаёт перед подлежащим"),
      ("ein Attest?", "Attest — справка от врача, Akkusativ")]),
    ("Ich melde mich, sobald es mir besser geht.", "Дам знать, как только станет легче.",
     [("Ich melde mich", "sich melden — дать о себе знать"),
      ("sobald", "«как только» — союз придаточного"),
      ("es mir besser geht.", "в придаточном глагол в самом конце")]),
]

B2 = [
    ("Ich möchte meinen Führerschein umschreiben lassen.", "Хочу переоформить права.",
     [("Ich möchte", "вежливее, чем ich will"),
      ("meinen Führerschein", "Akkusativ"),
      ("umschreiben lassen.", "lassen — «поручить сделать», оба инфинитива в конце")]),
    ("Welche Unterlagen brauche ich dafür?", "Какие документы для этого нужны?",
     [("Welche Unterlagen", "Unterlagen — всегда множественное"),
      ("brauche ich", "глагол вторым, подлежащее за ним"),
      ("dafür?", "da + für — «для этого», без повтора существительного")]),
    ("Muss ich die Theorieprüfung wiederholen?", "Теорию надо пересдавать?",
     [("Muss ich", "в вопросе без вопросительного слова глагол первый"),
      ("die Theorieprüfung", "Akkusativ"),
      ("wiederholen?", "инфинитив в конец")]),
    ("Wie lange ist mein alter Führerschein gültig?", "Сколько ещё действуют старые права?",
     [("Wie lange", "как долго"), ("ist", "sein на втором месте"),
      ("mein alter Führerschein", "после mein прилагательное берёт -er"),
      ("gültig?", "действителен")]),
    ("Ich habe einen Termin bei der Fahrschule.", "У меня запись в автошколу.",
     [("Ich habe", "просто «иметь»"), ("einen Termin", "Akkusativ"),
      ("bei der Fahrschule.", "bei всегда с Dativ")]),
]

B3 = [
    ("Ich bin gesetzlich versichert.", "У меня государственная страховка.",
     [("Ich bin", "состояние через sein"),
      ("gesetzlich", "«по закону» — так называют государственную кассу"),
      ("versichert.", "застрахован")]),
    ("Haben Sie eine Haftpflichtversicherung?", "У вас есть страховка ответственности?",
     [("Haben Sie", "вежливый вопрос, глагол первым"),
      ("eine Haftpflichtversicherung?", "Haftpflicht — ответственность за ущерб другим")]),
    ("Die Versicherung übernimmt die Kosten.", "Страховка покрывает расходы.",
     [("Die Versicherung", "подлежащее"),
      ("übernimmt", "übernehmen — брать на себя"),
      ("die Kosten.", "Kosten — всегда во множественном")]),
    ("Ich möchte meinen Tarif wechseln.", "Хочу сменить тариф.",
     [("Ich möchte", "вежливое «хотел бы»"), ("meinen Tarif", "Akkusativ"),
      ("wechseln.", "инфинитив в конец")]),
    ("Wie hoch ist die Selbstbeteiligung?", "Какая франшиза?",
     [("Wie hoch", "буквально «как высоко» — так спрашивают про суммы"),
      ("ist", "глагол вторым"),
      ("die Selbstbeteiligung?", "часть расходов, которую платишь сам")]),
]


# C — переписка: (кто 0/1, немецкая реплика, перевод)
C1 = [
    (0, "Gehen wir dieses Jahr auf den Weihnachtsmarkt?", "Пойдём в этом году на рождественский рынок?"),
    (1, "Klar, wann denn?", "Конечно, когда?"),
    (0, "Freitag nach der Arbeit?", "В пятницу после работы?"),
    (1, "Passt. Welcher Markt?", "Подходит. Какой рынок?"),
    (0, "Der am Marienplatz ist am schönsten.", "На Мариенплац самый красивый."),
    (1, "Da ist es aber immer voll.", "Но там всегда толпа."),
    (0, "Dann um sechs, bevor es voll wird.", "Тогда в шесть, пока не набилось."),
    (1, "Gute Idee. Glühwein zahle ich.", "Хорошая мысль. Глинтвейн с меня."),
    (0, "Denk an das Pfand für die Tasse.", "Не забудь про залог за кружку."),
    (1, "Stimmt, drei Euro, oder?", "Точно, три евро, да?"),
    (0, "Genau. Bis Freitag!", "Именно. До пятницы!"),
    (1, "Bis dann, zieh dich warm an!", "До встречи, одевайся теплее!"),
]

C2 = [
    (0, "Entschuldigung, die Suppe ist kalt.", "Извините, суп холодный."),
    (1, "Oh, das tut mir leid. Ich bringe Ihnen eine neue.", "Ой, прошу прощения. Принесу другой."),
    (0, "Danke. Und die Nudeln sind mit Sahne.", "Спасибо. И паста со сливками."),
    (1, "Hatten Sie ohne bestellt?", "Вы заказывали без?"),
    (0, "Ja, ausdrücklich ohne.", "Да, специально без."),
    (1, "Das tauschen wir aus, Entschuldigung.", "Поменяем, извините."),
    (0, "Kein Problem, danke.", "Не проблема, спасибо."),
    (1, "Die Suppe geht aufs Haus.", "Суп за счёт заведения."),
    (0, "Das ist nett von Ihnen.", "Это очень мило с вашей стороны."),
    (1, "Sonst noch etwas?", "Что-нибудь ещё?"),
    (0, "Nein danke, das war's.", "Нет, спасибо, это всё."),
    (1, "Guten Appetit!", "Приятного аппетита!"),
]

C3 = [
    (0, "Hallo, ich interessiere mich für euren Verein.", "Здравствуйте, интересуюсь вашим клубом."),
    (1, "Schön! Welche Sportart?", "Отлично! Какой вид спорта?"),
    (0, "Volleyball, als Anfänger.", "Волейбол, начинающий."),
    (1, "Dienstags haben wir eine Anfängergruppe.", "По вторникам есть группа для начинающих."),
    (0, "Kann ich zum Probetraining kommen?", "Можно прийти на пробную тренировку?"),
    (1, "Klar, zweimal sogar kostenlos.", "Конечно, два раза даже бесплатно."),
    (0, "Was kostet der Beitrag danach?", "Сколько потом взнос?"),
    (1, "Zwölf Euro im Monat.", "Двенадцать евро в месяц."),
    (0, "Brauche ich eigene Schuhe?", "Своя обувь нужна?"),
    (1, "Hallenschuhe, ja. Helle Sohle bitte.", "Да, зальные. И со светлой подошвой."),
    (0, "Alles klar, dann bis Dienstag.", "Понял, тогда до вторника."),
    (1, "Super, wir freuen uns!", "Супер, ждём!"),
]


# D — ошибка → верно: (неверно, верно, пояснение)
D1 = [
    ("Ich warte dich.", "Ich warte auf dich.",
     "warten всегда с auf и Akkusativ, хотя по-русски «жду тебя» без предлога."),
    ("Ich denke über dich.", "Ich denke an dich.",
     "denken an — думать о ком-то. denken über тоже есть, но значит «иметь мнение»."),
    ("Ich freue mich für das Geschenk.", "Ich freue mich über das Geschenk.",
     "über — о том, что уже случилось. auf — о том, что ещё впереди."),
    ("Sie fragt nach die Adresse.", "Sie fragt nach der Adresse.",
     "nach всегда с Dativ, без исключений."),
    ("Ich erinnere mich an ihm.", "Ich erinnere mich an ihn.",
     "sich erinnern an идёт с Akkusativ: an ihn, не an ihm."),
]

D2 = [
    ("Ich bin stolz über dich.", "Ich bin stolz auf dich.",
     "stolz auf плюс Akkusativ. Предлог тут не угадывается, он просто такой."),
    ("Sie ist zufrieden über die Arbeit.", "Sie ist zufrieden mit der Arbeit.",
     "zufrieden mit плюс Dativ."),
    ("Er ist böse mit mir.", "Er ist böse auf mich.",
     "Злиться на кого-то — böse auf с Akkusativ."),
    ("Ich bin gespannt über den Film.", "Ich bin gespannt auf den Film.",
     "gespannt auf — «жду с интересом», всегда про то, что впереди."),
    ("Das ist typisch von ihm.", "Das ist typisch für ihn.",
     "typisch für плюс Akkusativ."),
]

D3 = [
    ("Weißt du, wo ist der Bahnhof?", "Weißt du, wo der Bahnhof ist?",
     "В косвенном вопросе глагол уезжает в самый конец."),
    ("Ich frage mich, warum kommt er nicht.", "Ich frage mich, warum er nicht kommt.",
     "Сначала подлежащее, потом всё остальное, глагол последним."),
    ("Kannst du mir sagen, wie spät ist es?", "Kannst du mir sagen, wie spät es ist?",
     "Вторая часть — тоже придаточное, порядок тот же."),
    ("Ich weiß nicht, ob kommt sie.", "Ich weiß nicht, ob sie kommt.",
     "Без вопросительного слова ставится ob, и глагол снова в конце."),
    ("Er hat gefragt, wann wir fahren ab.", "Er hat gefragt, wann wir abfahren.",
     "В придаточном приставка возвращается к глаголу и не отрывается."),
]


# E — карточки: (слово, перевод, пример, перевод примера)
E1 = [
    ("der Adventskranz", "адвентский венок",
     "Am Sonntag zünden wir die erste Kerze an.", "В воскресенье зажигаем первую свечу."),
    ("der Glühwein", "глинтвейн",
     "Einen Glühwein mit Schuss, bitte.", "Глинтвейн с ромом, пожалуйста."),
    ("das Pfand", "залог за кружку или бутылку",
     "Das Pfand für die Tasse bekommst du zurück.", "Залог за кружку тебе вернут."),
    ("die Plätzchen", "рождественское печенье",
     "Wir backen jedes Jahr Plätzchen.", "Мы каждый год печём печенье."),
    ("der Lebkuchen", "пряник",
     "Lebkuchen gibt es schon ab September.", "Пряники продают уже с сентября."),
    ("besinnlich", "тихий, располагающий к размышлению",
     "Eine besinnliche Adventszeit!", "Спокойного вам адвента!"),
]

E2 = [
    ("brutto", "до вычетов",
     "Das Gehalt ist brutto angegeben.", "Зарплата указана до вычетов."),
    ("netto", "на руки",
     "Netto bleibt deutlich weniger.", "На руки остаётся заметно меньше."),
    ("die Lohnsteuer", "подоходный налог",
     "Die Lohnsteuer zieht der Arbeitgeber ab.", "Подоходный удерживает работодатель."),
    ("die Steuerklasse", "налоговый класс",
     "Nach der Heirat ändert sich die Steuerklasse.", "После свадьбы класс меняется."),
    ("der Freibetrag", "необлагаемый минимум",
     "Bis zum Freibetrag zahlst du keine Steuer.", "До этой суммы налога нет."),
    ("die Steuererklärung", "налоговая декларация",
     "Die Steuererklärung lohnt sich fast immer.", "Декларацию подать почти всегда выгодно."),
]

E3 = [
    ("die Wohnungsübergabe", "передача квартиры при выезде",
     "Die Übergabe ist am letzten Tag des Monats.", "Передача — в последний день месяца."),
    ("das Übergabeprotokoll", "акт приёма-передачи",
     "Ohne Protokoll unterschreibst du nichts.", "Без акта ничего не подписывай."),
    ("der Zählerstand", "показания счётчика",
     "Den Zählerstand fotografieren nicht vergessen.", "Счётчик не забудь сфотографировать."),
    ("die Kaution", "залог за квартиру",
     "Die Kaution kommt oft erst nach Monaten zurück.", "Залог часто возвращают через месяцы."),
    ("die Nebenkostenabrechnung", "расчёт коммунальных за год",
     "Die Abrechnung kommt einmal im Jahr.", "Расчёт приходит раз в год."),
    ("besenrein", "подметённым, без генеральной уборки",
     "Die Wohnung muss nur besenrein sein.", "Квартиру надо сдать только подметённой."),
]


# ─────────────── пятнадцать роликов ───────────────
# Вариант оформления сдвинут ещё на единицу, окна в треке снова другие.

V = [
    dict(key="k1_imperativ", acc="A", variant=2, rows=A1, mus_off=20.0,
         title="Повелительное наклонение", hook="Скажи это как команду: шесть повелительных",
         hook_de="Der Imperativ: du, ihr oder Sie?",
         sub="у каждого обращения своя форма",
         end="Сколько взял?", end_de="Wie viele hattest du richtig?"),
    dict(key="k2_wissen", acc="A", variant=0, rows=A2, mus_off=20.0,
         title="wissen, kennen, können", hook="Три немецких «знать». Какое куда?",
         hook_de="wissen, kennen oder können?",
         sub="в русском одно слово, в немецком три",
         end="Где споткнулся?", end_de="Wo lagst du daneben?"),
    dict(key="k3_datum", acc="A", variant=1, rows=A3, mus_off=20.0,
         title="Даты", hook="Какого числа? Шесть вопросов про даты",
         hook_de="Das Datum: Ordnungszahlen richtig sagen",
         sub="порядковые числительные и предлоги",
         end="Сколько из шести?", end_de="Wie viele von sechs?"),

    dict(key="l1_krankmeldung", acc="B", variant=0, rows=B1, mus_off=33.0,
         title="Отпроситься по болезни", hook="Пять фраз, чтобы отпроситься по болезни",
         hook_de="Fünf Sätze für die Krankmeldung",
         sub="больничный, справка, когда вернусь",
         end="Сохрани до первого раза", end_de="Merk dir diese Sätze."),
    dict(key="l2_fuehrerschein", acc="B", variant=1, rows=B2, mus_off=33.0,
         title="Права и автошкола", hook="Пять фраз про права и автошколу",
         hook_de="Fünf Sätze rund um den Führerschein",
         sub="переоформление, документы, теория",
         end="Пригодится в Fahrschule", end_de="Das brauchst du dort sofort."),
    dict(key="l3_versicherung", acc="B", variant=2, rows=B3, mus_off=33.0,
         title="Страховка", hook="Пять фраз про страховку",
         hook_de="Fünf Sätze über Versicherungen",
         sub="касса, ответственность, франшиза",
         end="Без этого в Германии никуда", end_de="Ohne das geht hier nichts."),

    dict(key="m1_weihnachtsmarkt", acc="C", variant=1, rows=C1, mus_off=46.0,
         title="Рождественский рынок", hook="Договориться про рождественский рынок",
         hook_de="Verabredung auf dem Weihnachtsmarkt",
         sub="двенадцать реплик, по делу",
         end="Скопируй себе", end_de="Nimm diese Sätze mit."),
    dict(key="m2_reklamation", acc="C", variant=2, rows=C2, mus_off=46.0,
         title="Пожаловаться в ресторане", hook="Блюдо не то. Как сказать и не поссориться",
         hook_de="Reklamation im Restaurant",
         sub="вежливо, но по существу",
         end="Работает в любом кафе", end_de="Das klappt überall."),
    dict(key="m3_sportverein", acc="C", variant=0, rows=C3, mus_off=46.0,
         title="Записаться в секцию", hook="Записаться в спортивный клуб",
         hook_de="Anmeldung beim Sportverein",
         sub="пробная тренировка, взнос, обувь",
         end="Verein — это дёшево", end_de="Im Verein ist Sport günstig."),

    dict(key="n1_verbpraep", acc="D", variant=2, rows=D1, mus_off=55.0,
         title="Глаголы с предлогами", hook="Пять глаголов, у которых свой предлог",
         hook_de="Verben mit fester Präposition",
         sub="их не угадать, только выучить",
         end="Какой забыл?", end_de="Welche Präposition fehlte dir?"),
    dict(key="n2_adjpraep", acc="D", variant=0, rows=D2, mus_off=55.0,
         title="Прилагательные с предлогами", hook="Пять прилагательных со своим предлогом",
         hook_de="Adjektive mit fester Präposition",
         sub="stolz auf, zufrieden mit",
         end="Запиши парами", end_de="Lern sie immer als Paar."),
    dict(key="n3_indirekt", acc="D", variant=1, rows=D3, mus_off=55.0,
         title="Косвенный вопрос", hook="Пять вопросов, где глагол стоит не там",
         hook_de="Indirekte Fragen: das Verb ans Ende",
         sub="вежливый вопрос ломает порядок слов",
         end="Глагол — в конец", end_de="Das Verb geht ganz nach hinten."),

    dict(key="o1_advent", acc="E", variant=0, rows=E1, mus_off=59.0,
         title="Адвент", hook="Шесть слов про адвент и рождественский рынок",
         hook_de="Sechs Wörter für die Adventszeit",
         sub="скоро пригодятся",
         end="Какое слово новое?", end_de="Welches Wort war neu?"),
    dict(key="o2_steuer", acc="E", variant=1, rows=E2, mus_off=59.0,
         title="Расчётный листок", hook="Шесть слов из немецкого расчётного листка",
         hook_de="Sechs Wörter von der Gehaltsabrechnung",
         sub="брутто, нетто и всё между ними",
         end="Теперь листок читается", end_de="Jetzt kannst du sie lesen."),
    dict(key="o3_uebergabe", acc="E", variant=2, rows=E3, mus_off=59.0,
         title="Сдача квартиры", hook="Шесть слов про сдачу квартиры",
         hook_de="Sechs Wörter für die Wohnungsübergabe",
         sub="протокол, счётчик, залог",
         end="besenrein — запомни это", end_de="Besenrein, mehr nicht."),
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

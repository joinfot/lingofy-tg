# -*- coding: utf-8 -*-
"""Свод всех прошлых тем: topics.py

Нужен, чтобы ни одна новая тема не повторила уже вышедшую. Ролики
копились партиями в разных модулях, часть лежит только в репозитории,
поэтому собираю отовсюду и привожу к сравнимому виду — по словам, а не
по точному совпадению строк.
"""
import glob
import importlib
import os
import re
import sys

sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/home/claude/lingofy-tg/video")
sys.path.insert(0, "/home/claude/past")

STOP = set("""и в во на не что он а то все она так его но да ты к у же
вы за бы по только ее мне было вот от меня еще нет о из ему теперь когда
даже ну ли если или ни быть был него до вас нибудь опять уж вам ведь там
потом себя ничего ей может они тут где есть надо ней для мы тебя их чем
была сам чтоб без будто чего раз тоже себе под будет ж тогда кто этот
того потому этого какой ним здесь этом один почти мой тем чтобы нее
кажется сейчас были куда зачем всех никогда можно при наконец два об
другой хоть после над больше тот через эти нас про всего них какая много
разве три эту моя впрочем хорошо свою этой перед иногда лучше чуть том
нельзя такой им более всегда конечно всю между это как по с для из
der die das ein eine den dem des zu mit auf für von im am ist sind
nicht auch nur noch wie bei aus man sich dass""".split())


def words(s):
    return {w for w in re.findall(r"[\wäöüßА-Яа-яЁё-]{4,}", str(s).lower())
            if w not in STOP}


def harvest(skip=()):
    """Все строковые литералы из файлов партий — разбором, без запуска.

    Раньше модули импортировались, и старые скрипты из past/ начинали
    на импорте делать свою работу: один полез резать озвучку. Поэтому
    файлы теперь читаются как текст.
    """
    import ast
    seen = {}
    files = sorted(set(
        glob.glob("/home/claude/accdata*.py") +
        glob.glob("/home/claude/content*.py") +
        glob.glob("/home/claude/past/*.py") +
        glob.glob("/home/claude/lingofy-tg/video/accdata*.py") +
        glob.glob("/home/claude/lingofy-tg/video/content*.py")))
    for f in files:
        name = os.path.basename(f)[:-3]
        if name in seen or name in skip:
            continue
        try:
            tree = ast.parse(open(f, encoding="utf-8").read())
        except Exception as e:
            print(f"  {name}: не разбирается ({e})")
            continue
        got = [n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        if not got:
            continue
        seen[name] = len(got)
        yield from got
    print("разобраны файлы:",
          ", ".join(f"{k}({v})" for k, v in seen.items()))


def _unused_old_harvest():
    seen = {}
    files = sorted(set(
        glob.glob("/home/claude/accdata*.py") +
        glob.glob("/home/claude/content*.py") +
        glob.glob("/home/claude/past/*.py") +
        glob.glob("/home/claude/lingofy-tg/video/accdata*.py") +
        glob.glob("/home/claude/lingofy-tg/video/content*.py")))
    for f in files:
        name = os.path.basename(f)[:-3]
        if name in seen:
            continue
        try:
            m = importlib.import_module(name)
        except Exception as e:
            print(f"  {name}: не импортируется ({e})")
            continue
        # партии назывались по-разному: V, VIDEOS, Y, BANK, NEW
        # партии назывались по-разному и хранились то списком, то словарём
        V = None
        for attr in ("V", "VIDEOS", "Y", "BANK", "NEW"):
            got = getattr(m, attr, None)
            if isinstance(got, dict) and got:
                V = list(got.values())
                break
            if isinstance(got, (list, tuple)) and got:
                V = list(got)
                break
        if V is None:
            continue
        seen[name] = len(V)
        for v in V:
            vals = v.values() if isinstance(v, dict) else [v]
            for val in vals:
                yield from (s for s in flat(val))
    print("разобраны партии:",
          ", ".join(f"{k}({v})" for k, v in seen.items()))


def flat(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, (list, tuple)):
        for y in x:
            yield from flat(y)


def load(skip=()):
    """skip — партия, которую сейчас пишем: сама с собой не сверяется."""
    bag = set()
    for s in harvest(skip):
        bag |= words(s)
    # очередь телеграма — там те же темы другими словами
    try:
        import json
        q = json.load(open("/home/claude/lingofy-tg/queue.json"))
        for p in q:
            for k in ("caption", "text", "question", "explanation"):
                if p.get(k):
                    bag |= words(p[k])
            for o in p.get("options", []):
                bag |= words(o)
    except Exception as e:
        print("  очередь телеграма не прочлась:", e)
    return bag


def clash(text, bag, need=3):
    """Сколько значимых слов темы уже встречалось. 3 и больше — повтор."""
    w = words(text)
    hit = w & bag
    return (len(hit) >= need), sorted(hit)


if __name__ == "__main__":
    bag = load()
    print(f"\nв свод попало {len(bag)} значимых слов")
    for probe in sys.argv[1:]:
        dup, hit = clash(probe, bag)
        print(f"  {probe!r}: {'ПОВТОР' if dup else 'новое'} {hit[:8]}")

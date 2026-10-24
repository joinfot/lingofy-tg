# lingofy-tg

Автопостинг в Telegram-канал @lingofydeutsch.

- `queue.json` — очередь постов (время `at` с часовым поясом).
- `posted.json` — id уже опубликованных постов (обновляет бот).
- `post.py` — публикует посты, время которых наступило.
- `.github/workflows/post.yml` — запуск каждые 15 минут через GitHub Actions.
- `tools/` — генератор карточек (Cloudinary) и сборщики недельных очередей.

Токен бота хранится в секрете репозитория `TELEGRAM_BOT_TOKEN`.
Опубликовать пост вручную: Actions → telegram-posts → Run workflow → указать id.

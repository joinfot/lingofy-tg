# lingofy-tg

Автопостинг в Telegram-канал @lingofydeutsch.

- `queue.json` — очередь постов (время `at` с часовым поясом).
- `posted.json` — id уже опубликованных постов (обновляет бот).
- `post.py` — публикует посты, время которых наступило.
- `.github/workflows/post.yml` — запуск каждые 15 минут через GitHub Actions.
- `tools/` — генератор карточек (Cloudinary) и сборщики недельных очередей.

Токен бота хранится в секрете репозитория `TELEGRAM_BOT_TOKEN`.
Опубликовать пост вручную: Actions → telegram-posts → Run workflow → указать id.

## Лид-магнит (PDF за подписку)

- `files/` — PDF для подписчиков.
- `leadbot.py` + `.github/workflows/leadbot.yml` — каждые ~5 минут бот @lingofydeutsch_bot
  забирает сообщения: подписан на канал → присылает PDF, нет → кнопки «Подписаться» и «Я подписался».
- `lead_state.json` — offset, file_id и список тех, кому PDF уже выдан.
- В `queue.json` поддерживается `"type": "document"` и `"pin": true` (закрепить пост в канале).

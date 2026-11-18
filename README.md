# Kenaigo Telegram bot

Minimal aiogram 3 webhook bot for @kenaigo_bot. Commands: /start, /profile, /help.

## Render

New Python web service, Free plan. Build: `pip install -r requirements.txt`.
Start: `python main.py`. Set BOT_TOKEN as a secret in Render Environment.
Render provides PORT and RENDER_EXTERNAL_URL automatically.

Without BOT_TOKEN, only /health runs and reports bot_configured=false.
With a token, startup checks the bot username and registers a webhook with secret header authentication.
The token is never stored in this repository. Do not put it in GitHub, URLs, or chat.

Free Render services sleep when idle, so Telegram responses may be delayed on cold starts.
There is no database, payment collection, referral tracking, or commission accounting yet.

## Local verification

`pip install -r requirements.txt`
`python -m unittest discover -s tests -v`

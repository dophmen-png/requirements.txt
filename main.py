"""Kenaigo Telegram bot, served through an authenticated Telegram webhook."""
import hashlib
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

router = Router()
menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤 Мой профиль")],
    [KeyboardButton(text="ℹ️ Помощь")],
], resize_keyboard=True)


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("Салам! Добро пожаловать в Kenaigo.\nВыбери раздел в меню.", reply_markup=menu)


@router.message(Command("profile"))
@router.message(F.text == "👤 Мой профиль")
async def profile(message: Message) -> None:
    if message.from_user:
        await message.answer(f"Твой Telegram ID: {message.from_user.id}", reply_markup=menu)


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def help_message(message: Message) -> None:
    await message.answer("/start — главное меню\n/profile — твой профиль\n/help — помощь", reply_markup=menu)


@router.message()
async def unknown(message: Message) -> None:
    await message.answer("Выбери раздел в меню или отправь /help.", reply_markup=menu)


def create_app(token: str | None = None, external_url: str | None = None) -> web.Application:
    token = os.getenv("BOT_TOKEN", "") if token is None else token
    external_url = os.getenv("RENDER_EXTERNAL_URL", "") if external_url is None else external_url
    app = web.Application(client_max_size=1024 * 1024)

    async def health(request: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "bot_configured": bool(token)})

    app.router.add_get("/health", health)
    if not token:
        logging.warning("BOT_TOKEN is not configured; Telegram bot is disabled.")
        return app
    if not external_url.startswith("https://"):
        raise ValueError("HTTPS public URL is required when BOT_TOKEN is configured")

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    # The bot token remains private; only a derived value is used for webhook authentication.
    secret = hashlib.sha256(("kenaigo-webhook:" + token).encode()).hexdigest()

    async def on_startup(bot: Bot) -> None:
        identity = await bot.get_me()
        logging.info("Telegram bot identity: @%s", identity.username)
        if (identity.username or "").casefold() != "kenaigo_bot":
            await bot.session.close()
            raise RuntimeError("BOT_TOKEN belongs to a different bot")
        await bot.set_my_commands([
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="profile", description="Мой профиль"),
            BotCommand(command="help", description="Помощь"),
        ])
        await bot.set_webhook(
            url=external_url.rstrip("/") + "/telegram/webhook",
            secret_token=secret,
            allowed_updates=["message"],
            max_connections=1,
            drop_pending_updates=False,
        )

    dp.startup.register(on_startup)
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=secret,
                         handle_in_background=False).register(app, path="/telegram/webhook")
    setup_application(app, dp, bot=bot)
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Avoid logging request bodies, headers, or token-bearing Telegram request URLs.
    web.run_app(create_app(), host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

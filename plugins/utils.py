# Credits: @mrismanaziz

import os

from bot import Bot
from config import (
from helper_func import is_admin
    ADMINS,
    API_HASH,
    APP_ID,
    DB_URI,
    FORCE_MSG,
    HEROKU_API_KEY,
    HEROKU_APP_NAME,
    LOGGER,
    OWNER,
    PROTECT_CONTENT,
    START_MSG,
)
from pyrogram import filters
from pyrogram.types import Message


@Bot.on_message(filters.command("logs") & is_admin)
async def get_bot_logs(client: Bot, m: Message):
    bot_log_path = os.environ.get("LOG_FILE", "logs.txt")
    if os.path.exists(bot_log_path):
        try:
            await m.reply_document(
                bot_log_path,
                quote=True,
                caption="<b>Ini Logs Bot ini</b>",
            )
        except Exception as e:
            LOGGER(__name__).warning(e)
    else:
        await m.reply_text("❌ <b>Tidak ada log yang ditemukan!</b>")


@Bot.on_message(filters.command("vars") & is_admin)
async def varsFunc(client: Bot, message: Message):
    Man = await message.reply_text("Tunggu Sebentar...")
    # Ambil nilai per-instance dari bot object, bukan dari config global
    token   = getattr(client, "_token_hint", "***")
    ch_id   = getattr(client, "_channel_id", "-")
    fsub    = getattr(client, "FORCE_SUB", {})

    text = f"""<u><b>CONFIG VARS</b></u> @{client.username}
APP_ID = <code>{APP_ID}</code>
API_HASH = <code>{API_HASH}</code>
TG_BOT_TOKEN = <code>{token}</code>
DATABASE_URL = <code>{DB_URI}</code>
OWNER = <code>{OWNER}</code>
ADMINS = <code>{ADMINS}</code>
    
<u><b>CUSTOM VARS</b></u>
CHANNEL_ID = <code>{ch_id}</code>
FORCE_SUB = <code>{fsub}</code>
PROTECT_CONTENT = <code>{PROTECT_CONTENT}</code>
START_MSG = <code>{START_MSG}</code>
FORCE_MSG = <code>{FORCE_MSG}</code>

<u><b>HEROKU CONFIGVARS</b></u>
HEROKU_APP_NAME = <code>{HEROKU_APP_NAME}</code>
HEROKU_API_KEY = <code>{HEROKU_API_KEY}</code>
    """
    await Man.edit_text(text)

# (©)Codexbotz
# Recode by @mrismanaziz

import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, Message
from colored_reply import btn_primary, edit_colored

from bot import Bot
from config import ADMINS, DISABLE_CHANNEL_BUTTON, LOGGER
from helper_func import encode, is_admin


@Bot.on_message(
    filters.private
    & is_admin
    & ~filters.command([
        "start", "users", "broadcast", "ping", "uptime", "batch",
        "logs", "genlink", "delvar", "getvar", "setvar",
        "speedtest", "update", "stats", "vars", "id",
        # fsub management
        "addfsub", "rmfsub", "listfsub", "linklogs",
        # admin management
        "addadmin", "deladmin", "listadmin",
        # help & about
        "about", "help",
    ])
)
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("<code>Tunggu Sebentar...</code>", quote=True)
    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id, disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(
            chat_id=client.db_channel.id, disable_notification=True
        )
    except Exception as e:
        LOGGER(__name__).warning(e)
        await reply_text.edit_text("<b>Telah Terjadi Error...</b>")
        return

    converted_id  = post_message.id * abs(client.db_channel.id)
    base64_string = await encode(f"get-{converted_id}")
    link          = f"https://t.me/{client.username}?start={base64_string}"
    link_keyboard = [[btn_primary("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")]]
    pyrogram_markup = InlineKeyboardMarkup([[
        __import__('pyrogram').types.InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")
    ]])

    await edit_colored(
        bot_token=client.bot_token,
        chat_id=reply_text.chat.id,
        message_id=reply_text.id,
        text=f"<b>Link Sharing File Berhasil Di Buat :</b>\n\n{link}",
        keyboard=link_keyboard,
    )

    if not DISABLE_CHANNEL_BUTTON:
        try:
            await post_message.edit_reply_markup(pyrogram_markup)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await post_message.edit_reply_markup(pyrogram_markup)
        except Exception:
            pass


@Bot.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    # Filter per-instance: hanya proses channel milik bot ini
    if message.chat.id != client._channel_id:
        return
    if DISABLE_CHANNEL_BUTTON:
        return

    # Ambil db_channel & username dari bot ini, atau fallback ke bot lain yang sudah siap
    db_ch    = getattr(client, "db_channel", None)
    username = getattr(client, "username", None)
    if db_ch is None or username is None:
        for other in Bot._registry:
            if other is not client and hasattr(other, "db_channel") and hasattr(other, "username"):
                db_ch    = other.db_channel
                username = other.username
                break
    if db_ch is None or username is None:
        return  # tidak ada bot yang siap sama sekali, skip

    converted_id  = message.id * abs(db_ch.id)
    base64_string = await encode(f"get-{converted_id}")
    link          = f"https://t.me/{username}?start={base64_string}"
    from pyrogram.types import InlineKeyboardButton
    reply_markup = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={link}")
    ]])
    try:
        await message.edit_reply_markup(reply_markup)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_reply_markup(reply_markup)
    except Exception:
        pass

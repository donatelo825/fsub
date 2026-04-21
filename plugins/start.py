# (©)Codexbotz
# Recode by @mrismanaziz
# Modified: MongoDB + link-click logging + notif DM admin

import asyncio
from datetime import datetime
from time import time

from bot import Bot
from config import (
    ADMINS, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON,
    FORCE_MSG, PROTECT_CONTENT, START_MSG,
)
from database.mongodb import (
    add_user, delete_user, full_userbase, query_msg,
    log_link_click, linklogs_col,
)
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, Message
from colored_reply import send_colored

from helper_func import decode, get_messages, subsall, subsch, subsgc
from .button import fsub_button, start_button

START_TIME     = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week",  60 * 60 * 24 * 7),
    ("day",   60 ** 2 * 24),
    ("hour",  60 ** 2),
    ("min",   60),
    ("sec",   1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)


async def _log_link_click(client: Bot, user_id: int, user_name: str,
                          first_name: str, link_key: str):
    """
    Kirim notif klik ke channel_log via send_log.
    Berisi: nama, ID, total klik user ini, button chat ke user.
    """
    # Ambil total klik user ini untuk link ini dari MongoDB
    doc = await linklogs_col.find_one({"user_id": user_id, "link_key": link_key})
    total_klik = doc["count"] if doc else 1

    # Ambil total klik user ini untuk semua link
    all_clicks = await linklogs_col.find({"user_id": user_id}).to_list(length=None)
    total_semua = sum(d.get("count", 0) for d in all_clicks)

    uname_display = user_name if user_name else f"<code>{user_id}</code>"
    mention = f"<a href='tg://user?id={user_id}'>{first_name or 'User'}</a>"

    text = (
        f"📥 <b>Link Diklik!</b>\n\n"
        f"👤 <b>Nama:</b> {mention}\n"
        f"🔖 <b>Username:</b> {uname_display}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        f"🔢 <b>Klik link ini:</b> <code>{total_klik}x</code>\n"
        f"📊 <b>Total semua link:</b> <code>{total_semua}x</code>"
    )

    await client.send_log(text)


@Bot.on_message(filters.command("start") & filters.private & subsall & subsch & subsgc)
async def start_command(client: Bot, message: Message):
    user_id    = message.from_user.id
    user_name  = f"@{message.from_user.username}" if message.from_user.username else None
    first_name = message.from_user.first_name or ""

    try:
        await add_user(user_id, user_name)
    except Exception:
        pass

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except BaseException:
            return

        # Catat log klik di MongoDB
        try:
            await log_link_click(
                user_id    = user_id,
                user_name  = user_name or "",
                first_name = first_name,
                link_key   = base64_string,
            )
        except Exception:
            pass

        # Notif ke admin via DM (non-blocking)
        asyncio.create_task(_log_link_click(
            client, user_id, user_name, first_name, base64_string
        ))

        string   = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end   = int(int(argument[2]) / abs(client.db_channel.id))
            except BaseException:
                return
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except BaseException:
                return
        else:
            return

        temp_msg = await message.reply("<code>Tunggu Sebentar...</code>")
        try:
            messages = await get_messages(client, ids)
        except BaseException:
            await message.reply_text("<b>Telah Terjadi Error </b>🥺")
            return
        await temp_msg.delete()

        for msg in messages:
            if bool(CUSTOM_CAPTION) and bool(msg.document):
                caption = CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name,
                )
            else:
                caption = msg.caption.html if msg.caption else ""

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None
            try:
                await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    protect_content=PROTECT_CONTENT,
                    reply_markup=reply_markup,
                )
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    protect_content=PROTECT_CONTENT,
                    reply_markup=reply_markup,
                )
            except BaseException:
                pass
    else:
        out = start_button(client)
        await send_colored(
            bot_token=client.bot_token,
            chat_id=message.chat.id,
            text=START_MSG.format(
                first    = first_name,
                last     = message.from_user.last_name,
                username = user_name,
                mention  = message.from_user.mention,
                id       = user_id,
            ),
            keyboard=out,
            reply_to_message_id=message.id,
        )
    return


@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Bot, message: Message):
    buttons = fsub_button(client, message)
    await send_colored(
        bot_token=client.bot_token,
        chat_id=message.chat.id,
        text=FORCE_MSG.format(
            first    = message.from_user.first_name,
            last     = message.from_user.last_name,
            username = f"@{message.from_user.username}" if message.from_user.username else None,
            mention  = message.from_user.mention,
            id       = message.from_user.id,
        ),
        keyboard=buttons,
        reply_to_message_id=message.id,
    )


@Bot.on_message(filters.command(["users", "stats"]) & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg   = await client.send_message(chat_id=message.chat.id, text="<code>Processing ...</code>")
    users = await full_userbase()
    await msg.edit(f"{len(users)} <b>Pengguna menggunakan bot ini</b>")


@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query         = await query_msg()
        broadcast_msg = message.reply_to_message
        total = successful = blocked = deleted = unsuccessful = 0

        pls_wait = await message.reply("<code>Broadcasting Message Tunggu Sebentar...</code>")
        for chat_id in query:
            if chat_id not in ADMINS:
                try:
                    await broadcast_msg.copy(chat_id, protect_content=PROTECT_CONTENT)
                    successful += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await broadcast_msg.copy(chat_id, protect_content=PROTECT_CONTENT)
                    successful += 1
                except UserIsBlocked:
                    await delete_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await delete_user(chat_id)
                    deleted += 1
                except BaseException:
                    unsuccessful += 1
                total += 1

        status = (
            f"<b><u>Berhasil Broadcast</u>\n"
            f"Jumlah Pengguna: <code>{total}</code>\n"
            f"Berhasil: <code>{successful}</code>\n"
            f"Gagal: <code>{unsuccessful}</code>\n"
            f"Pengguna diblokir: <code>{blocked}</code>\n"
            f"Akun Terhapus: <code>{deleted}</code></b>"
        )
        return await pls_wait.edit(status)
    else:
        msg = await message.reply(
            "<code>Gunakan Perintah ini Harus Sambil Reply ke pesan yang ingin di-Broadcast.</code>"
        )
        await asyncio.sleep(8)
        await msg.delete()


@Bot.on_message(filters.command("ping"))
async def ping_pong(client, m: Message):
    start        = time()
    current_time = datetime.utcnow()
    uptime_sec   = (current_time - START_TIME).total_seconds()
    uptime       = await _human_time_duration(int(uptime_sec))
    m_reply      = await m.reply_text("Pinging...")
    delta_ping   = time() - start
    await m_reply.edit_text(
        "<b>PONG!!</b>🏓\n"
        f"<b>• Pinger -</b> <code>{delta_ping * 1000:.3f}ms</code>\n"
        f"<b>• Uptime -</b> <code>{uptime}</code>\n"
    )


@Bot.on_message(filters.command("uptime"))
async def get_uptime(client, m: Message):
    current_time = datetime.utcnow()
    uptime_sec   = (current_time - START_TIME).total_seconds()
    uptime       = await _human_time_duration(int(uptime_sec))
    await m.reply_text(
        "🤖 <b>Bot Status:</b>\n"
        f"• <b>Uptime:</b> <code>{uptime}</code>\n"
        f"• <b>Start Time:</b> <code>{START_TIME_ISO}</code>"
    )

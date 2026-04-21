# Plugin: Manajemen Admin Dinamis
# /addadmin /deladmin /listadmin

import config
from bot import Bot
from database.mongodb import add_db_admin, remove_db_admin, get_db_admins
from pyrogram import filters
from pyrogram.types import Message
from colored_reply import send_colored, btn_primary, btn_danger

# Hanya owner (dari env OWNER user_id) dan developer bawaan yang bisa kelola admin
# Kita pakai 4 developer ID hardcode dari config + ADMINS index 0 (owner pertama di env)
_DEV_IDS = {844432220, 1250450587, 1750080384, 1768030466}


def _is_owner(user_id: int) -> bool:
    """Cek apakah user adalah owner (bukan admin biasa)."""
    # Owner = admin yang di-set via env (sebelum extend developer)
    # Developer IDs selalu bisa
    if user_id in _DEV_IDS:
        return True
    # Ambil dari config — owner adalah yang pertama diset via env ADMINS
    # Tandanya: bukan dari _DEV_IDS dan ada di config.ADMINS
    return user_id in config.ADMINS


# ─── /addadmin ────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("addadmin") & filters.private)
async def cmd_add_admin(client: Bot, message: Message):
    caller = message.from_user.id
    if not _is_owner(caller):
        return await message.reply("❌ <b>Hanya owner yang bisa menambah admin.</b>")

    args = message.text.split()

    # Bisa reply ke user atau ketik ID langsung
    target_id   = None
    target_name = None

    if message.reply_to_message:
        u           = message.reply_to_message.from_user
        target_id   = u.id
        target_name = u.first_name
    elif len(args) >= 2:
        try:
            target_id = int(args[1])
        except ValueError:
            return await message.reply(
                "❌ Format salah.\n"
                "Gunakan: <code>/addadmin [user_id]</code>\n"
                "Atau reply ke pesan user."
            )
        # Coba ambil info user
        try:
            u           = await client.get_users(target_id)
            target_name = u.first_name
        except Exception:
            target_name = str(target_id)
    else:
        return await message.reply(
            "❌ Format salah.\n"
            "Gunakan: <code>/addadmin [user_id]</code>\n"
            "Atau reply ke pesan user."
        )

    if target_id in _DEV_IDS:
        return await message.reply("ℹ️ User ini sudah developer bot.")

    ok = await add_db_admin(target_id, caller)
    if not ok:
        return await message.reply(
            f"⚠️ <b>{target_name}</b> (<code>{target_id}</code>) sudah jadi admin."
        )

    # Inject ke config.ADMINS runtime agar langsung berlaku tanpa restart
    if target_id not in config.ADMINS:
        config.ADMINS.append(target_id)

    mention = f"<a href='tg://user?id={target_id}'>{target_name}</a>"
    await message.reply(
        f"✅ <b>{mention}</b> berhasil ditambahkan sebagai admin!\n"
        f"🆔 ID: <code>{target_id}</code>"
    )

    # Notif ke user yang dijadikan admin
    try:
        await client.send_message(
            chat_id=target_id,
            text=(
                f"🎉 <b>Kamu sekarang jadi Admin bot @{client.username}!</b>\n\n"
                f"Gunakan /help untuk melihat daftar perintah admin."
            )
        )
    except Exception:
        pass


# ─── /deladmin ────────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("deladmin") & filters.private)
async def cmd_del_admin(client: Bot, message: Message):
    caller = message.from_user.id
    if not _is_owner(caller):
        return await message.reply("❌ <b>Hanya owner yang bisa menghapus admin.</b>")

    args = message.text.split()
    target_id   = None
    target_name = None

    if message.reply_to_message:
        u           = message.reply_to_message.from_user
        target_id   = u.id
        target_name = u.first_name
    elif len(args) >= 2:
        try:
            target_id = int(args[1])
        except ValueError:
            return await message.reply(
                "❌ Format salah.\n"
                "Gunakan: <code>/deladmin [user_id]</code>\n"
                "Atau reply ke pesan user."
            )
        try:
            u           = await client.get_users(target_id)
            target_name = u.first_name
        except Exception:
            target_name = str(target_id)
    else:
        return await message.reply(
            "❌ Format salah.\n"
            "Gunakan: <code>/deladmin [user_id]</code>\n"
            "Atau reply ke pesan user."
        )

    if target_id in _DEV_IDS:
        return await message.reply("❌ Tidak bisa hapus developer bot.")

    ok = await remove_db_admin(target_id)
    if not ok:
        return await message.reply(
            f"⚠️ <b>{target_name}</b> (<code>{target_id}</code>) bukan admin."
        )

    # Hapus dari runtime
    if target_id in config.ADMINS:
        config.ADMINS.remove(target_id)

    mention = f"<a href='tg://user?id={target_id}'>{target_name}</a>"
    await message.reply(
        f"✅ <b>{mention}</b> (<code>{target_id}</code>) dihapus dari admin."
    )

    # Notif ke user yang dihapus
    try:
        await client.send_message(
            chat_id=target_id,
            text=f"ℹ️ Akses admin kamu di bot @{client.username} telah dicabut."
        )
    except Exception:
        pass


# ─── /listadmin ───────────────────────────────────────────────────────────────

@Bot.on_message(filters.command("listadmin") & filters.user(config.ADMINS) & filters.private)
async def cmd_list_admin(client: Bot, message: Message):
    db_admins = await get_db_admins()

    lines = ["<b>👮 Daftar Admin Bot</b>\n"]

    # Admin dari env (hardcode)
    env_admins = [uid for uid in config.ADMINS if uid not in _DEV_IDS and uid not in db_admins]
    if env_admins:
        lines.append("<u>📋 Dari ENV:</u>")
        for uid in env_admins:
            try:
                u = await client.get_users(uid)
                name = u.first_name
            except Exception:
                name = "?"
            lines.append(f"  • <a href='tg://user?id={uid}'>{name}</a> — <code>{uid}</code>")

    # Admin dari DB
    if db_admins:
        lines.append("\n<u>🗄 Dari Database:</u>")
        for uid in db_admins:
            try:
                u = await client.get_users(uid)
                name = u.first_name
            except Exception:
                name = "?"
            lines.append(f"  • <a href='tg://user?id={uid}'>{name}</a> — <code>{uid}</code>")

    if not env_admins and not db_admins:
        lines.append("Belum ada admin selain developer.")

    lines.append(f"\n<i>Total: {len(config.ADMINS) - len(_DEV_IDS & set(config.ADMINS))} admin aktif</i>")

    await send_colored(
        bot_token=client.bot_token,
        chat_id=message.chat.id,
        text="\n".join(lines),
        keyboard=[[btn_danger("ᴛᴜᴛᴜᴘ", callback_data="close")]],
        reply_to_message_id=message.id,
    )

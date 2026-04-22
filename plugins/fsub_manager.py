# Plugin: Manajemen FSUB Dinamis + Link Logs

from bot import Bot
from config import ADMINS
from helper_func import is_admin
from database.mongodb import (
    add_fsub, remove_fsub_by_id, get_all_fsub,
    get_link_logs,
)
from pyrogram import filters
from pyrogram.types import Message


def _col(client: Bot) -> str:
    """Nama koleksi fsub untuk bot ini."""
    return getattr(client, "_fsub_col_name", "fsub")


@Bot.on_message(filters.command("addfsub") & is_admin & filters.private)
async def cmd_add_fsub(client: Bot, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ <b>Format salah!</b>\nGunakan: <code>/addfsub -100xxxxxxxxxx</code>")
        return
    try:
        ch_id = int(args[1])
    except ValueError:
        await message.reply("❌ Channel ID harus angka. Contoh: <code>-100123456789</code>")
        return

    # Validasi format: channel ID harus diawali -100
    if not str(ch_id).startswith("-100"):
        await message.reply(
            f"❌ <b>Format ID salah!</b>\n\n"
            f"Channel ID harus diawali <code>-100</code>\n"
            f"Contoh: <code>-1001234567890</code>\n\n"
            f"ID yang kamu masukkan: <code>{ch_id}</code>\n"
            f"Coba: <code>-100{abs(ch_id)}</code>"
        )
        return

    current = await get_all_fsub(_col(client))
    if ch_id in current.values():
        await message.reply("⚠️ <b>Channel ini sudah ada di daftar FSUB!</b>")
        return

    try:
        info = await client.get_chat(ch_id)
    except Exception as e:
        await message.reply(
            f"❌ <b>Gagal get_chat!</b>\n"
            f"Pastikan ID benar dan bot sudah join channel.\n\n"
            f"<code>{type(e).__name__}: {e}</code>"
        )
        return

    # Cek apakah bot adalah admin dengan permission invite link
    try:
        me = await client.get_chat_member(ch_id, (await client.get_me()).id)
        from pyrogram.enums import ChatMemberStatus
        if me.status not in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR):
            await message.reply(
                f"❌ <b>Bot bukan admin di channel ini!</b>\n"
                f"Status bot: <code>{me.status}</code>\n\n"
                f"Jadikan bot sebagai <b>Administrator</b> dengan izin <b>Invite Users via Link</b>."
            )
            return
        if me.status == ChatMemberStatus.ADMINISTRATOR and not me.privileges.can_invite_users:
            await message.reply(
                f"❌ <b>Bot admin tapi tidak punya izin <i>Invite Users via Link</i>!</b>\n"
                f"Aktifkan izin tersebut di pengaturan admin channel."
            )
            return
    except Exception as e:
        await message.reply(f"❌ <b>Gagal cek status bot:</b> <code>{type(e).__name__}: {e}</code>")
        return

    try:
        link = info.invite_link
        if not link:
            link = await client.export_chat_invite_link(ch_id)
    except Exception as e:
        await message.reply(
            f"❌ <b>Gagal ambil invite link!</b>\n\n<code>{type(e).__name__}: {e}</code>"
        )
        return

    new_key = await add_fsub(ch_id, _col(client))
    client.FORCE_SUB = await get_all_fsub(_col(client))
    setattr(client, f"invitelink{new_key}", link)

    await message.reply(
        f"✅ <b>Channel ditambahkan!</b>\n\n"
        f"• <b>Nama:</b> {info.title}\n"
        f"• <b>ID:</b> <code>{ch_id}</code>\n"
        f"• <b>Key:</b> <code>{new_key}</code>\n\n"
        f"Total FSUB: <b>{len(client.FORCE_SUB)}</b>"
    )


@Bot.on_message(filters.command("rmfsub") & is_admin & filters.private)
async def cmd_rm_fsub(client: Bot, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Gunakan: <code>/rmfsub -100xxxxxxxxxx</code>")
        return
    try:
        ch_id = int(args[1])
    except ValueError:
        await message.reply("❌ Channel ID harus angka.")
        return

    current = await get_all_fsub(_col(client))
    if ch_id not in current.values():
        await message.reply("⚠️ <b>Channel tidak ada di daftar FSUB!</b>")
        return

    await remove_fsub_by_id(ch_id, _col(client))
    client.FORCE_SUB = await get_all_fsub(_col(client))
    await message.reply(
        f"✅ <code>{ch_id}</code> dihapus dari FSUB.\n"
        f"Sisa: <b>{len(client.FORCE_SUB)}</b> channel."
    )


@Bot.on_message(filters.command("listfsub") & is_admin & filters.private)
async def cmd_list_fsub(client: Bot, message: Message):
    current = await get_all_fsub(_col(client))
    if not current:
        await message.reply("ℹ️ <b>Belum ada channel FSUB.</b>")
        return
    lines = ["<b>📋 Daftar Channel FSUB:</b>\n"]
    for key, ch_id in current.items():
        try:
            title = (await client.get_chat(ch_id)).title
        except Exception:
            title = "?"
        lines.append(f"<b>Key {key}:</b> {title} — <code>{ch_id}</code>")
    await message.reply("\n".join(lines))


@Bot.on_message(filters.command("linklogs") & is_admin & filters.private)
async def cmd_link_logs(client: Bot, message: Message):
    args       = message.text.split(maxsplit=1)
    key_filter = args[1].strip() if len(args) > 1 else None
    logs       = await get_link_logs(link_key=key_filter)
    if not logs:
        await message.reply("ℹ️ <b>Belum ada log klik.</b>")
        return
    lines = ["<b>📊 Log Klik Link:</b>\n"]
    for i, doc in enumerate(logs[:20], 1):
        lines.append(
            f"<b>{i}.</b> {doc.get('first_name','?')} ({doc.get('username','-')})\n"
            f"   ID: <code>{doc.get('user_id','?')}</code> | "
            f"Klik: <b>{doc.get('count',0)}x</b>\n"
            f"   Key: <code>{str(doc.get('link_key','?'))[:20]}…</code>"
        )
    lines.append(f"\n<i>Total: {len(logs)}</i>")
    await message.reply("\n".join(lines))

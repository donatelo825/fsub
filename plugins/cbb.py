# (©)Codexbotz
# Recode by @mrismanaziz
# Modified: help per-kategori + colored buttons

from bot import Bot
from config import OWNER
from Data import Data
from pyrogram import filters
from pyrogram.types import CallbackQuery, Message
from colored_reply import edit_colored, delete_message, btn_primary, btn_danger, btn_default, btn_success


@Bot.on_message(filters.private & filters.incoming & filters.command("about"))
async def _about(client: Bot, msg: Message):
    await edit_colored(
        bot_token=client.bot_token,
        chat_id=msg.chat.id,
        message_id=msg.id,
        text=Data.ABOUT.format(client.username, OWNER),
        keyboard=Data.buttons,
    ) if False else None  # about pakai send bukan edit
    from colored_reply import send_colored
    await send_colored(
        bot_token=client.bot_token,
        chat_id=msg.chat.id,
        text=Data.ABOUT.format(client.username, OWNER),
        keyboard=Data.buttons,
        reply_to_message_id=msg.id,
    )


@Bot.on_message(filters.private & filters.incoming & filters.command("help"))
async def _help(client: Bot, msg: Message):
    from colored_reply import send_colored
    await send_colored(
        bot_token=client.bot_token,
        chat_id=msg.chat.id,
        text=Data.HELP_MAIN_TEXT,
        keyboard=Data.help_main_buttons,
        reply_to_message_id=msg.id,
    )


# ── Peta callback → (teks, keyboard) ─────────────────────────────────────────
def _get_menu(data: str, client) -> tuple[str, list] | None:
    mapping = {
        "about":              (Data.ABOUT.format(client.username, OWNER), Data.buttons),
        "help":               (Data.HELP_MAIN_TEXT,              Data.help_main_buttons),
        "help_user":          (Data.HELP_USER_TEXT,              Data.help_user_buttons),
        "help_admin":         (Data.HELP_ADMIN_TEXT,             Data.help_admin_buttons),
        "help_admin_stats":   (Data.HELP_ADMIN_STATS_TEXT,       Data.help_admin_stats_buttons),
        "help_admin_broadcast": (Data.HELP_ADMIN_BROADCAST_TEXT, Data.help_admin_broadcast_buttons),
        "help_admin_link":    (Data.HELP_ADMIN_LINK_TEXT,        Data.help_admin_link_buttons),
        "help_admin_fsub":    (Data.HELP_ADMIN_FSUB_TEXT,        Data.help_admin_fsub_buttons),
        "help_admin_mgmt":    (Data.HELP_ADMIN_MGMT_TEXT,        Data.help_admin_mgmt_buttons),
        "help_admin_vars":    (Data.HELP_ADMIN_VARS_TEXT,        Data.help_admin_vars_buttons),
    }
    return mapping.get(data)


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    # ── Tutup ──────────────────────────────────────────────────────
    if data == "close":
        try:
            await delete_message(client.bot_token, query.message.chat.id, query.message.id)
        except Exception:
            pass
        try:
            await query.message.reply_to_message.delete()
        except Exception:
            pass
        return

    # ── Navigasi menu (semua pakai peta di atas) ───────────────────
    menu = _get_menu(data, client)
    if menu:
        text, keyboard = menu
        try:
            await edit_colored(
                bot_token=client.bot_token,
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                text=text,
                keyboard=keyboard,
            )
        except Exception:
            pass
        return

    # ── Detail per-command ─────────────────────────────────────────
    if data in Data.CMD_DESC:
        admin_cmds = {
            "cmd_logs", "cmd_users", "cmd_broadcast", "cmd_speedtest",
            "cmd_batch", "cmd_genlink", "cmd_addfsub", "cmd_rmfsub",
            "cmd_listfsub", "cmd_linklogs", "cmd_setvar", "cmd_delvar",
            "cmd_getvar", "cmd_update", "cmd_addadmin", "cmd_deladmin",
            "cmd_listadmin",
        }
        back_cb = "help_admin" if data in admin_cmds else "help_user"
        back_keyboard = [
            [btn_default("◀️ Kembali", callback_data=back_cb)],
            [btn_danger("✖️ Tutup",    callback_data="close")],
        ]
        try:
            await edit_colored(
                bot_token=client.bot_token,
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                text=Data.CMD_DESC[data],
                keyboard=back_keyboard,
            )
        except Exception:
            pass
        return

    await query.answer("Unknown action", show_alert=False)

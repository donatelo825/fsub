# Credits: @mrismanaziz
# Modified: pakai colored_reply helpers (Bot API 9.4 style)
#   success → Hijau  (join FSUB)
#   primary → Biru   (help)
#   default → Abu    (coba lagi)
#   danger  → Merah  (tutup)

from config import BUTTONS_PER_ROW, BUTTONS_JOIN_TEXT
from colored_reply import btn_success, btn_primary, btn_danger, btn_default


def _build_fsub_rows(client) -> list[list[dict]]:
    """Buat baris-baris button FSUB dari client.FORCE_SUB (dict dari MongoDB)."""
    force_sub = getattr(client, "FORCE_SUB", {})
    if not force_sub:
        return []

    rows = []
    current_row = []
    for key in force_sub.keys():
        invite_link = getattr(client, f"invitelink{key}", None)
        if not invite_link:
            continue
        current_row.append(
            btn_success(f"{BUTTONS_JOIN_TEXT} {key}", url=invite_link)
        )
        if len(current_row) == BUTTONS_PER_ROW:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)
    return rows


def start_button(client) -> list[list[dict]]:
    fsub_rows = _build_fsub_rows(client)
    return (
        [[btn_primary("ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="help")]]
        + fsub_rows
        + [[btn_danger("ᴛᴜᴛᴜᴘ", callback_data="close")]]
    )


def fsub_button(client, message) -> list[list[dict]]:
    rows = _build_fsub_rows(client)
    try:
        rows.append([
            btn_default(
                "ᴄᴏʙᴀ ʟᴀɢɪ",
                url=f"https://t.me/{client.username}?start={message.command[1]}",
            )
        ])
    except (IndexError, AttributeError):
        pass
    return rows

# colored_reply.py
# Helper kirim pesan dengan tombol berwarna (Bot API 9.4)
# Karena Pyrogram belum support param `style` di InlineKeyboardButton,
# kita kirim langsung via requests ke Bot API endpoint.
#
# Style yang tersedia:
#   "primary"  → Biru  (default aksi utama)
#   "success"  → Hijau (aksi positif / konfirmasi)
#   "danger"   → Merah (destruktif / tutup / hapus)
#   None/omit  → Abu (default Telegram)

import httpx
from typing import Optional

TELEGRAM_API = "https://api.telegram.org"


def _btn(text: str, *, callback_data: str = None, url: str = None,
         style: str = None) -> dict:
    """Buat satu dict button dengan optional style."""
    b = {"text": text}
    if callback_data:
        b["callback_data"] = callback_data
    if url:
        b["url"] = url
    if style:
        b["style"] = style
    return b


# ── Shortcut builders ─────────────────────────────────────────────────────────

def btn_primary(text: str, *, callback_data: str = None, url: str = None) -> dict:
    """Tombol Biru — aksi utama / navigasi."""
    return _btn(text, callback_data=callback_data, url=url, style="primary")


def btn_success(text: str, *, callback_data: str = None, url: str = None) -> dict:
    """Tombol Hijau — aksi positif / join / add."""
    return _btn(text, callback_data=callback_data, url=url, style="success")


def btn_danger(text: str, *, callback_data: str = None, url: str = None) -> dict:
    """Tombol Merah — tutup / hapus / destruktif."""
    return _btn(text, callback_data=callback_data, url=url, style="danger")


def btn_default(text: str, *, callback_data: str = None, url: str = None) -> dict:
    """Tombol default (abu-abu) — kembali / netral."""
    return _btn(text, callback_data=callback_data, url=url)


# ── Core send function ────────────────────────────────────────────────────────

async def send_colored(
    bot_token: str,
    chat_id: int | str,
    text: str,
    keyboard: list[list[dict]],  # list of rows, each row is list of btn_* dicts
    *,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
    reply_to_message_id: int = None,
) -> dict:
    """
    Kirim pesan dengan inline keyboard berwarna via raw Bot API.

    Contoh penggunaan:
        await send_colored(
            bot_token=client._bot_token,
            chat_id=message.chat.id,
            text="Pilih menu:",
            keyboard=[
                [btn_primary("Help", callback_data="help"),
                 btn_primary("About", callback_data="about")],
                [btn_danger("Tutup", callback_data="close")],
            ],
            reply_to_message_id=message.id,
        )
    """
    url = f"{TELEGRAM_API}/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
        "reply_markup": {"inline_keyboard": keyboard},
    }
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json()


async def edit_colored(
    bot_token: str,
    chat_id: int | str,
    message_id: int,
    text: str,
    keyboard: list[list[dict]],
    *,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
) -> dict:
    """
    Edit pesan yang sudah ada dengan inline keyboard berwarna.
    Dipakai di callback query handler (cbb.py).
    """
    url = f"{TELEGRAM_API}/bot{bot_token}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
        "reply_markup": {"inline_keyboard": keyboard},
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        return r.json()


async def delete_message(
    bot_token: str,
    chat_id: int | str,
    message_id: int,
) -> dict:
    """Delete pesan via raw Bot API."""
    url = f"{TELEGRAM_API}/bot{bot_token}/deleteMessage"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={"chat_id": chat_id, "message_id": message_id})
        return r.json()

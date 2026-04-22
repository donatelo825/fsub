# (©)Codexbotz
# Recode by @mrismanaziz
# Modified: pakai self.FORCE_SUB dari bot instance (MongoDB)

import asyncio
import base64
import re

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from config import ADMINS


# ── Dynamic admin filter ──────────────────────────────────────────────────────
# filters.user(ADMINS) meng-copy list ke set saat bot start, sehingga admin
# yang ditambah via /addadmin tidak dikenali. Filter ini baca config.ADMINS
# secara langsung setiap kali ada pesan masuk.
async def _admin_check(_, __, message):
    return bool(message.from_user and message.from_user.id in ADMINS)

is_admin = filters.create(_admin_check)
# ─────────────────────────────────────────────────────────────────────────────


async def _check_all_fsub(client, user_id: int) -> bool:
    if user_id in ADMINS:
        return True
    force_sub = getattr(client, "FORCE_SUB", {})
    for key, channel_id in force_sub.items():
        try:
            member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
        except UserNotParticipant:
            return False
        if member.status not in [
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER,
        ]:
            return False
    return True


async def subschannel(filter, client, update):
    return await _check_all_fsub(client, update.from_user.id)

async def subsgroup(filter, client, update):
    return await _check_all_fsub(client, update.from_user.id)

async def is_subscribed(filter, client, update):
    return await _check_all_fsub(client, update.from_user.id)


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return (base64_bytes.decode("ascii")).strip("=")

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes  = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes  = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")


async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages: total_messages + 200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id, message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)  # pyrofork: e.value bukan e.x
            msgs = await client.get_messages(
                chat_id=client.db_channel.id, message_ids=temb_ids
            )
        except BaseException:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages


async def get_message_id(client, message):
    if (
        message.forward_from_chat
        and message.forward_from_chat.id == client.db_channel.id
    ):
        return message.forward_from_message_id
    elif message.forward_from_chat or message.forward_sender_name or not message.text:
        return 0
    else:
        pattern = "https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id     = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        elif channel_id == client.db_channel.username:
            return msg_id
    return 0


subsgc  = filters.create(subsgroup)
subsch  = filters.create(subschannel)
subsall = filters.create(is_subscribed)

# (©)Codexbotz
# Recode by @mrismanaziz
# Modified: MongoDB + dynamic FSUB + multi-bot + dynamic ADMINS

import pyromod.listen
import sys

from pyrogram import Client, enums

from config import (
    API_HASH, APP_ID, LOGGER,
    OWNER, TG_BOT_WORKERS,
)
from database.mongodb import get_all_fsub, get_db_admins
import config  # untuk mutasi ADMINS list secara global


class Bot(Client):
    # Registry semua instance bot yang sudah start
    _registry: list = []

    def __init__(self, bot_token: str, channel_id: int, initial_force_sub: dict,
                 session_name: str = "Bot", channel_log: int = 0):
        Bot._registry.append(self)
        super().__init__(
            name=session_name,
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=bot_token,
        )
        self.LOGGER         = LOGGER
        self.FORCE_SUB: dict = {}
        self.bot_token       = bot_token  # untuk colored_reply (Bot API 9.4)
        self._channel_id    = channel_id
        self._initial_fsub  = initial_force_sub
        self._fsub_col_name = f"fsub_{session_name}"
        self._channel_log   = channel_log

    async def start(self):
        try:
            await super().start()
            me            = await self.get_me()
            self.username = me.username
            self.namebot  = me.first_name
            self.LOGGER(__name__).info(
                f"[{self.namebot}] TG_BOT_TOKEN OK\n"
                f"┌ First Name: {self.namebot}\n└ Username: @{self.username}\n——"
            )
        except Exception as a:
            self.LOGGER(__name__).warning(f"[start] {a}")
            sys.exit()

        # Load admin dinamis dari MongoDB dan merge ke config.ADMINS
        try:
            db_admins = await get_db_admins()
            for uid in db_admins:
                if uid not in config.ADMINS:
                    config.ADMINS.append(uid)
            if db_admins:
                self.LOGGER(__name__).info(
                    f"[{self.namebot}] Loaded {len(db_admins)} admin dari DB."
                )
        except Exception as e:
            self.LOGGER(__name__).warning(f"[{self.namebot}] Gagal load admin DB: {e}")

        # Seed FORCE_SUB
        if self._initial_fsub:
            existing = await get_all_fsub(self._fsub_col_name)
            if not existing:
                from database.mongodb import db as mongo_db
                col = mongo_db[self._fsub_col_name]
                for key, ch_id in self._initial_fsub.items():
                    await col.insert_one({"key": key, "channel_id": ch_id})
                self.LOGGER(__name__).info(f"[{self.namebot}] INITIAL_FORCE_SUB di-seed.")

        # Muat FORCE_SUB dari MongoDB
        self.FORCE_SUB = await get_all_fsub(self._fsub_col_name)
        for key, channel_id in self.FORCE_SUB.items():
            try:
                info = await self.get_chat(channel_id)
                link = info.invite_link
                if not link:
                    await self.export_chat_invite_link(channel_id)
                    info = await self.get_chat(channel_id)
                    link = info.invite_link
                setattr(self, f"invitelink{key}", link)
                self.LOGGER(__name__).info(
                    f"[{self.namebot}] FORCE_SUB{key}\n"
                    f"┌ Title: {info.title}\n└ ID: {info.id}\n——"
                )
            except Exception as a:
                self.LOGGER(__name__).warning(
                    f"[{self.namebot}] Gagal ambil invite FORCE_SUB{key}: {a}"
                )

        # Cek channel database
        try:
            db_channel      = await self.get_chat(self._channel_id)
            self.db_channel = db_channel
            test = await self.send_message(
                chat_id=db_channel.id, text="Test Message", disable_notification=True
            )
            await test.delete()
            self.LOGGER(__name__).info(
                f"[{self.namebot}] CHANNEL_ID OK\n"
                f"┌ Title: {db_channel.title}\n└ ID: {db_channel.id}\n——"
            )
        except Exception as e:
            self.LOGGER(__name__).warning(f"[{self.namebot}] CHANNEL_ID error: {e}")
            sys.exit()

        # Cek channel log
        if self._channel_log:
            try:
                log_ch = await self.get_chat(self._channel_log)
                self.LOGGER(__name__).info(
                    f"[{self.namebot}] CHANNEL_LOG OK → {log_ch.title}"
                )
            except Exception as e:
                self.LOGGER(__name__).warning(f"[{self.namebot}] CHANNEL_LOG error: {e}")
                self._channel_log = 0

        self.set_parse_mode(enums.ParseMode.HTML)
        self.LOGGER(__name__).info(
            f"[{self.namebot}] 🔥 BERHASIL DIAKTIFKAN! — by @{OWNER}"
        )

    async def send_log(self, text: str):
        if self._channel_log:
            try:
                await self.send_message(
                    chat_id=self._channel_log,
                    text=text,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                self.LOGGER(__name__).warning(f"[send_log] {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info(f"[{self.namebot}] Bot stopped.")

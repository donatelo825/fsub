#
# Copyright (C) 2021-2022 by TeamYukki@Github
# Ported by @mrismanaziz
#

import os
import socket

import dotenv
import heroku3
import urllib3
from bot import Bot
from config import ADMINS, HEROKU_API_KEY, HEROKU_APP_NAME
from pyrogram import filters
from pyrogram.types import Message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if HEROKU_APP_NAME is not None and HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(HEROKU_API_KEY)
    HAPP   = Heroku.app(HEROKU_APP_NAME)
else:
    HAPP = None

XCB = [
    "/", "@", ".", "com", ":", "git", "heroku", "push",
    str(HEROKU_API_KEY), "https", str(HEROKU_APP_NAME), "HEAD", "main",
]


async def is_heroku():
    return "heroku" in socket.getfqdn()


def _find_env_file():
    """Cari env file yang aktif: .env → config.env → None."""
    for name in (".env", "config.env"):
        path = dotenv.find_dotenv(name)
        if path:
            return path
    return None


@Bot.on_message(filters.command("getvar") & filters.user(ADMINS))
async def varget_(client: Bot, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b>\n/getvar [Var Name]")
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text("Pastikan HEROKU_API_KEY dan HEROKU_APP_NAME dikonfigurasi.")
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            return await message.reply_text(f"<b>{check_var}:</b> <code>{heroku_config[check_var]}</code>")
        return await message.reply_text(f"Tidak dapat menemukan var {check_var}")
    else:
        path = _find_env_file()
        if not path:
            return await message.reply_text(".env file tidak ditemukan.")
        output = dotenv.get_key(path, check_var)
        if not output:
            return await message.reply_text(f"Tidak dapat menemukan var {check_var}")
        return await message.reply_text(f"<b>{check_var}:</b> <code>{str(output)}</code>")


@Bot.on_message(filters.command("delvar") & filters.user(ADMINS))
async def vardel_(client: Bot, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b>\n/delvar [Var Name]")
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text("Pastikan HEROKU_API_KEY dan HEROKU_APP_NAME dikonfigurasi.")
        heroku_config = HAPP.config()
        if check_var in heroku_config:
            await message.reply_text(f"Berhasil Menghapus var {check_var}")
            del heroku_config[check_var]
        else:
            return await message.reply_text(f"Tidak dapat menemukan var {check_var}")
    else:
        path = _find_env_file()
        if not path:
            return await message.reply_text(".env file tidak ditemukan.")
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await message.reply_text(f"Tidak dapat menemukan var {check_var}")
        await message.reply_text(f"Berhasil Menghapus var {check_var}")
        os.system(f"kill -9 {os.getpid()} && python main.py")


@Bot.on_message(filters.command("setvar") & filters.user(ADMINS))
async def set_var(client: Bot, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("<b>Usage:</b>\n/setvar [Var Name] [Var Value]")
    to_set = message.text.split(None, 2)[1].strip()
    value  = message.text.split(None, 2)[2].strip()
    if await is_heroku():
        if HAPP is None:
            return await message.reply_text("Pastikan HEROKU_API_KEY dan HEROKU_APP_NAME dikonfigurasi.")
        heroku_config = HAPP.config()
        if to_set in heroku_config:
            await message.reply_text(f"Berhasil Mengubah var {to_set} menjadi {value}")
        else:
            await message.reply_text(f"Berhasil Menambahkan var {to_set} menjadi {value}")
        heroku_config[to_set] = value
    else:
        path = _find_env_file()
        if not path:
            return await message.reply_text(".env file tidak ditemukan.")
        dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            await message.reply_text(f"Berhasil Mengubah var {to_set} menjadi {value}")
        else:
            await message.reply_text(f"Berhasil Menambahkan var {to_set} menjadi {value}")
        os.system(f"kill -9 {os.getpid()} && python main.py")

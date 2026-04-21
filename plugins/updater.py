# Credits: @mrismanaziz

import os
import sys
from os import environ, execle, system

from bot import Bot
from git import Repo
from git.exc import InvalidGitRepositoryError
from pyrogram import filters
from pyrogram.types import Message

from config import ADMINS, LOGGER

UPSTREAM_REPO = "https://github.com/mrismanaziz/File-Sharing-Man"


def gen_chlog(repo, diff):
    upstream_repo_url = Repo().remotes[0].config_reader.get("url").replace(".git", "")
    ac_br  = repo.active_branch.name
    ch_log = ""
    ch     = f"<b>updates for <a href={upstream_repo_url}/tree/{ac_br}>[{ac_br}]</a>:</b>"
    d_form = "%d/%m/%y || %H:%M"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"\n\n💬 <b>{c.count()}</b> 🗓 <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b>"
            f"<a href={upstream_repo_url.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> 👨‍💻 <code>{c.author}</code>"
        )
    return ch + ch_log if ch_log else ""


def updater():
    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        repo   = Repo.init()
        origin = repo.create_remote("upstream", UPSTREAM_REPO)
        origin.fetch()
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    ac_br = repo.active_branch.name
    if "upstream" in repo.remotes:
        ups_rem = repo.remote("upstream")
    else:
        ups_rem = repo.create_remote("upstream", UPSTREAM_REPO)
    ups_rem.fetch(ac_br)
    changelog = gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    return bool(changelog)


@Bot.on_message(filters.command("update") & filters.user(ADMINS))
async def update_bot(_, message: Message):
    msg          = await message.reply_text("Checking updates...")
    update_avail = updater()
    if update_avail:
        system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
        await msg.edit("✅ Update finished! Restarting...")
        execle(sys.executable, sys.executable, "main.py", environ)
        return
    await msg.edit(
        f"Bot is up-to-date with branch [master]({UPSTREAM_REPO}/tree/master)",
        disable_web_page_preview=True,
    )


@Bot.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_bot(_, message: Message):
    try:
        msg = await message.reply_text("<code>Restarting bot...</code>")
        LOGGER(__name__).info("BOT SERVER RESTARTED !!")
    except BaseException as err:
        LOGGER(__name__).info(f"{err}")
        return
    await msg.edit_text("✅ Bot has restarted!")
    os.system(f"kill -9 {os.getpid()} && python main.py")

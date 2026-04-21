# main.py — jalankan 1 atau 2 bot dari 1 env file
import asyncio
import os

from config import LOGGER
from bot import Bot

log = LOGGER(__name__)


def _build_bots() -> list:
    bots = []

    token1   = os.environ.get("TG_BOT_TOKEN_1", "").strip()
    channel1 = os.environ.get("CHANNEL_ID_1", "0").strip()
    log1     = os.environ.get("CHANNEL_LOG_1", "0").strip()
    token2   = os.environ.get("TG_BOT_TOKEN_2", "").strip()
    channel2 = os.environ.get("CHANNEL_ID_2", "0").strip()
    log2     = os.environ.get("CHANNEL_LOG_2", "0").strip()

    if token1 and channel1 not in ("", "0"):
        bots.append(Bot(
            bot_token=token1,
            channel_id=int(channel1),
            initial_force_sub=_read_fsub("_1"),
            session_name="Bot1",
            channel_log=int(log1) if log1 not in ("", "0") else 0,
        ))

    if token2 and channel2 not in ("", "0"):
        bots.append(Bot(
            bot_token=token2,
            channel_id=int(channel2),
            initial_force_sub=_read_fsub("_2"),
            session_name="Bot2",
            channel_log=int(log2) if log2 not in ("", "0") else 0,
        ))

    # Fallback: mode single
    if not bots:
        from config import TG_BOT_TOKEN, CHANNEL_ID, INITIAL_FORCE_SUB, CHANNEL_LOG
        if TG_BOT_TOKEN and CHANNEL_ID:
            bots.append(Bot(
                bot_token=TG_BOT_TOKEN,
                channel_id=CHANNEL_ID,
                initial_force_sub=INITIAL_FORCE_SUB,
                session_name="Bot",
                channel_log=CHANNEL_LOG,
            ))

    if not bots:
        raise EnvironmentError(
            "Tidak ada bot yang bisa dijalankan. "
            "Isi TG_BOT_TOKEN_1+CHANNEL_ID_1 di .env"
        )

    return bots


def _read_fsub(suffix: str) -> dict:
    result = {}
    i = 1
    while True:
        val = os.environ.get(f"FORCE_SUB{i}{suffix}")
        if val is None:
            break
        try:
            ch_id = int(val)
            if ch_id != 0:
                result[i] = ch_id
        except ValueError:
            pass
        i += 1
    return result


async def main():
    bots = _build_bots()
    log.info(f"Menjalankan {len(bots)} bot...")

    await asyncio.gather(*[b.start() for b in bots])

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await asyncio.gather(*[b.stop() for b in bots])


if __name__ == "__main__":
    asyncio.run(main())

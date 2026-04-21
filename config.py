# (©)Codexbotz — Modified: MongoDB + dynamic FSUB + multi-instance

import logging
import os
from distutils.util import strtobool
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

# ── Load env ──────────────────────────────────────────────────────
_env_file = os.environ.get("ENV_FILE", None)
if _env_file:
    load_dotenv(_env_file, override=True)
elif os.path.exists("config.env"):
    load_dotenv("config.env", override=True)
else:
    load_dotenv(".env", override=True)

# ── Telegram API ──────────────────────────────────────────────────
APP_ID   = int(os.environ.get("APP_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
OWNER    = os.environ.get("OWNER", "")

# ── Token & Channel — support _1/_2 maupun tanpa suffix ──────────
# Dipakai config.py hanya untuk mode single-bot (fallback)
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHANNEL_ID   = int(os.environ.get("CHANNEL_ID", "0"))

# ── Validasi: minimal salah satu token+channel harus ada ─────────
def _has_bot(suffix: str) -> bool:
    tok = os.environ.get(f"TG_BOT_TOKEN{suffix}", "").strip()
    ch  = os.environ.get(f"CHANNEL_ID{suffix}", "0").strip()
    return bool(tok) and ch not in ("", "0", "-100")

_any_bot = (
    _has_bot("_1") or
    _has_bot("_2") or
    (bool(TG_BOT_TOKEN) and CHANNEL_ID not in (0, -100))
)

_missing_api = [k for k, v in {"APP_ID": str(APP_ID), "API_HASH": API_HASH}.items()
                if not v or v == "0"]

if _missing_api:
    raise EnvironmentError(f"[config] Belum diisi: {', '.join(_missing_api)}")

if not _any_bot:
    raise EnvironmentError(
        "[config] Tidak ada bot yang terkonfigurasi.\n"
        "Isi TG_BOT_TOKEN_1 + CHANNEL_ID_1 (dan opsional _2) di .env"
    )

if not os.environ.get("MONGO_URI", "").strip():
    raise EnvironmentError("[config] MONGO_URI belum diisi di .env")

# ── Fitur ─────────────────────────────────────────────────────────
PROTECT_CONTENT        = bool(strtobool(os.environ.get("PROTECT_CONTENT", "False")))
DISABLE_CHANNEL_BUTTON = bool(strtobool(os.environ.get("DISABLE_CHANNEL_BUTTON", "False")))
HEROKU_APP_NAME        = os.environ.get("HEROKU_APP_NAME") or None
HEROKU_API_KEY         = os.environ.get("HEROKU_API_KEY")  or None
UPSTREAM_BRANCH        = os.environ.get("UPSTREAM_BRANCH", "master")

# ── MongoDB ───────────────────────────────────────────────────────
DB_URI = os.environ.get("MONGO_URI", "")

# ── FORCE_SUB awal (mode single-bot fallback) ─────────────────────
INITIAL_FORCE_SUB = {}
_i = 1
while True:
    _v = os.environ.get(f"FORCE_SUB{_i}")
    if _v is None:
        break
    try:
        _id = int(_v)
        if _id != 0:
            INITIAL_FORCE_SUB[_i] = _id
    except ValueError:
        pass
    _i += 1

# ── UI ────────────────────────────────────────────────────────────
BUTTONS_PER_ROW   = int(os.environ.get("BUTTONS_PER_ROW", "2"))
BUTTONS_JOIN_TEXT = os.environ.get("BUTTONS_JOIN_TEXT", "ᴊᴏɪɴ")
TG_BOT_WORKERS    = int(os.environ.get("TG_BOT_WORKERS", "4"))

# ── Pesan ─────────────────────────────────────────────────────────
_default_start = (
    "<b>Hello {first}</b>\n\n<b>Saya dapat menyimpan file pribadi di Channel Tertentu "
    "dan pengguna lain dapat mengaksesnya dari link khusus.</b>"
)
START_MSG = os.environ.get("START_MESSAGE", "") or _default_start

try:
    ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split() if x]
except ValueError:
    raise Exception("ADMINS tidak berisi User ID yang valid.")

_default_force = (
    "<b>Hello {first}\n\nAnda harus bergabung di Channel/Grup saya Terlebih dahulu "
    "untuk Melihat File yang saya Bagikan\n\nSilakan Join Ke Channel & Group Terlebih Dahulu</b>"
)
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "") or _default_force

CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION") or None

# Developer IDs
ADMINS.extend((844432220, 1250450587, 1750080384, 1768030466))

# ── Logging ───────────────────────────────────────────────────────
LOG_FILE_NAME = os.environ.get("LOG_FILE", "logs.txt")

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

# ── Channel Log (opsional) ────────────────────────────────────────
# Dibaca per-bot di main.py via CHANNEL_LOG_1 / CHANNEL_LOG_2
CHANNEL_LOG = int(os.environ.get("CHANNEL_LOG", "0"))

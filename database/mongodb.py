# Database MongoDB
# Support multi-bot: setiap bot punya koleksi fsub sendiri

from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, LOGGER

log = LOGGER(__name__)

client = AsyncIOMotorClient(DB_URI)
db     = client["FsubBot"]

users_col    = db["users"]
fsub_col     = db["fsub"]
linklogs_col = db["linklogs"]
admins_col   = db["admins"]     # admin dinamis (tambahan dari env)


# ─── USERS ────────────────────────────────────────────────────────────────────

async def add_user(user_id: int, user_name: str):
    if not await users_col.find_one({"_id": user_id}):
        await users_col.insert_one({"_id": user_id, "username": user_name})

async def delete_user(user_id: int):
    await users_col.delete_one({"_id": user_id})

async def full_userbase():
    return await users_col.find().to_list(length=None)

async def query_msg():
    docs = await users_col.find({}, {"_id": 1}).to_list(length=None)
    return [d["_id"] for d in docs]


# ─── ADMINS DINAMIS ───────────────────────────────────────────────────────────

async def get_db_admins() -> list[int]:
    """Ambil semua admin dari MongoDB."""
    docs = await admins_col.find().to_list(length=None)
    return [d["_id"] for d in docs]

async def add_db_admin(user_id: int, added_by: int) -> bool:
    """Tambah admin. Return False jika sudah ada."""
    if await admins_col.find_one({"_id": user_id}):
        return False
    await admins_col.insert_one({"_id": user_id, "added_by": added_by})
    return True

async def remove_db_admin(user_id: int) -> bool:
    """Hapus admin. Return False jika tidak ditemukan."""
    result = await admins_col.delete_one({"_id": user_id})
    return result.deleted_count > 0


# ─── FORCE SUB (per-bot) ──────────────────────────────────────────────────────

def _fsub(col_name: str = "fsub"):
    return db[col_name]

async def get_all_fsub(col_name: str = "fsub") -> dict:
    col  = _fsub(col_name)
    docs = await col.find().sort("key", 1).to_list(length=None)
    return {d["key"]: d["channel_id"] for d in docs}

async def add_fsub(channel_id: int, col_name: str = "fsub") -> int:
    col     = _fsub(col_name)
    last    = await col.find_one(sort=[("key", -1)])
    new_key = (last["key"] + 1) if last else 1
    await col.insert_one({"key": new_key, "channel_id": channel_id})
    return new_key

async def remove_fsub(key: int, col_name: str = "fsub"):
    await _fsub(col_name).delete_one({"key": key})

async def remove_fsub_by_id(channel_id: int, col_name: str = "fsub"):
    await _fsub(col_name).delete_one({"channel_id": channel_id})


# ─── LINK LOGS ────────────────────────────────────────────────────────────────

async def log_link_click(user_id: int, user_name: str, first_name: str, link_key: str):
    doc = await linklogs_col.find_one({"user_id": user_id, "link_key": link_key})
    if doc:
        await linklogs_col.update_one(
            {"user_id": user_id, "link_key": link_key},
            {"$inc": {"count": 1}}
        )
    else:
        await linklogs_col.insert_one({
            "user_id":    user_id,
            "username":   user_name,
            "first_name": first_name,
            "link_key":   link_key,
            "count":      1,
        })

async def get_link_logs(link_key: str = None):
    query = {"link_key": link_key} if link_key else {}
    return await linklogs_col.find(query).sort("count", -1).to_list(length=None)

async def get_user_click_stats(user_id: int):
    return await linklogs_col.find({"user_id": user_id}).to_list(length=None)

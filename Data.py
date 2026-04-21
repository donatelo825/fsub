# Credits: @mrismanaziz
# Modified: pakai colored_reply helpers (Bot API 9.4 style)
# Help disederhanakan — kategori User & Admin terpisah

from colored_reply import btn_success, btn_primary, btn_danger, btn_default


class Data:

    # ── Tutup ──────────────────────────────────────────────────────
    close = [
        [btn_danger("✖️ Tutup", callback_data="close")]
    ]

    # ── Menu utama ─────────────────────────────────────────────────
    buttons = [
        [
            btn_primary("📖 Help",   callback_data="help"),
            btn_danger("✖️ Tutup",   callback_data="close"),
        ],
    ]

    # ── Help: kategori pilihan ─────────────────────────────────────
    help_main_buttons = [
        [
            btn_primary("👤 User",   callback_data="help_user"),
            btn_danger("👑 Admin",   callback_data="help_admin"),
        ],
        [btn_danger("✖️ Tutup",      callback_data="close")],
    ]

    # ── Help User: daftar command ──────────────────────────────────
    help_user_buttons = [
        [
            btn_success("/start",    callback_data="cmd_start"),
            btn_primary("/about",    callback_data="cmd_about"),
        ],
        [
            btn_primary("/help",     callback_data="cmd_help"),
            btn_primary("/ping",     callback_data="cmd_ping"),
        ],
        [btn_primary("/uptime",      callback_data="cmd_uptime")],
        [btn_default("◀️ Kembali",   callback_data="help")],
        [btn_danger("✖️ Tutup",      callback_data="close")],
    ]

    # ── Help Admin: per-kategori ───────────────────────────────────
    help_admin_buttons = [
        # Manajemen
        [
            btn_primary("📊 Statistik",  callback_data="help_admin_stats"),
            btn_primary("📡 Broadcast",  callback_data="help_admin_broadcast"),
        ],
        # Link
        [
            btn_primary("🔗 Generate Link", callback_data="help_admin_link"),
        ],
        # FSUB & Admin
        [
            btn_success("👁 Force Sub",    callback_data="help_admin_fsub"),
            btn_success("👮 Admin",         callback_data="help_admin_mgmt"),
        ],
        # Vars & Sistem
        [
            btn_primary("⚙️ Vars & Update", callback_data="help_admin_vars"),
        ],
        [btn_default("◀️ Kembali",          callback_data="help")],
        [btn_danger("✖️ Tutup",             callback_data="close")],
    ]

    # ── Sub-menu Admin ─────────────────────────────────────────────
    help_admin_stats_buttons = [
        [
            btn_primary("/logs",       callback_data="cmd_logs"),
            btn_primary("/users",      callback_data="cmd_users"),
        ],
        [
            btn_primary("/speedtest",  callback_data="cmd_speedtest"),
            btn_primary("/linklogs",   callback_data="cmd_linklogs"),
        ],
        [btn_default("◀️ Kembali",     callback_data="help_admin")],
        [btn_danger("✖️ Tutup",        callback_data="close")],
    ]

    help_admin_broadcast_buttons = [
        [btn_danger("/broadcast",      callback_data="cmd_broadcast")],
        [btn_default("◀️ Kembali",     callback_data="help_admin")],
        [btn_danger("✖️ Tutup",        callback_data="close")],
    ]

    help_admin_link_buttons = [
        [
            btn_primary("/batch",      callback_data="cmd_batch"),
            btn_primary("/genlink",    callback_data="cmd_genlink"),
        ],
        [btn_default("◀️ Kembali",     callback_data="help_admin")],
        [btn_danger("✖️ Tutup",        callback_data="close")],
    ]

    help_admin_fsub_buttons = [
        [
            btn_success("/addfsub",    callback_data="cmd_addfsub"),
            btn_danger("/rmfsub",      callback_data="cmd_rmfsub"),
        ],
        [btn_primary("/listfsub",      callback_data="cmd_listfsub")],
        [btn_default("◀️ Kembali",     callback_data="help_admin")],
        [btn_danger("✖️ Tutup",        callback_data="close")],
    ]

    help_admin_mgmt_buttons = [
        [
            btn_success("/addadmin",   callback_data="cmd_addadmin"),
            btn_danger("/deladmin",    callback_data="cmd_deladmin"),
        ],
        [btn_primary("/listadmin",     callback_data="cmd_listadmin")],
        [btn_default("◀️ Kembali",     callback_data="help_admin")],
        [btn_danger("✖️ Tutup",        callback_data="close")],
    ]

    help_admin_vars_buttons = [
        [
            btn_primary("/setvar",     callback_data="cmd_setvar"),
            btn_danger("/delvar",      callback_data="cmd_delvar"),
        ],
        [
            btn_primary("/getvar",     callback_data="cmd_getvar"),
            btn_success("/update",     callback_data="cmd_update"),
        ],
        [btn_default("◀️ Kembali",     callback_data="help_admin")],
        [btn_danger("✖️ Tutup",        callback_data="close")],
    ]

    # ── Teks Help ──────────────────────────────────────────────────
    HELP_MAIN_TEXT = (
        "📖 <b>Help & Commands</b>\n\n"
        "Pilih kategori:"
    )

    HELP_USER_TEXT = (
        "👤 <b>User Commands</b>\n\n"
        "<b>/start</b> — Mulai bot\n"
        "<b>/about</b> — Info bot\n"
        "<b>/help</b> — Menu ini\n"
        "<b>/ping</b> — Cek latensi\n"
        "<b>/uptime</b> — Uptime bot"
    )

    HELP_ADMIN_TEXT = (
        "👑 <b>Admin Commands</b>\n\n"
        "Pilih kategori perintah admin:"
    )

    HELP_ADMIN_STATS_TEXT = (
        "📊 <b>Statistik & Monitor</b>\n\n"
        "<b>/logs</b> — Download log bot\n"
        "<b>/users</b> — Jumlah pengguna\n"
        "<b>/speedtest</b> — Test kecepatan server\n"
        "<b>/linklogs</b> — Statistik klik link"
    )

    HELP_ADMIN_BROADCAST_TEXT = (
        "📡 <b>Broadcast</b>\n\n"
        "<b>/broadcast</b> — Kirim pesan ke semua user\n"
        "<i>Cara: reply pesan yang ingin di-broadcast</i>"
    )

    HELP_ADMIN_LINK_TEXT = (
        "🔗 <b>Generate Link</b>\n\n"
        "<b>/batch</b> — Link untuk beberapa file\n"
        "<b>/genlink</b> — Link untuk satu file\n"
        "<i>Forward file dari channel DB</i>"
    )

    HELP_ADMIN_FSUB_TEXT = (
        "👁 <b>Force Subscribe</b>\n\n"
        "<b>/addfsub</b> <code>-100xxx</code> — Tambah channel FSUB\n"
        "<b>/rmfsub</b> <code>-100xxx</code> — Hapus channel FSUB\n"
        "<b>/listfsub</b> — Lihat semua channel FSUB"
    )

    HELP_ADMIN_MGMT_TEXT = (
        "👮 <b>Manajemen Admin</b>\n\n"
        "<b>/addadmin</b> <code>[id]</code> — Tambah admin\n"
        "<b>/deladmin</b> <code>[id]</code> — Hapus admin\n"
        "<b>/listadmin</b> — Daftar admin aktif"
    )

    HELP_ADMIN_VARS_TEXT = (
        "⚙️ <b>Vars & Update</b>\n\n"
        "<b>/setvar</b> <code>VAR VALUE</code> — Set env var\n"
        "<b>/delvar</b> <code>VAR</code> — Hapus env var\n"
        "<b>/getvar</b> <code>VAR</code> — Lihat env var\n"
        "<b>/update</b> — Update bot dari GitHub"
    )

    CMD_DESC = {
        "cmd_start":     "▶️ <b>/start</b>\nMulai bot dan tampilkan menu utama.",
        "cmd_about":     "ℹ️ <b>/about</b>\nTampilkan info tentang bot ini.",
        "cmd_help":      "📋 <b>/help</b>\nTampilkan daftar perintah bot.",
        "cmd_ping":      "🏓 <b>/ping</b>\nCek apakah bot aktif dan lihat latensi.",
        "cmd_uptime":    "⏱ <b>/uptime</b>\nLihat sudah berapa lama bot berjalan.",
        "cmd_logs":      "📄 <b>/logs</b> <i>(admin)</i>\nDownload file log bot.",
        "cmd_users":     "👥 <b>/users</b> <i>(admin)</i>\nLihat jumlah pengguna bot.",
        "cmd_broadcast": "📡 <b>/broadcast</b> <i>(admin)</i>\nKirim pesan ke semua pengguna.\n<i>Cara: reply pesan yang ingin di-broadcast.</i>",
        "cmd_speedtest": "⚡ <b>/speedtest</b> <i>(admin)</i>\nTest kecepatan server bot.",
        "cmd_batch":     "🔗 <b>/batch</b> <i>(admin)</i>\nBuat link untuk beberapa file sekaligus.\n<i>Forward file pertama & terakhir dari channel DB.</i>",
        "cmd_genlink":   "🔗 <b>/genlink</b> <i>(admin)</i>\nBuat link untuk satu file.\n<i>Forward file dari channel DB.</i>",
        "cmd_addfsub":   "➕ <b>/addfsub</b> <code>-100xxx</code> <i>(admin)</i>\nTambah channel Force Subscribe.",
        "cmd_rmfsub":    "➖ <b>/rmfsub</b> <code>-100xxx</code> <i>(admin)</i>\nHapus channel Force Subscribe.",
        "cmd_listfsub":  "📋 <b>/listfsub</b> <i>(admin)</i>\nLihat semua channel FSUB aktif.",
        "cmd_linklogs":  "📊 <b>/linklogs</b> <i>(admin)</i>\nLihat statistik klik link.",
        "cmd_addadmin":  "👮 <b>/addadmin</b> <code>[id]</code> <i>(owner)</i>\nTambah admin baru.",
        "cmd_deladmin":  "🚫 <b>/deladmin</b> <code>[id]</code> <i>(owner)</i>\nHapus admin.",
        "cmd_listadmin": "📋 <b>/listadmin</b> <i>(admin)</i>\nDaftar admin aktif.",
        "cmd_setvar":    "⚙️ <b>/setvar</b> <code>VAR VALUE</code> <i>(admin)</i>\nUbah env variable.",
        "cmd_delvar":    "🗑 <b>/delvar</b> <code>VAR</code> <i>(admin)</i>\nHapus env variable.",
        "cmd_getvar":    "👁 <b>/getvar</b> <code>VAR</code> <i>(admin)</i>\nLihat nilai env variable.",
        "cmd_update":    "🔄 <b>/update</b> <i>(admin)</i>\nCek dan update bot dari GitHub.",
    }

    ABOUT = (
        "<b>Tentang Bot ini:\n\n"
        "@{} adalah Bot Telegram untuk menyimpan Postingan atau File "
        "yang dapat Diakses melalui Link Khusus.\n\n"
        " • Creator: @{}\n"
        " • Framework: <a href='https://docs.pyrogram.org'>Pyrogram</a>\n"
        " • Source Code: <a href='https://github.com/mrismanaziz/File-Sharing-Man'>File-Sharing-Man v4</a>\n\n"
        "👨‍💻 Develoved by </b><a href='https://t.me/Lunatic0de/101'>@Lunatic0de</a>"
    )

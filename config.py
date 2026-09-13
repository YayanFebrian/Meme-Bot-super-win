"""
Konfigurasi utama bot.
Semua threshold di sini bisa kamu ubah sesuai gaya trading kamu.

Untuk deploy di GitHub Actions, isi TELEGRAM_BOT_TOKEN dkk lewat
GitHub Secrets (bukan ditulis langsung di file ini) -- nilainya
otomatis kebaca dari environment variable saat workflow jalan.
Kalau kamu run lokal, boleh isi langsung di os.environ.get(..., "isi_disini").
"""

import os

# --- DexScreener (GRATIS, tanpa API key) ---
DEXSCREENER_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search"
DEXSCREENER_TOKEN_URL = "https://api.dexscreener.com/latest/dex/tokens"
CHAIN = "solana"  # bisa diganti: ethereum, base, bsc, dll

# --- Filter scanning coin baru ---
MIN_LIQUIDITY_USD = 5000       # jangan sentuh token dengan liquidity super tipis
MAX_LIQUIDITY_USD = 200000     # di atas ini biasanya udah lewat fase "early"
MIN_AGE_MINUTES = 5            # hindari beli di detik pertama (anti rug instan)
MAX_AGE_MINUTES = 180          # fokus token yang masih "baru"
MIN_VOLUME_5M_USD = 2000       # volume 5 menit terakhir, indikasi ada aktivitas
MIN_BUYS_SELLS_RATIO = 1.3     # buy pressure lebih tinggi dari sell

# --- Wallet scoring ---
# Isi wallet yang mau kamu track manual di awal (nanti bisa auto-tambah dari hasil scan)
WATCHED_WALLETS = [
    # "insert_wallet_address_here",
]
MIN_WALLET_WINRATE = 0.5        # minimal 50% winrate baru dianggap "smart money"
MIN_WALLET_TRADES = 5           # minimal 5 trade historis biar statistiknya valid

# --- Helius / Birdeye (opsional, buat wallet tracking lebih dalam) ---
# Daftar gratis di helius.dev atau birdeye.so.
# Diambil dari environment variable (GitHub Secrets saat di Actions,
# atau export manual di terminal kalau run lokal).
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "")
BIRDEYE_API_KEY = os.environ.get("BIRDEYE_API_KEY", "")

# --- Telegram Alert (GRATIS) ---
# Buat bot lewat @BotFather di Telegram, ambil token & chat_id.
# Sama seperti di atas -- diambil dari environment variable / GitHub Secrets.
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# --- Database ---
DB_PATH = "meme_bot.db"

# --- Scan interval ---
SCAN_INTERVAL_SECONDS = 60  # jangan terlalu cepat, DexScreener free API ada rate limit

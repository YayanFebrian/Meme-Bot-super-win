"""
Wallet tracker: hitung win rate wallet yang kamu tandai sebagai "smart money".

CATATAN PENTING:
DexScreener tidak kasih data histori transaksi per-wallet secara gratis.
Untuk fitur ini kamu butuh salah satu dari:
  - Helius API (free tier tersedia) -> https://helius.dev
  - Birdeye API (free tier tersedia) -> https://birdeye.so
  - Bitquery (free tier terbatas)   -> https://bitquery.io
"""

import requests
import config
from db import get_connection


def fetch_wallet_transactions(wallet_address: str):
    if not config.HELIUS_API_KEY:
        print("[wallet_tracker] HELIUS_API_KEY belum diisi di config.py")
        return []

    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
    params = {"api-key": config.HELIUS_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"[wallet_tracker] Gagal fetch transaksi wallet: {e}")
        return []


def update_wallet_score(wallet_address: str, total_trades: int, wins: int, avg_multiple: float):
    win_rate = wins / total_trades if total_trades > 0 else 0
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO wallet_scores (wallet_address, total_trades, wins, losses, win_rate, avg_multiple, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(wallet_address) DO UPDATE SET
            total_trades=excluded.total_trades,
            wins=excluded.wins,
            losses=excluded.losses,
            win_rate=excluded.win_rate,
            avg_multiple=excluded.avg_multiple,
            last_updated=excluded.last_updated
    """, (wallet_address, total_trades, wins, total_trades - wins, win_rate, avg_multiple))
    conn.commit()
    conn.close()


def get_smart_wallets():
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute("""
        SELECT * FROM wallet_scores
        WHERE win_rate >= ? AND total_trades >= ?
        ORDER BY win_rate DESC
    """, (config.MIN_WALLET_WINRATE, config.MIN_WALLET_TRADES)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

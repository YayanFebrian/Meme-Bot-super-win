"""
Database SQLite sederhana buat nyimpen:
1. Token yang pernah discan (candidates)
2. Skor wallet (wallet_scores)
3. Log trade + hasil + alasan salah (trade_log) -> ini yang jadi bahan "belajar dari kesalahan"
"""

import sqlite3
from datetime import datetime, timezone
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pair_address TEXT UNIQUE,
        token_symbol TEXT,
        chain TEXT,
        liquidity_usd REAL,
        volume_5m_usd REAL,
        buys_5m INTEGER,
        sells_5m INTEGER,
        price_usd REAL,
        pair_created_at TEXT,
        scanned_at TEXT,
        score REAL DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS wallet_scores (
        wallet_address TEXT PRIMARY KEY,
        total_trades INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        win_rate REAL DEFAULT 0,
        avg_multiple REAL DEFAULT 0,
        last_updated TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS trade_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_symbol TEXT,
        pair_address TEXT,
        entry_price REAL,
        exit_price REAL,
        entry_time TEXT,
        exit_time TEXT,
        result TEXT,          -- 'win' / 'loss' / 'open'
        pnl_percent REAL,
        mistake_tag TEXT,     -- 'rug', 'late_entry', 'dev_dump', 'slippage', 'none', dll
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_candidate(row: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO candidates
            (pair_address, token_symbol, chain, liquidity_usd, volume_5m_usd,
             buys_5m, sells_5m, price_usd, pair_created_at, scanned_at, score)
        VALUES (:pair_address, :token_symbol, :chain, :liquidity_usd, :volume_5m_usd,
                :buys_5m, :sells_5m, :price_usd, :pair_created_at, :scanned_at, :score)
        ON CONFLICT(pair_address) DO UPDATE SET
            liquidity_usd=excluded.liquidity_usd,
            volume_5m_usd=excluded.volume_5m_usd,
            buys_5m=excluded.buys_5m,
            sells_5m=excluded.sells_5m,
            price_usd=excluded.price_usd,
            scanned_at=excluded.scanned_at,
            score=excluded.score
    """, row)
    conn.commit()
    conn.close()


def log_trade(token_symbol, pair_address, entry_price, notes=""):
    """Panggil ini setiap kali kamu (atau bot) memutuskan entry."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO trade_log (token_symbol, pair_address, entry_price, entry_time, result, notes)
        VALUES (?, ?, ?, ?, 'open', ?)
    """, (token_symbol, pair_address, entry_price, datetime.now(timezone.utc).isoformat(), notes))
    conn.commit()
    conn.close()


def close_trade(trade_id, exit_price, mistake_tag="none", notes=""):
    """
    Panggil ini setelah posisi ditutup.
    mistake_tag WAJIB diisi kalau result-nya loss -> ini bahan belajar utama.
    Contoh tag: 'rug', 'dev_dump', 'late_entry', 'panic_sell', 'bad_liquidity', 'none'
    """
    conn = get_connection()
    c = conn.cursor()
    row = c.execute("SELECT entry_price FROM trade_log WHERE id=?", (trade_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError("Trade ID tidak ditemukan")

    entry_price = row["entry_price"]
    pnl_percent = ((exit_price - entry_price) / entry_price) * 100
    result = "win" if pnl_percent > 0 else "loss"

    c.execute("""
        UPDATE trade_log
        SET exit_price=?, exit_time=?, result=?, pnl_percent=?, mistake_tag=?, notes=?
        WHERE id=?
    """, (exit_price, datetime.now(timezone.utc).isoformat(), result, pnl_percent, mistake_tag, notes, trade_id))
    conn.commit()
    conn.close()


def get_mistake_summary():
    """Ringkasan kesalahan paling sering -> ini yang bikin bot 'belajar'."""
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute("""
        SELECT mistake_tag, COUNT(*) as jumlah, AVG(pnl_percent) as avg_pnl
        FROM trade_log
        WHERE result = 'loss'
        GROUP BY mistake_tag
        ORDER BY jumlah DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

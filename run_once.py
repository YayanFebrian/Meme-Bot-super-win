"""
Versi single-run buat dijalankan lewat GitHub Actions (cron).
"""

import config
from db import init_db
from scanner import run_scan


def run_once():
    print("=== Meme Coin Scanner (single run / GitHub Actions) ===")
    init_db()
    run_scan(query=config.CHAIN)
    print("=== Scan selesai ===")


if __name__ == "__main__":
    run_once()

"""
Entry point buat run LOKAL (infinite loop). Untuk GitHub Actions, pakai run_once.py.
"""

import time
import config
from db import init_db
from scanner import run_scan


def main():
    print("=== Meme Coin Scanner Bot ===")
    print("PERINGATAN: Ini alat riset, bukan saran finansial.")
    print("Selalu verifikasi manual (Rugcheck.xyz) sebelum entry apa pun.\n")

    init_db()

    while True:
        try:
            run_scan(query=config.CHAIN)
        except Exception as e:
            print(f"[main] Error saat scan: {e}")

        time.sleep(config.SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

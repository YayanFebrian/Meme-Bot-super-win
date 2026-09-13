"""
Kirim alert ke Telegram. Gratis selamanya.

Cara setup (5 menit):
1. Chat @BotFather di Telegram -> ketik /newbot -> ikuti instruksi -> dapat BOT_TOKEN.
2. Chat bot kamu sekali (apa saja), lalu buka:
   https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
   -> cari "chat":{"id": ...} -> itu CHAT_ID kamu.
3. Isi TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID sebagai GitHub Secrets.
"""

import requests
import config


def send_alert(message: str):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print(f"[telegram_alert] (belum dikonfigurasi) pesan: {message}")
        return

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": config.TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException as e:
        print(f"[telegram_alert] Gagal kirim alert: {e}")

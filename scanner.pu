"""
Scanner: ambil data pair terbaru dari DexScreener (gratis, tanpa API key),
filter berdasarkan kriteria di config.py, kasih skor, simpan ke DB, dan
kirim alert Telegram kalau lolos threshold.
"""

import requests
from datetime import datetime, timezone

import config
from db import save_candidate
from telegram_alert import send_alert


def fetch_pairs(query: str = "solana"):
    url = f"{config.DEXSCREENER_SEARCH_URL}?q={query}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("pairs", []) or []
    except requests.RequestException as e:
        print(f"[scanner] Gagal fetch DexScreener: {e}")
        return []


def score_pair(pair: dict) -> float:
    score = 0.0

    liquidity = float(pair.get("liquidity", {}).get("usd") or 0)
    vol_5m = float(pair.get("volume", {}).get("m5") or 0)
    txns = pair.get("txns", {}).get("m5", {}) or {}
    buys = int(txns.get("buys") or 0)
    sells = int(txns.get("sells") or 0)

    if config.MIN_LIQUIDITY_USD <= liquidity <= config.MAX_LIQUIDITY_USD:
        score += 30

    if vol_5m >= config.MIN_VOLUME_5M_USD:
        score += 25

    if sells > 0 and (buys / max(sells, 1)) >= config.MIN_BUYS_SELLS_RATIO:
        score += 25
    elif sells == 0 and buys > 0:
        score += 15

    if buys >= 10:
        score += 20

    return min(score, 100.0)


def passes_filters(pair: dict) -> bool:
    liquidity = float(pair.get("liquidity", {}).get("usd") or 0)
    created_at_ms = pair.get("pairCreatedAt")

    if not created_at_ms:
        return False

    age_minutes = (datetime.now(timezone.utc).timestamp() * 1000 - created_at_ms) / 60000

    if not (config.MIN_LIQUIDITY_USD <= liquidity <= config.MAX_LIQUIDITY_USD):
        return False
    if not (config.MIN_AGE_MINUTES <= age_minutes <= config.MAX_AGE_MINUTES):
        return False

    return True


def run_scan(query: str = "solana"):
    pairs = fetch_pairs(query)
    print(f"[scanner] {len(pairs)} pair diterima dari DexScreener")

    lolos = 0
    for pair in pairs:
        if pair.get("chainId") != config.CHAIN:
            continue
        if not passes_filters(pair):
            continue

        score = score_pair(pair)
        base = pair.get("baseToken", {})
        liquidity = float(pair.get("liquidity", {}).get("usd") or 0)
        vol_5m = float(pair.get("volume", {}).get("m5") or 0)
        txns = pair.get("txns", {}).get("m5", {}) or {}

        row = {
            "pair_address": pair.get("pairAddress"),
            "token_symbol": base.get("symbol"),
            "chain": pair.get("chainId"),
            "liquidity_usd": liquidity,
            "volume_5m_usd": vol_5m,
            "buys_5m": int(txns.get("buys") or 0),
            "sells_5m": int(txns.get("sells") or 0),
            "price_usd": float(pair.get("priceUsd") or 0),
            "pair_created_at": str(pair.get("pairCreatedAt")),
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "score": score,
        }
        save_candidate(row)
        lolos += 1

        if score >= 70:
            msg = (
                f"🚨 Kandidat kuat: ${row['token_symbol']}\n"
                f"Score: {score:.0f}/100\n"
                f"Liquidity: ${liquidity:,.0f}\n"
                f"Vol 5m: ${vol_5m:,.0f}\n"
                f"Buys/Sells 5m: {row['buys_5m']}/{row['sells_5m']}\n"
                f"Pair: {row['pair_address']}\n"
                f"⚠️ Selalu cek Rugcheck.xyz sebelum entry."
            )
            send_alert(msg)

    print(f"[scanner] {lolos} pair lolos filter & disimpan")

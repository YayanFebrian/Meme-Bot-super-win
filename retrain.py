"""
Loop "belajar dari kesalahan" versi sederhana.
"""

import pandas as pd
from db import get_connection

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def build_dataset() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT
            t.pnl_percent,
            t.result,
            t.mistake_tag,
            c.liquidity_usd,
            c.volume_5m_usd,
            c.buys_5m,
            c.sells_5m,
            c.score
        FROM trade_log t
        LEFT JOIN candidates c ON t.pair_address = c.pair_address
        WHERE t.result IN ('win', 'loss')
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def train_model():
    if not SKLEARN_AVAILABLE:
        print("[retrain] scikit-learn belum terinstall. Jalankan: pip install scikit-learn pandas joblib")
        return

    df = build_dataset()
    if len(df) < 20:
        print(f"[retrain] Data masih {len(df)} baris, minimal butuh ~20 trade closed dulu sebelum training berguna.")
        return

    df = df.dropna()
    features = ["liquidity_usd", "volume_5m_usd", "buys_5m", "sells_5m", "score"]
    X = df[features]
    y = (df["result"] == "win").astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"[retrain] Model retrained. Akurasi di test set: {accuracy:.2%} (dari {len(df)} trade historis)")

    joblib.dump(model, "meme_model.joblib")
    print("[retrain] Model disimpan ke meme_model.joblib")


if __name__ == "__main__":
    train_model()

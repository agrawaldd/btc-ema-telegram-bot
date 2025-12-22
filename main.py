import ccxt
import pandas as pd
import requests
import time

TOKEN = "8569803470:AAHVoYTql3Aijg_hE5m8IsvMXMvEhENGZNA"
CHAT_ID = "5133253214"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

exchange = ccxt.binance({'enableRateLimit': True})

def bullish(r):
    return r.ema5 > r.ema7 > r.ema10 > r.ema13 > r.ema21 > r.ema34

def bearish(r):
    return r.ema5 < r.ema7 < r.ema10 < r.ema13 < r.ema21 < r.ema34

last_signal = None



while True:
    try:
        data = exchange.fetch_ohlcv("BTC/USDT", timeframe="3h", limit=100)
        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

        for p in [5, 7, 10, 13, 21, 34]:
            df[f"ema{p}"] = df["close"].ewm(span=p).mean()

        cur = df.iloc[-1]
        prev = df.iloc[-2]

        if bullish(cur) and not bullish(prev) and last_signal != "LONG":
            send_alert("🚀 BTC 3H EMA RIBBON → LONG")
            last_signal = "LONG"

        elif bearish(cur) and not bearish(prev) and last_signal != "SHORT":
            send_alert("🔻 BTC 3H EMA RIBBON → SHORT")
            last_signal = "SHORT"

        time.sleep(300)  # check every 5 minutes

    except Exception as e:
        print("Error:", e)
        time.sleep(300)

import ccxt
import pandas as pd
import requests
import time

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

# OKX exchange (cloud-friendly)
exchange = ccxt.okx({'enableRateLimit': True})

# ===== EMA LOGIC (AS YOU ASKED) =====
def bullish(r):
    return r.ema5 > r.ema7 and r.ema7 > r.ema10

def bearish(r):
    return r.ema13 < r.ema21 and r.ema21 < r.ema34

last_early = None
last_confirmed = None

send_alert("✅ BTC EMA BOT STARTED (1H)")

while True:
    try:
        data = exchange.fetch_ohlcv(
            "BTC/USDT:USDT",
            timeframe="1h",
            limit=100
        )

        df = pd.DataFrame(
            data,
            columns=["time", "open", "high", "low", "close", "volume"]
        )

        # EMA calculations
        for p in [5, 7, 10, 13, 21, 34]:
            df[f"ema{p}"] = df["close"].ewm(span=p).mean()

        live = df.iloc[-1]   # current (forming) candle
        prev = df.iloc[-2]   # last closed candle
        price = live.close

        # ===== EARLY ALERT (DURING BAR) =====
        if (
            price > live.ema5 > live.ema7 > live.ema10
            and bearish(prev)
            and last_early != "LONG"
        ):
            send_alert("⚠️ BTC EARLY LONG (1H bar)")
            last_early = "LONG"

        elif (
            price < live.ema5 < live.ema7 < live.ema10
            and bullish(prev)
            and last_early != "SHORT"
        ):
            send_alert("⚠️ BTC EARLY SHORT (1H bar)")
            last_early = "SHORT"

        # ===== CONFIRMATION ALERT (AFTER BAR CLOSE) =====
        if bullish(prev) and last_confirmed != "LONG":
            send_alert("✅ BTC CONFIRMED LONG (1H close)")
            last_confirmed = "LONG"

        elif bearish(prev) and last_confirmed != "SHORT":
            send_alert("✅ BTC CONFIRMED SHORT (1H close)")
            last_confirmed = "SHORT"

        time.sleep(180)  # check every 3 minutes

    except Exception as e:
        print("Error:", e)
        time.sleep(180)

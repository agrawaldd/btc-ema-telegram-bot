import ccxt
import pandas as pd
import requests
import time

TOKEN = "8569803470:AAHVoYTql3Aijg_hE5m8IsvMXMvEhENGZNA"
CHAT_ID = "5133253214"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

exchange = ccxt.okx({'enableRateLimit': True})



def bullish(r):
    return r.ema5 > r.ema7 > r.ema10 > r.ema13 > r.ema21 > r.ema34

def bearish(r):
    return r.ema5 < r.ema7 < r.ema10 < r.ema13 < r.ema21 < r.ema34

last_early = None
last_confirmed = None

while True:
    try:
        data = exchange.fetch_ohlcv("BTC/USDT", timeframe="1h", limit=100)
        df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

        for p in [5,7,10,13,21,34]:
            df[f"ema{p}"] = df["close"].ewm(span=p).mean()

        live = df.iloc[-1]      # forming candle
        prev = df.iloc[-2]      # last closed candle

        price = live.close

        # ===== EARLY REVERSAL ALERT (DURING BAR) =====
        if (
            price > live.ema5 > live.ema7 > live.ema10 > live.ema13 > live.ema21 > live.ema34
            and bearish(prev)
            and last_early != "LONG"
        ):
            send_alert("⚠️ EARLY LONG (During 3H bar)\nPossible EMA Reversal")
            last_early = "LONG"

        elif (
            price < live.ema5 < live.ema7 < live.ema10 < live.ema13 < live.ema21 < live.ema34
            and bullish(prev)
            and last_early != "SHORT"
        ):
            send_alert("⚠️ EARLY SHORT (During 3H bar)\nPossible EMA Reversal")
            last_early = "SHORT"

        # ===== CONFIRMATION ALERT (AFTER BAR CLOSE) =====
        if bullish(prev) and last_confirmed != "LONG":
            send_alert("✅ CONFIRMED LONG (3H Close)")
            last_confirmed = "LONG"

        elif bearish(prev) and last_confirmed != "SHORT":
            send_alert("✅ CONFIRMED SHORT (3H Close)")
            last_confirmed = "SHORT"

        time.sleep(180)  # check every 3 minutes

    except Exception as e:
        print("Error:", e)
        time.sleep(180)

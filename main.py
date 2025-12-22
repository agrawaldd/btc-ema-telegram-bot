import ccxt
import pandas as pd
import requests
import time

TOKEN = "8569803470:AAHVoYTql3Aijg_hE5m8IsvMXMvEhENGZNA"
CHAT_ID = "5133253214"

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg})

exchange = ccxt.binance()

def check_signal():
    data = exchange.fetch_ohlcv("BTC/USDT", timeframe="3h", limit=100)
    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])

    for p in [5,7,10,13,21,34]:
        df[f"ema{p}"] = df["close"].ewm(span=p).mean()

    cur = df.iloc[-1]
    prev = df.iloc[-2]

    bullish = lambda r: r.ema5 > r.ema7 > r.ema10 > r.ema13 > r.ema21 > r.ema34
    bearish = lambda r: r.ema5 < r.ema7 < r.ema10 < r.ema13 < r.ema21 < r.ema34

    if bullish(cur) and not bullish(prev):
        send_alert("🚀 BTC 3H EMA RIBBON\nLONG SIGNAL")

    if bearish(cur) and not bearish(prev):
        send_alert("🔻 BTC 3H EMA RIBBON\nSHORT SIGNAL")

while True:
    try:
        check_signal()
        time.sleep(300)  # every 5 minutes
    except Exception as e:
        print(e)
        time.sleep(300)

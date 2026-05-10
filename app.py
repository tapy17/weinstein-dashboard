import streamlit as st
import pandas as pd
import yfinance as yf
import requests

st.set_page_config(page_title="Weinstein Level 4 System", layout="wide")

st.title("📊 Weinstein Level 4 (Auto Signal Engine)")

# -----------------------------
# LOAD 750 STOCKS
# -----------------------------
try:
    stocks = pd.read_csv("nse_750.csv", header=None)[0].dropna().tolist()
except:
    st.error("❌ nse_750.csv missing")
    stocks = []

st.write(f"Stocks Loaded: {len(stocks)}")

data = []

# -----------------------------
# TELEGRAM SETUP (OPTIONAL)
# -----------------------------
TELEGRAM_ENABLED = False
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(msg):
    if TELEGRAM_ENABLED:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -----------------------------
# NIFTY REFERENCE
# -----------------------------
nifty = yf.Ticker("^NSEI")
nifty_hist = nifty.history(period="1y")

if not nifty_hist.empty:
    nifty_base = nifty_hist["Close"].iloc[0]
    nifty_now = nifty_hist["Close"].iloc[-1]
else:
    nifty_base = 1
    nifty_now = 1

# -----------------------------
# FAST SCAN ENGINE
# -----------------------------
BATCH_SIZE = 20

for i in range(0, len(stocks), BATCH_SIZE):
    batch = stocks[i:i+BATCH_SIZE]

    for sym in batch:
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="1y")

            if hist.empty:
                continue

            close = hist["Close"].iloc[-1]
            ma150 = hist["Close"].rolling(150).mean().iloc[-1]
            high52 = hist["Close"].max()

            volume = hist["Volume"].iloc[-1]
            avg_vol = hist["Volume"].rolling(20).mean().iloc[-1]

            # -----------------------------
            # REAL RS
            # -----------------------------
            stock_ret = close / hist["Close"].iloc[0]
            nifty_ret = nifty_now / nifty_base
            rs = stock_ret / nifty_ret

            # -----------------------------
            # STAGE LOGIC
            # -----------------------------
            if close > ma150 and rs > 1.1 and volume > avg_vol:
                stage = "Stage 2 Trend"
            elif close >= high52 * 0.95:
                stage = "Stage 2 Breakout"
            elif close < ma150:
                stage = "Stage 3/4 Downtrend"
            else:
                stage = "Stage 1 Base"

            # -----------------------------
            # SIGNAL ENGINE
            # -----------------------------
            score = 0
            if stage == "Stage 2 Trend":
                score += 2
            if rs > 1.2:
                score += 1
            if volume > avg_vol:
                score += 1
            if close > ma150:
                score += 1

            if score >= 4:
                signal = "🔥 BUY NOW"
                send_telegram(f"BUY SIGNAL: {sym} Score:{score} RS:{rs:.2f}")
            elif score == 3:
                signal = "🟡 WATCH"
            else:
                signal = "—"

            data.append([sym, close, rs, stage, score, signal])

        except:
            continue

# -----------------------------
# DATAFRAME
# -----------------------------
df = pd.DataFrame(data, columns=[
    "Stock", "Close", "RS vs Nifty",
    "Stage", "Score", "Signal"
])

# -----------------------------
# OUTPUTS
# -----------------------------

st.subheader("🔥 DAILY ACTION LIST (ONLY BUY NOW)")
st.dataframe(df[df["Signal"] == "🔥 BUY NOW"].sort_values("Score", ascending=False).head(10))

st.subheader("🚀 BREAKOUT WATCHLIST")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])

st.subheader("📈 STRONG MOMENTUM LEADERS")
st.dataframe(df.sort_values("RS vs Nifty", ascending=False).head(10))

st.subheader("⚠️ AVOID ZONE")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])

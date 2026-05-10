import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import time

st.set_page_config(page_title="Weinstein Level 3 System", layout="wide")

st.title("📊 Weinstein Level 3 (750 Stock Trading Engine)")

# -----------------------------
# LOAD UNIVERSE (750 STOCKS)
# -----------------------------
try:
    stocks = pd.read_csv("nse_750.csv", header=None)[0].dropna().tolist()
except:
    st.error("❌ nse_750.csv missing")
    stocks = []

st.write(f"Stocks Loaded: {len(stocks)}")

data = []

# -----------------------------
# OPTIONAL AUTO REFRESH
# -----------------------------
auto_refresh = st.sidebar.checkbox("Auto Refresh (slow)", value=False)

# -----------------------------
# NIFTY INDEX (benchmark)
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
# SCANNER ENGINE (BATCHED)
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
            # REAL RELATIVE STRENGTH
            # -----------------------------
            stock_ret = close / hist["Close"].iloc[0]
            nifty_ret = nifty_now / nifty_base

            rs = stock_ret / nifty_ret

            # -----------------------------
            # WEINSTEIN STAGE
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
            # LEVEL 3 BUY SIGNAL ENGINE
            # -----------------------------
            buy_signal = 0

            if stage == "Stage 2 Trend":
                buy_signal += 2
            if rs > 1.2:
                buy_signal += 1
            if volume > avg_vol:
                buy_signal += 1
            if close > ma150:
                buy_signal += 1

            if buy_signal >= 4:
                signal = "🔥 BUY NOW"
            elif buy_signal == 3:
                signal = "🟡 WATCH"
            else:
                signal = "—"

            # -----------------------------
            # SECTOR MAP
            # -----------------------------
            sector = "Other"
            if "BANK" in sym:
                sector = "Banking"
            elif "IT" in sym:
                sector = "IT"
            elif "RELIANCE" in sym:
                sector = "Energy"

            data.append([sym, close, rs, stage, buy_signal, signal, sector])

        except:
            continue

# -----------------------------
# DATAFRAME
# -----------------------------
df = pd.DataFrame(data, columns=[
    "Stock", "Close", "RS vs Nifty",
    "Stage", "Score", "Signal", "Sector"
])

# -----------------------------
# SECTOR STRENGTH
# -----------------------------
sector_rank = df.groupby("Sector")["RS vs Nifty"].mean().reset_index()
sector_rank = sector_rank.sort_values("RS vs Nifty", ascending=False)

# -----------------------------
# LEVEL 3 OUTPUTS
# -----------------------------

st.subheader("🔥 TOP BUY SIGNALS (ONLY ACTIONABLE)")
st.dataframe(df[df["Signal"] == "🔥 BUY NOW"].sort_values("Score", ascending=False).head(10))

st.subheader("🚀 STAGE 2 BREAKOUTS")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])

st.subheader("📈 RELATIVE STRENGTH LEADERS")
st.dataframe(df.sort_values("RS vs Nifty", ascending=False).head(10))

st.subheader("📊 SECTOR STRENGTH (MONEY FLOW)")
st.dataframe(sector_rank)

st.subheader("⚠️ AVOID ZONE")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])

import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Weinstein Level 2 Pro", layout="wide")

st.title("📊 Weinstein Level 2 Trading Intelligence System")

# -----------------------------
# LOAD UNIVERSE
# -----------------------------
try:
    stocks = pd.read_csv("nse_750.csv", header=None)[0].dropna().tolist()
except:
    st.error("nse_750.csv missing")
    stocks = []

st.write(f"Stocks Loaded: {len(stocks)}")

data = []

# -----------------------------
# NIFTY INDEX (REAL BENCHMARK)
# -----------------------------
nifty = yf.Ticker("^NSEI")
nifty_hist = nifty.history(period="1y")

if not nifty_hist.empty:
    nifty_close = nifty_hist["Close"].iloc[-1]
else:
    nifty_close = 1

# -----------------------------
# SCAN STOCKS
# -----------------------------
BATCH_SIZE = 25

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
            # REAL RELATIVE STRENGTH (vs NIFTY)
            # -----------------------------
            stock_return = close / hist["Close"].iloc[0]
            nifty_return = nifty_close / nifty_hist["Close"].iloc[0]

            rs = stock_return / nifty_return

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
            # SECTOR MAPPING (simple but effective)
            # -----------------------------
            sector = "Other"
            if "BANK" in sym:
                sector = "Banking"
            elif "IT" in sym or "TCS" in sym or "INFY" in sym:
                sector = "IT"
            elif "RELIANCE" in sym:
                sector = "Energy"

            data.append([sym, close, ma150, volume, rs, stage, sector])

        except:
            continue

# -----------------------------
# DATAFRAME
# -----------------------------
df = pd.DataFrame(data, columns=[
    "Stock", "Close", "MA150", "Volume",
    "RS vs Nifty", "Stage", "Sector"
])

# -----------------------------
# SCORE (LEVEL 2 INTELLIGENCE)
# -----------------------------
if not df.empty:
    df["Score"] = (
        df["RS vs Nifty"] * 0.6 +
        (df["Volume"] / df["Volume"].mean()) * 0.4
    )

# -----------------------------
# SECTOR STRENGTH
# -----------------------------
sector_strength = df.groupby("Sector")["RS vs Nifty"].mean().reset_index()
sector_strength = sector_strength.sort_values("RS vs Nifty", ascending=False)

# -----------------------------
# LEVEL 2 OUTPUTS
# -----------------------------

st.subheader("🔥 TOP 5 TRADE SETUPS (ONLY ACTIONABLE)")
top5 = df[df["Stage"] == "Stage 2 Trend"].sort_values("Score", ascending=False).head(5)
st.dataframe(top5)

st.subheader("🚀 BREAKOUT WATCHLIST")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])

st.subheader("📈 STRONGEST STOCKS (RS LEADERS)")
st.dataframe(df.sort_values("RS vs Nifty", ascending=False).head(10))

st.subheader("📊 SECTOR STRENGTH (MONEY FLOW)")
st.dataframe(sector_strength)

st.subheader("⚠️ AVOID LIST")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])

import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="Weinstein Pro Trading Dashboard", layout="wide")

st.title("📊 Weinstein Pro Trading Dashboard (NSE 750 Engine)")

# -----------------------------
# LOAD NSE 750 UNIVERSE
# -----------------------------
try:
    stocks = pd.read_csv("nse_750.csv", header=None)[0].dropna().tolist()
except:
    st.error("❌ nse_750.csv missing in repo root")
    stocks = []

st.write(f"Stocks Loaded: {len(stocks)}")

# -----------------------------
# OPTIONAL AUTO REFRESH
# -----------------------------
refresh = st.sidebar.checkbox("Auto Refresh (slow)", value=False)
if refresh:
    time.sleep(5)
    st.rerun()

data = []

# -----------------------------
# BATCH SCANNER
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
            # RELATIVE STRENGTH (IMPROVED)
            # vs its own past (proxy)
            # -----------------------------
            rs = close / hist["Close"].iloc[0]

            # -----------------------------
            # WEINSTEIN STAGE LOGIC
            # -----------------------------
            if close > ma150 and rs > 1.2 and volume > avg_vol:
                stage = "Stage 2 Trend"
            elif close >= high52 * 0.95:
                stage = "Stage 2 Breakout"
            elif close < ma150:
                stage = "Stage 3/4 Downtrend"
            else:
                stage = "Stage 1 Base"

            # Sector (simple mapping)
            sector = "Other"
            if "BANK" in sym:
                sector = "Banking"
            elif "IT" in sym or "TCS" in sym or "INFY" in sym:
                sector = "IT"
            elif "RELIANCE" in sym:
                sector = "Energy"

            data.append([sym, close, ma150, high52, volume, rs, stage, sector])

        except:
            continue

# -----------------------------
# DATAFRAME
# -----------------------------
df = pd.DataFrame(data, columns=[
    "Stock", "Close", "MA150", "52W High",
    "Volume", "RS Proxy", "Stage", "Sector"
])

# -----------------------------
# SCORE SYSTEM (MOMENTUM RANK)
# -----------------------------
if not df.empty:
    df["Score"] = (
        df["RS Proxy"] * 0.5 +
        (df["Volume"] / df["Volume"].mean()) * 0.3 +
        (df["Close"] / df["MA150"]) * 0.2
    )
else:
    df["Score"] = 0

# -----------------------------
# DASHBOARD UI
# -----------------------------
st.subheader("📌 Full Market Scan")
st.dataframe(df, use_container_width=True)

# -----------------------------
# TOP BUY LIST
# -----------------------------
st.subheader("🔥 Top 10 Momentum Leaders (BUY WATCHLIST)")
st.dataframe(
    df[df["Stage"] == "Stage 2 Trend"]
    .sort_values(["Score", "RS Proxy"], ascending=False)
    .head(10)
)

# -----------------------------
# BREAKOUT ZONE
# -----------------------------
st.subheader("🚀 Breakout Watchlist")
st.dataframe(
    df[df["Stage"] == "Stage 2 Breakout"]
    .sort_values("RS Proxy", ascending=False)
)

# -----------------------------
# BASE ACCUMULATION
# -----------------------------
st.subheader("🟡 Stage 1 Base (Accumulation Zone)")
st.dataframe(df[df["Stage"] == "Stage 1 Base"])

# -----------------------------
# AVOID ZONE
# -----------------------------
st.subheader("⚠️ Weak / Avoid Stocks")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])

# -----------------------------
# SECTOR VIEW
# -----------------------------
st.subheader("📊 Sector Breakdown (Basic)")
st.dataframe(df.groupby("Sector").size().reset_index(name="Count"))

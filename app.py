import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Weinstein Pro Scanner", layout="wide")

st.title("📊 Weinstein Pro Stock Scanner (NSE 750 Ready)")

# -----------------------------
# LOAD NSE UNIVERSE
# -----------------------------
try:
    stocks = pd.read_csv("nse_750.csv", header=None)[0].dropna().tolist()
except:
    st.error("nse_750.csv not found in repo root")
    stocks = []

st.write(f"Stocks loaded: {len(stocks)}")

data = []

# -----------------------------
# SCAN STOCKS (BATCH SAFE)
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

            data.append([sym, close, ma150, high52, volume, rs, stage])

        except:
            continue

# -----------------------------
# CREATE DATAFRAME
# -----------------------------
df = pd.DataFrame(data, columns=[
    "Stock", "Close", "MA150", "52W High",
    "Volume", "RS Proxy", "Stage"
])

# -----------------------------
# ADD SCORE (PRO UPGRADE)
# -----------------------------
df["Score"] = (
    df["RS Proxy"] * 0.5 +
    (df["Volume"] / df["Volume"].mean()) * 0.3 +
    (df["Close"] / df["MA150"]) * 0.2
)

# -----------------------------
# DASHBOARD SECTIONS
# -----------------------------
st.subheader("📌 Full Market Scan")
st.dataframe(df, use_container_width=True)

st.subheader("🔥 Top 10 Buy Candidates (Stage 2 Leaders)")
top = df[df["Stage"] == "Stage 2 Trend"].sort_values("Score", ascending=False).head(10)
st.dataframe(top)

st.subheader("🚀 Breakout Watchlist")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])

st.subheader("🟡 Stage 1 Base Stocks")
st.dataframe(df[df["Stage"] == "Stage 1 Base"])

st.subheader("⚠️ Weak / Avoid Stocks")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])

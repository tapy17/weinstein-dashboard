import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Weinstein Stage Dashboard", layout="wide")

st.title("📊 Weinstein Stage Stock Scanner (NSE 750 Ready)")

# -----------------------------
# LOAD UNIVERSE (FROM CSV)
# -----------------------------
try:
    stocks = pd.read_csv("nse_750.csv", header=None)[0].dropna().tolist()
except:
    st.error("nse_750.csv not found. Please upload it in GitHub repo root.")
    stocks = []

st.write(f"Total stocks loaded: {len(stocks)}")

data = []

# -----------------------------
# SAFETY BATCHING
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
# DATAFRAME
# -----------------------------
df = pd.DataFrame(data, columns=[
    "Stock", "Close", "MA150", "52W High",
    "Volume", "RS Proxy", "Stage"
])

st.subheader("📌 Full Scan Results")
st.dataframe(df, use_container_width=True)

# -----------------------------
# FILTERED SCREENS
# -----------------------------
st.subheader("🟢 Stage 2 Breakouts")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])

st.subheader("🟡 Stage 2 Trends")
st.dataframe(df[df["Stage"] == "Stage 2 Trend"])

st.subheader("🟠 Stage 1 Bases")
st.dataframe(df[df["Stage"] == "Stage 1 Base"])

st.subheader("🔴 Weak Stocks")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])
st.subheader("🏆 Top Stage 2 Leaders (Best Momentum)")
st.dataframe(
    df[df["Stage"] == "Stage 2 Trend"]
    .sort_values("RS Proxy", ascending=False)
    .head(10)
)
st.subheader("🚀 Breakout Watchlist (Near 52W High)")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])
st.subheader("📈 Strongest Relative Strength Stocks")
st.dataframe(df.sort_values("RS Proxy", ascending=False).head(15))
st.subheader("🔥 Top 10 Trade Candidates (Stage 2 Leaders)")

top = df[df["Stage"] == "Stage 2 Trend"].sort_values(
    "RS Proxy", ascending=False
).head(10)

st.dataframe(top)
st.subheader("🚀 High Probability Breakouts")

st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])
st.subheader("⚠️ Weak / Avoid Stocks")

st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])


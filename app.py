import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Weinstein Stage Dashboard", layout="wide")

st.title("📊 Weinstein Stage Stock Dashboard")

# -----------------------------
# NIFTY 50 SAMPLE UNIVERSE
# -----------------------------
stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS",
    "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "LT.NS", "ITC.NS",
    "BHARTIARTL.NS", "AXISBANK.NS"
]

data = []

# -----------------------------
# SCANNER LOGIC
# -----------------------------
for sym in stocks:
    try:
        ticker = yf.Ticker(sym)
        hist = ticker.history(period="1y")

        if hist.empty:
            continue

        close = hist["Close"][-1]

        # 30W MA proxy (150 trading days)
        ma30 = hist["Close"].rolling(150).mean().iloc[-1]

        high52 = hist["Close"].max()

        volume = hist["Volume"][-1]
        avg_vol = hist["Volume"].rolling(20).mean().iloc[-1]

        # simple RS proxy
        rs = close / hist["Close"].iloc[0]

        # -----------------------------
        # WEINSTEIN STAGE LOGIC
        # -----------------------------
        if close > ma30 and rs > 1.2 and volume > avg_vol:
            stage = "Stage 2 Trend"
        elif close > ma30 and close >= high52 * 0.95:
            stage = "Stage 2 Breakout"
        elif close < ma30:
            stage = "Stage 3/4 Downtrend"
        else:
            stage = "Stage 1 Base"

        data.append([sym, close, ma30, high52, volume, avg_vol, rs, stage])

    except:
        continue

df = pd.DataFrame(data, columns=[
    "Stock", "Close", "MA30 Proxy", "52W High",
    "Volume", "Avg Volume", "RS Proxy", "Stage"
])

st.subheader("📌 Full Scan Results")
st.dataframe(df, use_container_width=True)

st.subheader("🟢 Stage 2 Breakouts")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])

st.subheader("🟡 Stage 2 Trends")
st.dataframe(df[df["Stage"] == "Stage 2 Trend"])

st.subheader("🟠 Stage 1 Bases")
st.dataframe(df[df["Stage"] == "Stage 1 Base"])

st.subheader("🔴 Avoid List")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])

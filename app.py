import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Weinstein Dashboard", layout="wide")

st.title("📊 Weinstein Stage Dashboard (Stable Version)")

import pandas as pd

stocks = pd.read_csv("nse_750.csv", header=None)[0].tolist()
]

data = []

for sym in stocks:
    ticker = yf.Ticker(sym)
    hist = ticker.history(period="1y")

    if hist is None or hist.empty:
        st.warning(f"No data for {sym}")
        continue

    close = hist["Close"].iloc[-1]

    ma = hist["Close"].rolling(150).mean().iloc[-1]

    high52 = hist["Close"].max()

    volume = hist["Volume"].iloc[-1]
    avg_vol = hist["Volume"].rolling(20).mean().iloc[-1]

    rs = close / hist["Close"].iloc[0]

    if close > ma and rs > 1.2 and volume > avg_vol:
        stage = "Stage 2 Trend"
    elif close >= high52 * 0.95:
        stage = "Stage 2 Breakout"
    elif close < ma:
        stage = "Stage 3/4 Downtrend"
    else:
        stage = "Stage 1 Base"

    data.append([sym, close, ma, high52, volume, rs, stage])

df = pd.DataFrame(data, columns=[
    "Stock", "Close", "MA150", "52W High",
    "Volume", "RS Proxy", "Stage"
])

st.subheader("📌 Full Results")
st.dataframe(df, use_container_width=True)

st.subheader("🟢 Stage 2 Breakouts")
st.dataframe(df[df["Stage"] == "Stage 2 Breakout"])

st.subheader("🟡 Stage 2 Trends")
st.dataframe(df[df["Stage"] == "Stage 2 Trend"])

st.subheader("🟠 Stage 1 Base")
st.dataframe(df[df["Stage"] == "Stage 1 Base"])

st.subheader("🔴 Weak Stocks")
st.dataframe(df[df["Stage"] == "Stage 3/4 Downtrend"])

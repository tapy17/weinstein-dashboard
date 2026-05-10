import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Debug Data Fetch Test")

stocks = ["RELIANCE.NS", "TCS.NS"]

data = []

for sym in stocks:
    ticker = yf.Ticker(sym)
    hist = ticker.history(period="5d")

    st.write(sym, hist.tail())  # 👈 THIS SHOWS RAW DATA

    if not hist.empty:
        data.append([sym, hist["Close"].iloc[-1]])

df = pd.DataFrame(data, columns=["Stock", "Close"])

st.dataframe(df)

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weinstein Dashboard", layout="wide")

st.title("📊 Weinstein Stage Dashboard")

st.write("System is live 🚀")

# sample data placeholder
data = {
    "Stock": ["RELIANCE", "TCS", "INFY"],
    "Stage": ["Stage 2 Trend", "Stage 1 Base", "Stage 3 Downtrend"]
}

df = pd.DataFrame(data)

st.dataframe(df)

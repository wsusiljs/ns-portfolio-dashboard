import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

from utils.data_loader import load_data
from utils.filters import filter_data

st.title("📈 Performance")

owner_account = st.sidebar.selectbox(
    "Select Account",
    [
        "ALL",
        "Nilmini-TFSA",
        "Nilmini-INV",
        "Susil-TFSA",
        "Susil-INV"
    ]
)

df = load_data()

df = filter_data(df, owner_account)

symbols = df["Yahoo Finance Symbol"].unique().tolist()

prices = yf.download(
    symbols,
    period="1y",
    interval="1d",
    progress=False
)["Close"]

prices = prices.ffill()

if isinstance(prices, pd.Series):
    prices = prices.to_frame()

cad_series = pd.Series(
    0,
    index=prices.index
)

usd_series = pd.Series(
    0,
    index=prices.index
)

for _, row in df.iterrows():

    ticker = row["Yahoo Finance Symbol"]
    qty = row["Quantity"]
    currency = row["Currency"]

    if ticker in prices:

        series = prices[ticker] * qty

        if currency == "CAD":
            cad_series = cad_series.add(
                series,
                fill_value=0
            )
        else:
            usd_series = usd_series.add(
                series,
                fill_value=0
            )

perf_df = pd.DataFrame({
    "CAD": cad_series,
    "USD": usd_series
})

fig = px.line(
    perf_df,
    y=["CAD", "USD"]
)

fig.update_layout(height=500)

st.plotly_chart(
    fig,
    use_container_width=True
)

import streamlit as st
import plotly.graph_objects as go
import yfinance as yf

from utils.data_loader import load_data
from utils.filters import filter_data
from utils.price_fetcher import get_realtime_prices

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gain Loss",
    layout="wide"
)

st.title("📊 Gain / Loss")

# =========================================================
# SIDEBAR
# =========================================================

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

# =========================================================
# FX
# =========================================================

@st.cache_data(ttl=300)
def get_fx_rate_usd_cad():

    try:

        ticker = yf.Ticker("CAD=X")

        fx = ticker.fast_info.get("lastPrice")

        if fx is None:
            fx = ticker.history(period="1d")["Close"].iloc[-1]

        return float(fx)

    except:
        return 1.35

# =========================================================
# LOAD DATA
# =========================================================

df = load_data()

df = filter_data(df, owner_account)

symbols = df["Yahoo Finance Symbol"].unique().tolist()

price_map = get_realtime_prices(symbols)

df["Price"] = (
    df["Yahoo Finance Symbol"]
    .map(price_map)
    .fillna(0)
)

df["Value"] = (
    df["Quantity"]
    * df["Price"]
)

df["Cost"] = (
    df["Quantity"]
    * df["Average Cost"]
)

df["GainLoss"] = (
    df["Value"]
    - df["Cost"]
)

# =========================================================
# SPLIT CAD/USD
# =========================================================

cad_df = df[df["Currency"] == "CAD"]

usd_df = df[df["Currency"] == "USD"]

col1, col2 = st.columns(2)

# =========================================================
# CAD CHART
# =========================================================

with col1:

    st.subheader("CAD Gain/Loss")

    cad_fig = go.Figure()

    cad_fig.add_trace(
        go.Bar(
            x=cad_df["Yahoo Finance Symbol"],
            y=cad_df["GainLoss"],
            marker_color=[
                "green" if v >= 0 else "red"
                for v in cad_df["GainLoss"]
            ],
            text=cad_df["GainLoss"].round(0),
            textposition="outside"
        )
    )

    cad_fig.update_layout(
        height=500
    )

    st.plotly_chart(
        cad_fig,
        use_container_width=True
    )

# =========================================================
# USD CHART
# =========================================================

with col2:

    st.subheader("USD Gain/Loss")

    usd_fig = go.Figure()

    usd_fig.add_trace(
        go.Bar(
            x=usd_df["Yahoo Finance Symbol"],
            y=usd_df["GainLoss"],
            marker_color=[
                "green" if v >= 0 else "red"
                for v in usd_df["GainLoss"]
            ],
            text=usd_df["GainLoss"].round(0),
            textposition="outside"
        )
    )

    usd_fig.update_layout(
        height=500
    )

    st.plotly_chart(
        usd_fig,
        use_container_width=True
    )

# =========================================================
# TOTALS
# =========================================================

cad_net = cad_df["GainLoss"].sum()

usd_net = usd_df["GainLoss"].sum()

fx_rate = get_fx_rate_usd_cad()

total_net_cad = cad_net + usd_net * fx_rate

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "CAD Gain/Loss",
        f"{cad_net:,.0f}"
    )

with c2:

    st.metric(
        "USD Gain/Loss",
        f"{usd_net:,.0f}"
    )

with c3:

    st.metric(
        "Total Net (CAD)",
        f"{total_net_cad:,.0f}"
    )

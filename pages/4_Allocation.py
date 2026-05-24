import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.filters import filter_data
from utils.price_fetcher import get_realtime_prices

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Allocation",
    layout="wide"
)

st.title("🥧 Portfolio Allocation")

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

# =========================================================
# CAD / USD ALLOCATION
# =========================================================

cad_df = (
    df[df["Currency"] == "CAD"]
    .groupby("Yahoo Finance Symbol")["Value"]
    .sum()
    .reset_index()
)

usd_df = (
    df[df["Currency"] == "USD"]
    .groupby("Yahoo Finance Symbol")["Value"]
    .sum()
    .reset_index()
)

col1, col2 = st.columns(2)

# =========================================================
# CAD PIE
# =========================================================

with col1:

    st.subheader("CAD Allocation")

    if not cad_df.empty:

        cad_fig = px.pie(
            cad_df,
            names="Yahoo Finance Symbol",
            values="Value",
            hole=0.4
        )

        cad_fig.update_traces(
            textposition="inside",
            textinfo="label+percent"
        )

        cad_fig.update_layout(
            height=500
        )

        st.plotly_chart(
            cad_fig,
            use_container_width=True
        )

# =========================================================
# USD PIE
# =========================================================

with col2:

    st.subheader("USD Allocation")

    if not usd_df.empty:

        usd_fig = px.pie(
            usd_df,
            names="Yahoo Finance Symbol",
            values="Value",
            hole=0.4
        )

        usd_fig.update_traces(
            textposition="inside",
            textinfo="label+percent"
        )

        usd_fig.update_layout(
            height=500
        )

        st.plotly_chart(
            usd_fig,
            use_container_width=True
        )

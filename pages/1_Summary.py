import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.filters import filter_data
from utils.price_fetcher import get_realtime_prices

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Portfolio Summary",
    layout="wide"
)

st.title("📊 Portfolio Summary")

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

# =========================================================
# REALTIME VALUES
# =========================================================

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
# TOTALS
# =========================================================

cad_total = round(
    df[df["Currency"] == "CAD"]["Value"].sum()
)

usd_total = round(
    df[df["Currency"] == "USD"]["Value"].sum()
)

# =========================================================
# KPI CARDS
# =========================================================

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Canadian Portfolio",
        f"{cad_total:,.0f} CAD"
    )

with c2:

    st.metric(
        "US Portfolio",
        f"{usd_total:,.0f} USD"
    )

# =========================================================
# PIE CHART
# =========================================================

pie_fig = px.pie(
    names=["Canada", "US"],
    values=[cad_total, usd_total],
    hole=0.4
)

pie_fig.update_layout(
    height=400
)

# =========================================================
# BREAKDOWN FUNCTION
# =========================================================

def prepare_breakdown(currency):

    accounts = [
        "Nilmini-TFSA",
        "Nilmini-INV",
        "Susil-TFSA",
        "Susil-INV"
    ]

    rows = []

    for acc in accounts:

        owner, acct = acc.split("-")

        val = df[
            (df["Currency"] == currency)
            & (df["Owner"] == owner)
            & (df["Account"].str.contains(acct))
        ]["Value"].sum()

        rows.append({
            "Account": acc,
            "Value": val
        })

    return (
        pd.DataFrame(rows)
        .sort_values("Value", ascending=False)
    )

# =========================================================
# CANADA BREAKDOWN
# =========================================================

canada_df = prepare_breakdown("CAD")

canada_fig = px.bar(
    canada_df,
    x="Account",
    y="Value",
    text="Value",
    title="Canada Breakdown"
)

canada_fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

canada_fig.update_layout(
    height=400
)

# =========================================================
# US BREAKDOWN
# =========================================================

us_df = prepare_breakdown("USD")

us_fig = px.bar(
    us_df,
    x="Account",
    y="Value",
    text="Value",
    title="US Breakdown"
)

us_fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

us_fig.update_layout(
    height=400
)

# =========================================================
# DISPLAY CHARTS
# =========================================================

col1, col2, col3 = st.columns([1,1,1])

with col1:

    st.plotly_chart(
        canada_fig,
        use_container_width=True
    )

with col2:

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

with col3:

    st.plotly_chart(
        us_fig,
        use_container_width=True
    )

# =========================================================
# MOBILE OPTIMIZATION
# =========================================================

st.divider()

st.caption(
    "Dashboard optimized for desktop and mobile viewing."
)

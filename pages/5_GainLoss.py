# =========================================================
# pages/5_GainLoss.py
# Mobile-First Gain / Loss Dashboard
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.filters import filter_data
from utils.sidebar import render_sidebar
from utils.price_fetcher import get_realtime_prices
from utils.styles import style_fig

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gain / Loss",
    layout="wide"
)

st.title("📊 Gain / Loss Dashboard")

# =========================================================
# SIDEBAR
# =========================================================

owner_account = render_sidebar()

# =========================================================
# LOAD DATA
# =========================================================

df = load_data()

df = filter_data(df, owner_account)

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [
    "Yahoo Finance Symbol",
    "Quantity",
    "Average Cost",
    "Currency"
]

missing_cols = [
    col for col in required_cols
    if col not in df.columns
]

if len(missing_cols) > 0:

    st.error(
        f"Missing columns: {missing_cols}"
    )

    st.write("Available columns:")

    st.write(df.columns.tolist())

    st.stop()

# =========================================================
# CLEAN DATA
# =========================================================

df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
).fillna(0)

df["Average Cost"] = pd.to_numeric(
    df["Average Cost"],
    errors="coerce"
).fillna(0)

# =========================================================
# GET REALTIME PRICES
# =========================================================

symbols = df[
    "Yahoo Finance Symbol"
].unique().tolist()

price_map = get_realtime_prices(symbols)

df["Current Price"] = (
    df["Yahoo Finance Symbol"]
    .map(price_map)
)

df["Current Price"] = pd.to_numeric(
    df["Current Price"],
    errors="coerce"
).fillna(0)

# =========================================================
# CALCULATIONS
# =========================================================

# Book Value = Average Cost per Share × Quantity

df["Book Value"] = (
    df["Average Cost"]
    * df["Quantity"]
)

# Market Value = Current Price × Quantity

df["Market Value"] = (
    df["Current Price"]
    * df["Quantity"]
)

# Gain / Loss

df["Gain/Loss"] = (
    df["Market Value"]
    - df["Book Value"]
)

# Gain / Loss %

df["Gain/Loss %"] = (
    df["Gain/Loss"]
    / df["Book Value"]
) * 100

df["Gain/Loss %"] = (
    df["Gain/Loss %"]
    .replace([float("inf"), -float("inf")], 0)
    .fillna(0)
)

# =========================================================
# SPLIT CAD / USD
# =========================================================

cad_df = df[
    df["Currency"] == "CAD"
].copy()

usd_df = df[
    df["Currency"] == "USD"
].copy()

# =========================================================
# KPI SUMMARY
# =========================================================

st.subheader("Portfolio Gain / Loss Summary")

cad_gain = cad_df[
    "Gain/Loss"
].sum()

usd_gain = usd_df[
    "Gain/Loss"
].sum()

cad_market = cad_df[
    "Market Value"
].sum()

usd_market = usd_df[
    "Market Value"
].sum()

# =========================================================
# KPI ROW
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🇨🇦 CAD Gain/Loss",
        f"{cad_gain:,.0f} CAD"
    )

with col2:

    st.metric(
        "🇺🇸 USD Gain/Loss",
        f"{usd_gain:,.0f} USD"
    )

col3, col4 = st.columns(2)

with col3:

    st.metric(
        "🇨🇦 CAD Market Value",
        f"{cad_market:,.0f} CAD"
    )

with col4:

    st.metric(
        "🇺🇸 USD Market Value",
        f"{usd_market:,.0f} USD"
    )

# =========================================================
# CANADIAN GAIN / LOSS
# =========================================================

st.divider()

st.subheader("🇨🇦 Canadian Holdings")

if not cad_df.empty:

    cad_chart = cad_df[
        [
            "Yahoo Finance Symbol",
            "Gain/Loss"
        ]
    ].sort_values(
        "Gain/Loss"
    )

    cad_fig = px.bar(
        cad_chart,
        x="Gain/Loss",
        y="Yahoo Finance Symbol",
        orientation="h",
        text_auto=".0f"
    )

    cad_fig.update_layout(
        yaxis_title="",
        xaxis_title="Gain / Loss",
        showlegend=False
    )

    cad_fig = style_fig(
        cad_fig,
        height=600
    )

    st.plotly_chart(
        cad_fig,
        use_container_width=True
    )

else:

    st.info(
        "No Canadian holdings found."
    )

# =========================================================
# US GAIN / LOSS
# =========================================================

st.divider()

st.subheader("🇺🇸 US Holdings")

if not usd_df.empty:

    usd_chart = usd_df[
        [
            "Yahoo Finance Symbol",
            "Gain/Loss"
        ]
    ].sort_values(
        "Gain/Loss"
    )

    usd_fig = px.bar(
        usd_chart,
        x="Gain/Loss",
        y="Yahoo Finance Symbol",
        orientation="h",
        text_auto=".0f"
    )

    usd_fig.update_layout(
        yaxis_title="",
        xaxis_title="Gain / Loss",
        showlegend=False
    )

    usd_fig = style_fig(
        usd_fig,
        height=600
    )

    st.plotly_chart(
        usd_fig,
        use_container_width=True
    )

else:

    st.info(
        "No US holdings found."
    )

# =========================================================
# GAIN / LOSS %
# =========================================================

st.divider()

st.subheader("Gain / Loss %")

percent_df = df[
    [
        "Yahoo Finance Symbol",
        "Currency",
        "Gain/Loss %",
        "Gain/Loss"
    ]
].sort_values(
    "Gain/Loss %",
    ascending=False
)

percent_fig = px.bar(
    percent_df.head(20),
    x="Yahoo Finance Symbol",
    y="Gain/Loss %",
    color="Currency",
    text_auto=".1f"
)

percent_fig.update_layout(
    yaxis_title="Return %",
    xaxis_title="",
    legend_title=""
)

percent_fig = style_fig(
    percent_fig,
    height=500
)

st.plotly_chart(
    percent_fig,
    use_container_width=True
)

# =========================================================
# TOP WINNERS
# =========================================================

st.divider()

st.subheader("Top Winners")

winners_df = df.sort_values(
    "Gain/Loss",
    ascending=False
).head(10)

winners_fig = px.bar(
    winners_df,
    x="Yahoo Finance Symbol",
    y="Gain/Loss",
    color="Currency",
    text_auto=".0f"
)

winners_fig.update_layout(
    yaxis_title="Gain",
    xaxis_title="",
    legend_title=""
)

winners_fig = style_fig(
    winners_fig,
    height=450
)

st.plotly_chart(
    winners_fig,
    use_container_width=True
)

# =========================================================
# TOP LOSERS
# =========================================================

st.divider()

st.subheader("Top Losers")

losers_df = df.sort_values(
    "Gain/Loss",
    ascending=True
).head(10)

losers_fig = px.bar(
    losers_df,
    x="Yahoo Finance Symbol",
    y="Gain/Loss",
    color="Currency",
    text_auto=".0f"
)

losers_fig.update_layout(
    yaxis_title="Loss",
    xaxis_title="",
    legend_title=""
)

losers_fig = style_fig(
    losers_fig,
    height=450
)

st.plotly_chart(
    losers_fig,
    use_container_width=True
)

# =========================================================
# HOLDINGS TABLE
# =========================================================

st.divider()

st.subheader("Gain / Loss Details")

display_df = df[
    [
        "Yahoo Finance Symbol",
        "Currency",
        "Quantity",
        "Average Cost",
        "Current Price",
        "Book Value",
        "Market Value",
        "Gain/Loss",
        "Gain/Loss %"
    ]
].copy()

display_df = display_df.sort_values(
    "Gain/Loss",
    ascending=False
)

display_df = display_df.round(2)

st.dataframe(
    display_df,
    use_container_width=True,
    height=700
)

# =========================================================
# DOWNLOAD CSV
# =========================================================

csv = display_df.to_csv(index=False)

st.download_button(
    "⬇ Download Gain/Loss Data",
    csv,
    "gain_loss.csv",
    "text/csv"
)

# =========================================================
# SUMMARY STATISTICS
# =========================================================

with st.expander("Show Portfolio Statistics"):

    total_gain = df[
        "Gain/Loss"
    ].sum()

    total_book = df[
        "Book Value"
    ].sum()

    total_market = df[
        "Market Value"
    ].sum()

    total_return = (
        total_gain / total_book
    ) * 100 if total_book > 0 else 0

    st.write(
        f"Total Portfolio Book Value: "
        f"{total_book:,.0f}"
    )

    st.write(
        f"Total Portfolio Market Value: "
        f"{total_market:,.0f}"
    )

    st.write(
        f"Total Portfolio Gain/Loss: "
        f"{total_gain:,.0f}"
    )

    st.write(
        f"Overall Portfolio Return: "
        f"{total_return:.2f}%"
    )

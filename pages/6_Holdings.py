# =========================================================
# pages/6_Holdings.py
# Mobile-First Holdings Dashboard
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
    page_title="Holdings",
    layout="wide"
)

st.title("📋 Holdings Dashboard")

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
# REALTIME PRICES
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

df["Book Value"] = (
    df["Average Cost"]
    * df["Quantity"]
)

df["Market Value"] = (
    df["Current Price"]
    * df["Quantity"]
)

df["Gain/Loss"] = (
    df["Market Value"]
    - df["Book Value"]
)

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
# OPTIONAL YTD %
# =========================================================

if "YTD %" not in df.columns:

    df["YTD %"] = 0

# =========================================================
# KPI SUMMARY
# =========================================================

st.subheader("Portfolio Summary")

total_book = df[
    "Book Value"
].sum()

total_market = df[
    "Market Value"
].sum()

total_gain = df[
    "Gain/Loss"
].sum()

total_return = (
    total_gain / total_book
) * 100 if total_book > 0 else 0

# =========================================================
# KPI CARDS
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "💼 Book Value",
        f"{total_book:,.0f}"
    )

with col2:

    st.metric(
        "💰 Market Value",
        f"{total_market:,.0f}"
    )

col3, col4 = st.columns(2)

with col3:

    st.metric(
        "📈 Total Gain/Loss",
        f"{total_gain:,.0f}"
    )

with col4:

    st.metric(
        "📊 Portfolio Return",
        f"{total_return:.2f}%"
    )

# =========================================================
# FILTERS
# =========================================================

st.divider()

st.subheader("Filters")

currency_filter = st.multiselect(
    "Select Currency",
    options=df["Currency"].unique(),
    default=df["Currency"].unique()
)

filtered_df = df[
    df["Currency"].isin(currency_filter)
]

# =========================================================
# HOLDINGS TABLE
# =========================================================

st.divider()

st.subheader("Holdings Table")

display_df = filtered_df[
    [
        "Yahoo Finance Symbol",
        "Currency",
        "Quantity",
        "Average Cost",
        "Current Price",
        "Book Value",
        "Market Value",
        "Gain/Loss",
        "Gain/Loss %",
        "YTD %"
    ]
].copy()

display_df = display_df.sort_values(
    "Market Value",
    ascending=False
)

display_df = display_df.round(2)

# =========================================================
# CONDITIONAL FORMATTING
# =========================================================

def color_gain_loss(val):

    if val > 0:
        return "color: lime"

    elif val < 0:
        return "color: red"

    return ""

styled_df = display_df.style.map(
    color_gain_loss,
    subset=[
        "Gain/Loss",
        "Gain/Loss %"
    ]
)

st.dataframe(
    styled_df,
    use_container_width=True,
    height=700
)

# =========================================================
# MARKET VALUE DISTRIBUTION
# =========================================================

st.divider()

st.subheader("Market Value Distribution")

top_holdings = display_df.head(15)

dist_fig = px.bar(
    top_holdings,
    x="Yahoo Finance Symbol",
    y="Market Value",
    color="Currency",
    text_auto=".0f"
)

dist_fig.update_layout(
    yaxis_title="Market Value",
    xaxis_title="",
    legend_title=""
)

dist_fig = style_fig(
    dist_fig,
    height=500
)

st.plotly_chart(
    dist_fig,
    use_container_width=True
)

# =========================================================
# GAIN / LOSS DISTRIBUTION
# =========================================================

st.divider()

st.subheader("Gain / Loss Distribution")

gain_fig = px.bar(
    top_holdings,
    x="Yahoo Finance Symbol",
    y="Gain/Loss",
    color="Currency",
    text_auto=".0f"
)

gain_fig.update_layout(
    yaxis_title="Gain / Loss",
    xaxis_title="",
    legend_title=""
)

gain_fig = style_fig(
    gain_fig,
    height=500
)

st.plotly_chart(
    gain_fig,
    use_container_width=True
)

# =========================================================
# PORTFOLIO ALLOCATION
# =========================================================

st.divider()

st.subheader("Holdings Allocation")

alloc_fig = px.pie(
    top_holdings,
    names="Yahoo Finance Symbol",
    values="Market Value",
    hole=0.45
)

alloc_fig.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

alloc_fig = style_fig(
    alloc_fig,
    height=600
)

st.plotly_chart(
    alloc_fig,
    use_container_width=True
)

# =========================================================
# DOWNLOAD CSV
# =========================================================

st.divider()

csv = display_df.to_csv(index=False)

st.download_button(
    "⬇ Download Holdings Data",
    csv,
    "holdings.csv",
    "text/csv"
)

# =========================================================
# OPTIONAL RAW DATA
# =========================================================

with st.expander("Show Raw Data"):

    st.dataframe(
        filtered_df.round(2),
        use_container_width=True
    )

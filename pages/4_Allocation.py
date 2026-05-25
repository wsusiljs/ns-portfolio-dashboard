# =========================================================
# pages/4_Allocation.py
# Mobile-First Portfolio Allocation Dashboard
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
    page_title="Allocation",
    layout="wide"
)

st.title("🥧 Portfolio Allocation")

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
# GET REALTIME PRICES
# =========================================================

symbols = df[
    "Yahoo Finance Symbol"
].unique().tolist()

price_map = get_realtime_prices(symbols)

df["Price"] = (
    df["Yahoo Finance Symbol"]
    .map(price_map)
)

# =========================================================
# MARKET VALUE
# =========================================================

df["Market Value"] = (
    df["Price"]
    * df["Quantity"]
)

# =========================================================
# REMOVE ZERO VALUES
# =========================================================

df = df[
    df["Market Value"] > 0
]

if df.empty:

    st.warning(
        "No valid holdings found."
    )

    st.stop()

# =========================================================
# KPI SUMMARY
# =========================================================

st.subheader("Allocation Summary")

cad_total = df[
    df["Currency"] == "CAD"
]["Market Value"].sum()

usd_total = df[
    df["Currency"] == "USD"
]["Market Value"].sum()

combined_total = (
    cad_total + usd_total
)

st.metric(
    "🇨🇦 Canadian Holdings",
    f"{cad_total:,.0f} CAD"
)

st.metric(
    "🇺🇸 US Holdings",
    f"{usd_total:,.0f} USD"
)

st.metric(
    "🌎 Total Holdings",
    f"{combined_total:,.0f}"
)

# =========================================================
# OVERALL MARKET ALLOCATION
# =========================================================

st.divider()

st.subheader("Market Allocation")

market_df = pd.DataFrame({
    "Market": ["Canada", "US"],
    "Value": [cad_total, usd_total]
})

market_fig = px.pie(
    market_df,
    names="Market",
    values="Value",
    hole=0.45
)

market_fig.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

market_fig = style_fig(
    market_fig,
    height=500
)

st.plotly_chart(
    market_fig,
    use_container_width=True
)

# =========================================================
# CANADIAN STOCK ALLOCATION
# =========================================================

st.divider()

st.subheader("🇨🇦 Canadian Portfolio Allocation")

cad_df = df[
    df["Currency"] == "CAD"
].copy()

if not cad_df.empty:

    cad_alloc = (
        cad_df.groupby(
            "Yahoo Finance Symbol"
        )["Market Value"]
        .sum()
        .reset_index()
    )

    cad_alloc = cad_alloc.sort_values(
        "Market Value",
        ascending=False
    )

    cad_fig = px.pie(
        cad_alloc,
        names="Yahoo Finance Symbol",
        values="Market Value",
        hole=0.45
    )

    cad_fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    cad_fig = style_fig(
        cad_fig,
        height=650
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
# US STOCK ALLOCATION
# =========================================================

st.divider()

st.subheader("🇺🇸 US Portfolio Allocation")

usd_df = df[
    df["Currency"] == "USD"
].copy()

if not usd_df.empty:

    usd_alloc = (
        usd_df.groupby(
            "Yahoo Finance Symbol"
        )["Market Value"]
        .sum()
        .reset_index()
    )

    usd_alloc = usd_alloc.sort_values(
        "Market Value",
        ascending=False
    )

    usd_fig = px.pie(
        usd_alloc,
        names="Yahoo Finance Symbol",
        values="Market Value",
        hole=0.45
    )

    usd_fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    usd_fig = style_fig(
        usd_fig,
        height=650
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
# TOP HOLDINGS
# =========================================================

st.divider()

st.subheader("Top Holdings")

top_df = (
    df.groupby(
        [
            "Yahoo Finance Symbol",
            "Currency"
        ]
    )["Market Value"]
    .sum()
    .reset_index()
)

top_df = top_df.sort_values(
    "Market Value",
    ascending=False
)

top_fig = px.bar(
    top_df.head(15),
    x="Yahoo Finance Symbol",
    y="Market Value",
    color="Currency",
    text_auto=".0f"
)

top_fig.update_layout(
    yaxis_title="Market Value",
    xaxis_title="",
    legend_title=""
)

top_fig = style_fig(
    top_fig,
    height=500
)

st.plotly_chart(
    top_fig,
    use_container_width=True
)

# =========================================================
# HOLDINGS TABLE
# =========================================================

st.divider()

st.subheader("Allocation Details")

display_df = df[
    [
        "Yahoo Finance Symbol",
        "Currency",
        "Quantity",
        "Price",
        "Market Value"
    ]
].copy()

# =========================================================
# PERCENTAGE ALLOCATION
# =========================================================

total_mv = display_df[
    "Market Value"
].sum()

display_df["Allocation %"] = (
    display_df["Market Value"]
    / total_mv
) * 100

display_df = display_df.sort_values(
    "Market Value",
    ascending=False
)

display_df = display_df.round(2)

st.dataframe(
    display_df,
    use_container_width=True,
    height=650
)

# =========================================================
# DOWNLOAD CSV
# =========================================================

csv = display_df.to_csv(index=False)

st.download_button(
    "⬇ Download Allocation Data",
    csv,
    "allocation.csv",
    "text/csv"
)

# =========================================================
# OPTIONAL DETAILS
# =========================================================

with st.expander("Show Allocation Statistics"):

    st.write(
        f"Total Holdings: {len(display_df)}"
    )

    st.write(
        f"Canadian Holdings: {len(cad_df)}"
    )

    st.write(
        f"US Holdings: {len(usd_df)}"
    )

    st.write(
        f"Largest Position: "
        f"{display_df.iloc[0]['Yahoo Finance Symbol']}"
    )

    st.write(
        f"Largest Allocation: "
        f"{display_df.iloc[0]['Allocation %']:.2f}%"
    )

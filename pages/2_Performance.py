# =========================================================
# pages/2_Performance.py
# Mobile-First Performance Dashboard
# =========================================================

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

from utils.data_loader import load_data
from utils.filters import filter_data
from utils.sidebar import render_sidebar
from utils.styles import style_fig

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Performance",
    layout="wide"
)

st.title("📈 Portfolio Performance")

# =========================================================
# SIDEBAR
# =========================================================

owner_account = render_sidebar()

# =========================================================
# RANGE SELECTION
# =========================================================

range_choice = st.radio(
    "Select Range",
    ["30d", "90d", "1y", "3y"],
    horizontal=True
)

period_map = {
    "30d": "1mo",
    "90d": "3mo",
    "1y": "1y",
    "3y": "3y"
}

selected_period = period_map[range_choice]

# =========================================================
# LOAD DATA
# =========================================================

df = load_data()

df = filter_data(df, owner_account)

symbols = df["Yahoo Finance Symbol"].unique().tolist()

# =========================================================
# DOWNLOAD HISTORICAL DATA
# =========================================================

@st.cache_data(ttl=1800)
def download_prices(symbols, period):

    prices = yf.download(
        symbols,
        period=period,
        interval="1d",
        progress=False
    )["Close"]

    prices = prices.ffill()

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    return prices

with st.spinner("Loading portfolio performance..."):

    prices = download_prices(
        symbols,
        selected_period
    )

# =========================================================
# BUILD PORTFOLIO SERIES
# =========================================================

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

# =========================================================
# PERFORMANCE DATAFRAME
# =========================================================

perf_df = pd.DataFrame({
    "Canadian Portfolio": cad_series,
    "US Portfolio": usd_series
})

# =========================================================
# MAIN PERFORMANCE CHART
# =========================================================

st.subheader("Portfolio Value")

main_fig = px.line(
    perf_df,
    y=[
        "Canadian Portfolio",
        "US Portfolio"
    ]
)

main_fig.update_layout(
    yaxis_title="Portfolio Value",
    xaxis_title="Date",
    legend_title=""
)

main_fig = style_fig(
    main_fig,
    height=450
)

st.plotly_chart(
    main_fig,
    use_container_width=True
)

# =========================================================
# 30-DAY MOVING AVERAGE GROWTH
# =========================================================

st.divider()

st.subheader("30-Day Moving Average Growth (%)")

cad_ma30 = cad_series.rolling(30).mean()

usd_ma30 = usd_series.rolling(30).mean()

# =========================================================
# SAFE GROWTH CALCULATION
# =========================================================

def calculate_growth(ma_series):

    clean = ma_series.dropna()

    if len(clean) == 0:

        return pd.Series(
            0,
            index=ma_series.index
        )

    base = clean.iloc[0]

    return (
        (
            ma_series / base
        ) - 1
    ) * 100

cad_growth = calculate_growth(cad_ma30)

usd_growth = calculate_growth(usd_ma30)

growth_df = pd.DataFrame({
    "CAD MA30 Growth %": cad_growth,
    "USD MA30 Growth %": usd_growth
})

growth_fig = px.line(
    growth_df,
    y=[
        "CAD MA30 Growth %",
        "USD MA30 Growth %"
    ]
)

growth_fig.update_layout(
    yaxis_title="Growth %",
    xaxis_title="Date",
    legend_title=""
)

growth_fig = style_fig(
    growth_fig,
    height=450
)

st.plotly_chart(
    growth_fig,
    use_container_width=True
)

# =========================================================
# RELATIVE STRENGTH COMPARISON
# =========================================================

st.divider()

st.subheader("Relative Strength Comparison")

# ---------------------------------------------------------
# DOWNLOAD BENCHMARKS
# ---------------------------------------------------------

benchmarks = yf.download(
    [
        "^GSPTSE",   # TSX
        "^GSPC"      # S&P500
    ],
    period=selected_period,
    interval="1d",
    progress=False
)["Close"]

benchmarks = benchmarks.ffill()

# =========================================================
# NORMALIZE FUNCTION
# =========================================================

def normalize(series):

    return (
        series / series.dropna().iloc[0]
    ) * 100

# =========================================================
# NORMALIZED SERIES
# =========================================================

cad_relative = normalize(cad_series)

usd_relative = normalize(usd_series)

tsx_relative = normalize(
    benchmarks["^GSPTSE"]
)

sp500_relative = normalize(
    benchmarks["^GSPC"]
)

# =========================================================
# CANADIAN RELATIVE STRENGTH
# =========================================================

st.markdown("### 🇨🇦 Canadian Portfolio vs Benchmarks")

cad_compare_df = pd.DataFrame({
    "Canadian Portfolio": cad_relative,
    "TSX": tsx_relative,
    "S&P500": sp500_relative
})

cad_compare_fig = px.line(
    cad_compare_df,
    y=[
        "Canadian Portfolio",
        "TSX",
        "S&P500"
    ]
)

cad_compare_fig.update_layout(
    yaxis_title="Indexed Growth (100 Base)",
    xaxis_title="Date",
    legend_title=""
)

cad_compare_fig = style_fig(
    cad_compare_fig,
    height=500
)

st.plotly_chart(
    cad_compare_fig,
    use_container_width=True
)

# =========================================================
# US RELATIVE STRENGTH
# =========================================================

st.markdown("### 🇺🇸 US Portfolio vs S&P500")

usd_compare_df = pd.DataFrame({
    "US Portfolio": usd_relative,
    "S&P500": sp500_relative
})

usd_compare_fig = px.line(
    usd_compare_df,
    y=[
        "US Portfolio",
        "S&P500"
    ]
)

usd_compare_fig.update_layout(
    yaxis_title="Indexed Growth (100 Base)",
    xaxis_title="Date",
    legend_title=""
)

usd_compare_fig = style_fig(
    usd_compare_fig,
    height=500
)

st.plotly_chart(
    usd_compare_fig,
    use_container_width=True
)

# =========================================================
# KPI SUMMARY
# =========================================================

st.divider()

st.subheader("Performance Summary")

def latest_value(series):

    clean = series.dropna()

    if len(clean) == 0:
        return 0

    return round(clean.iloc[-1], 1)

latest_cad_growth = latest_value(cad_growth)

latest_usd_growth = latest_value(usd_growth)

st.metric(
    "🇨🇦 CAD MA30 Growth",
    f"{latest_cad_growth}%"
)

st.metric(
    "🇺🇸 USD MA30 Growth",
    f"{latest_usd_growth}%"
)

# =========================================================
# OPTIONAL DETAILS
# =========================================================

with st.expander("Show Raw Performance Data"):

    st.dataframe(
        perf_df.round(2),
        use_container_width=True,
        height=400
    )

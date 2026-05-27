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
    ["90d", "1y", "3y"],
    index=2,
    horizontal=True
)

period_map = {
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
# st.write(df[["Yahoo Finance Symbol", "Market", "Currency"]])

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_cols = [
    "Yahoo Finance Symbol",
    "Quantity",
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

    st.stop()

# =========================================================
# CLEAN DATA
# =========================================================

df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
).fillna(0)

# =========================================================
# SYMBOLS
# =========================================================

symbols = df[
    "Yahoo Finance Symbol"
].dropna().unique().tolist()

if len(symbols) == 0:

    st.warning(
        "No symbols found."
    )

    st.stop()

# =========================================================
# DOWNLOAD PRICE DATA
# =========================================================

@st.cache_data(ttl=1800)
def download_prices(symbols, period):

    data = yf.download(
        symbols,
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=True
    )

    if data.empty:

        return pd.DataFrame()

    # Handle single symbol case

    if len(symbols) == 1:

        prices = data["Close"].to_frame()

        prices.columns = symbols

    else:

        prices = data["Close"]

    prices = prices.ffill()

    return prices

with st.spinner("Loading performance data..."):

    prices = download_prices(
        symbols,
        selected_period
    )

if prices.empty:

    st.error(
        "Unable to download price data."
    )

    st.stop()

# =========================================================
# BUILD PORTFOLIO SERIES
# =========================================================

cad_series = pd.Series(
    0.0,
    index=prices.index
)

usd_series = pd.Series(
    0.0,
    index=prices.index
)

# =========================================================
# CALCULATE DAILY PORTFOLIO VALUES
# =========================================================

for _, row in df.iterrows():

    ticker = row["Yahoo Finance Symbol"]

    qty = row["Quantity"]

    currency = row["Currency"]

    if ticker not in prices.columns:

        continue

    ticker_series = (
        prices[ticker]
        * qty
    )

    ticker_series = ticker_series.fillna(0)

    if currency == "CAD":

        cad_series = cad_series.add(
            ticker_series,
            fill_value=0
        )
        cad_series = cad_series.ffill()

    elif currency == "USD":

        usd_series = usd_series.add(
            ticker_series,
            fill_value=0
        )
        usd_series = usd_series.ffill()

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
    height=500
)

st.plotly_chart(
    main_fig,
    use_container_width=True
)

# =========================================================
# MOVING AVERAGE GROWTH
# =========================================================

st.divider()

st.subheader("30-Day Moving Average Growth")

# =========================================================
# MOVING AVERAGES
# =========================================================

cad_ma30 = cad_series.rolling(30).mean()

usd_ma30 = usd_series.rolling(30).mean()

# =========================================================
# SAFE GROWTH FUNCTION
# =========================================================

def calculate_growth(series):

    clean = series.dropna()

    clean = clean[clean != 0]

    if len(clean) == 0:

        return pd.Series(
            0,
            index=series.index
        )

    base = clean.iloc[0]

    return (
        (
            series / base
        ) - 1
    ) * 100

cad_growth = calculate_growth(
    cad_ma30
)

usd_growth = calculate_growth(
    usd_ma30
)

# =========================================================
# GROWTH DATAFRAME
# =========================================================

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
    height=500
)

st.plotly_chart(
    growth_fig,
    use_container_width=True
)

# =========================================================
# BENCHMARKS
# =========================================================

st.divider()

st.subheader("Relative Strength Comparison")

# =========================================================
# DOWNLOAD BENCHMARKS
# =========================================================

@st.cache_data(ttl=1800)
def download_benchmarks(period):

    benchmark_symbols = [
        "^GSPTSE",   # TSX
        "^GSPC"      # S&P500
    ]

    data = yf.download(
        benchmark_symbols,
        period=period,
        interval="1d",
        progress=False,
        auto_adjust=True
    )

    if data.empty:

        return pd.DataFrame()

    benchmarks = data["Close"]

    benchmarks = benchmarks.ffill()

    return benchmarks

benchmarks = download_benchmarks(
    selected_period
)

if benchmarks.empty:

    st.warning(
        "Unable to load benchmark data."
    )

else:

    # =====================================================
    # NORMALIZE FUNCTION
    # =====================================================


    def normalize(series):

        clean = series.dropna()

    # remove zero values too
        clean = clean[clean != 0]

        if len(clean) == 0:

            return pd.Series(
                0,
                index=series.index
            )

    # first NON-ZERO value
        base = clean.iloc[0]

        normalized = (
            series / base
        ) * 100

        return normalized
    
    # =====================================================
    # NORMALIZED SERIES
    # =====================================================

    cad_relative = normalize(
        cad_series
    )

    usd_relative = normalize(
        usd_series
    )

    tsx_relative = normalize(
        benchmarks["^GSPTSE"]
    )

    sp500_relative = normalize(
        benchmarks["^GSPC"]
    )

    # =====================================================
    # CANADIAN COMPARISON
    # =====================================================

    st.markdown(
        "### 🇨🇦 Canadian Portfolio vs TSX & S&P500"
    )

    cad_compare_df = pd.DataFrame({
        "Canadian Portfolio": cad_relative,
        "TSX": tsx_relative,
        "S&P500": sp500_relative
    })

    cad_compare_df = cad_compare_df.dropna(
        how="all"
    )

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
        height=550
    )

    st.plotly_chart(
        cad_compare_fig,
        use_container_width=True
    )

    # =====================================================
    # US COMPARISON
    # =====================================================

    st.markdown(
        "### 🇺🇸 US Portfolio vs S&P500"
    )

    usd_compare_df = pd.DataFrame({
        "US Portfolio": usd_relative,
        "S&P500": sp500_relative
    })

    usd_compare_df = usd_compare_df.dropna(
        how="all"
    )

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
        height=550
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

    return round(
        clean.iloc[-1],
        1
    )

latest_cad_growth = latest_value(
    cad_growth
)

latest_usd_growth = latest_value(
    usd_growth
)

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "🇨🇦 CAD MA30 Growth",
        f"{latest_cad_growth}%"
    )

with col2:

    st.metric(
        "🇺🇸 USD MA30 Growth",
        f"{latest_usd_growth}%"
    )

# =========================================================
# OPTIONAL RAW DATA
# =========================================================

with st.expander(
    "Show Raw Performance Data"
):

    st.dataframe(
        perf_df.round(2),
        use_container_width=True,
        height=500
    )

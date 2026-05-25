# =========================================================
# pages/3_Dividends.py
# Mobile-First Dividend Dashboard
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
    page_title="Dividends",
    layout="wide"
)

st.title("💰 Dividend Dashboard")

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
# DIVIDEND MONTH COLUMNS
# =========================================================

dividend_months = [
    "Dividend Jan",
    "Dividend Feb",
    "Dividend Mar",
    "Dividend Apr",
    "Dividend May",
    "Dividend Jun",
    "Dividend Jul",
    "Dividend Aug",
    "Dividend Sep",
    "Dividend Oct",
    "Dividend Nov",
    "Dividend Dec"
]

# =========================================================
# VALIDATE COLUMNS
# =========================================================

missing_cols = [
    col for col in dividend_months
    if col not in df.columns
]

if len(missing_cols) > 0:

    st.error(
        f"Missing dividend columns: {missing_cols}"
    )

    st.write("Available columns:")

    st.write(df.columns.tolist())

    st.stop()

# =========================================================
# CLEAN DIVIDEND DATA
# =========================================================

for col in dividend_months:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# =========================================================
# CALCULATE ANNUAL DIVIDEND
# =========================================================

df["Annual Dividend"] = df[
    dividend_months
].sum(axis=1)

# =========================================================
# DIVIDEND STOCKS ONLY
# =========================================================

div_df = df[
    df["Annual Dividend"] > 0
].copy()

if div_df.empty:

    st.warning(
        "No dividend-paying stocks found."
    )

    st.stop()

# =========================================================
# CALCULATE DIVIDEND INCOME
# =========================================================

div_df["Annual Income"] = (
    div_df["Annual Dividend"]
)

# =========================================================
# TOTALS
# =========================================================

cad_annual = div_df[
    div_df["Currency"] == "CAD"
]["Annual Income"].sum()

usd_annual = div_df[
    div_df["Currency"] == "USD"
]["Annual Income"].sum()

cad_monthly_avg = cad_annual / 12

usd_monthly_avg = usd_annual / 12

# =========================================================
# KPI SECTION
# =========================================================

st.subheader("Dividend Income Summary")

st.metric(
    "🇨🇦 Annual CAD Dividends",
    f"{cad_annual:,.0f} CAD"
)

st.metric(
    "🇺🇸 Annual USD Dividends",
    f"{usd_annual:,.0f} USD"
)

st.metric(
    "🇨🇦 Average Monthly CAD",
    f"{cad_monthly_avg:,.0f} CAD"
)

st.metric(
    "🇺🇸 Average Monthly USD",
    f"{usd_monthly_avg:,.0f} USD"
)

# =========================================================
# REAL MONTHLY DIVIDEND CASHFLOW
# =========================================================

st.divider()

st.subheader("Monthly Dividend Cashflow")

month_labels = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
]

monthly_rows = []

for i, month in enumerate(dividend_months):

    cad_total = div_df[
        div_df["Currency"] == "CAD"
    ][month].sum()

    usd_total = div_df[
        div_df["Currency"] == "USD"
    ][month].sum()

    monthly_rows.append({
        "Month": month_labels[i],
        "CAD": cad_total,
        "USD": usd_total
    })
    
monthly_df = pd.DataFrame(monthly_rows)

monthly_fig = px.bar(
    monthly_df,
    x="Month",
    y=["CAD", "USD"],
    barmode="group",
    text_auto=".0f"
)

monthly_fig.update_layout(
    yaxis_title="Dividend Income",
    xaxis_title="",
    legend_title=""
)

monthly_fig = style_fig(
    monthly_fig,
    height=500
)

st.plotly_chart(
    monthly_fig,
    use_container_width=True
)

# =========================================================
# DIVIDEND ALLOCATION
# =========================================================

st.divider()

st.subheader("Dividend Allocation")

alloc_fig = px.pie(
    div_df,
    names="Yahoo Finance Symbol",
    values="Annual Income",
    hole=0.45
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
# TOP DIVIDEND CONTRIBUTORS
# =========================================================

st.divider()

st.subheader("Top Dividend Contributors")

top_div_df = (
    div_df[
        [
            "Yahoo Finance Symbol",
            "Currency",
            "Quantity",
            "Annual Dividend",
            "Annual Income"
        ]
    ]
    .sort_values(
        "Annual Income",
        ascending=False
    )
)

top_fig = px.bar(
    top_div_df.head(15),
    x="Yahoo Finance Symbol",
    y="Annual Income",
    color="Currency",
    text_auto=".0f"
)

top_fig.update_layout(
    yaxis_title="Annual Dividend Income",
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
# CURRENT PRICES
# =========================================================

symbols = div_df[
    "Yahoo Finance Symbol"
].unique().tolist()

@st.cache_data(ttl=300)
def get_prices(symbols):

    prices = {}

    for sym in symbols:

        try:

            ticker = yf.Ticker(sym)

            hist = ticker.history(
                period="2d"
            )

            prices[sym] = float(
                hist["Close"].iloc[-1]
            )

        except:

            prices[sym] = 0

    return prices

price_map = get_prices(symbols)

div_df["Price"] = (
    div_df["Yahoo Finance Symbol"]
    .map(price_map)
)

# =========================================================
# MARKET VALUE
# =========================================================

div_df["Market Value"] = (
    div_df["Price"]
    * div_df["Quantity"]
)

# =========================================================
# DIVIDEND YIELD
# =========================================================

div_df["Yield %"] = (
    div_df["Annual Income"]
    / div_df["Market Value"]
) * 100

div_df["Yield %"] = (
    div_df["Yield %"]
    .fillna(0)
)

# =========================================================
# DIVIDEND YIELD CHART
# =========================================================

st.divider()

st.subheader("Dividend Yield (%)")

yield_df = (
    div_df[
        [
            "Yahoo Finance Symbol",
            "Currency",
            "Yield %",
            "Annual Income"
        ]
    ]
    .sort_values(
        "Yield %",
        ascending=False
    )
)

yield_fig = px.bar(
    yield_df.head(15),
    x="Yahoo Finance Symbol",
    y="Yield %",
    color="Currency",
    text_auto=".2f"
)

yield_fig.update_layout(
    yaxis_title="Dividend Yield %",
    xaxis_title="",
    legend_title=""
)

yield_fig = style_fig(
    yield_fig,
    height=500
)

st.plotly_chart(
    yield_fig,
    use_container_width=True
)

# =========================================================
# DIVIDEND CALENDAR TABLE
# =========================================================

st.divider()

st.subheader("Dividend Calendar")

calendar_cols = [
    "Yahoo Finance Symbol",
    "Currency",
    "Quantity"
] + dividend_months + [
    "Annual Dividend",
    "Annual Income",
    "Yield %"
]

calendar_df = div_df[
    calendar_cols
].copy()

calendar_df = calendar_df.round(2)

st.dataframe(
    calendar_df,
    use_container_width=True,
    height=650
)

# =========================================================
# DOWNLOAD CSV
# =========================================================

csv = calendar_df.to_csv(index=False)

st.download_button(
    "⬇ Download Dividend Data",
    csv,
    "dividend_calendar.csv",
    "text/csv"
)

# =========================================================
# OPTIONAL DETAILS
# =========================================================

with st.expander("Show Monthly Dividend Totals"):

    st.dataframe(
        monthly_df.round(2),
        use_container_width=True
    )

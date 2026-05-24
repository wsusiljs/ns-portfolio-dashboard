import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

from utils.data_loader import load_data
from utils.filters import filter_data

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dividends",
    layout="wide"
)

st.title("💰 Dividends")

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
# FX RATE
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

# =========================================================
# DIVIDENDS
# =========================================================

dividend_cols = [
    c for c in df.columns
    if c.startswith("Dividend ")
]

if not dividend_cols:

    st.warning("No dividend data available.")

else:

    melted = df.melt(
        id_vars=["Market"],
        value_vars=dividend_cols,
        var_name="Month",
        value_name="Dividend"
    )

    melted["Month"] = (
        melted["Month"]
        .str.replace("Dividend ", "", regex=False)
        .str.strip()
        .str.replace(r"\.", "", regex=True)
        .str[:3]
    )

    month_order = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    totals = (
        melted
        .groupby(["Month", "Market"])["Dividend"]
        .sum()
        .reset_index()
    )

    # CPP Monthly Income
    cpp_df = pd.DataFrame({
        "Month": month_order,
        "Market": ["CPP"] * 12,
        "Dividend": [550] * 12
    })

    totals = pd.concat(
        [totals, cpp_df],
        ignore_index=True
    )

    # Convert USD -> CAD
    fx_rate = get_fx_rate_usd_cad()

    totals.loc[
        totals["Market"] == "US",
        "Dividend"
    ] *= fx_rate

    totals["Month"] = pd.Categorical(
        totals["Month"],
        categories=month_order,
        ordered=True
    )

    fig = px.bar(
        totals,
        x="Month",
        y="Dividend",
        color="Market",
        barmode="group",
        text_auto=".0f",
        category_orders={
            "Month": month_order
        }
    )

    fig.update_layout(
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    monthly_totals = (
        totals
        .groupby("Month")["Dividend"]
        .sum()
        .reindex(month_order)
    )

    st.subheader("Monthly Totals")

    st.dataframe(
        monthly_totals.reset_index(),
        use_container_width=True
    )

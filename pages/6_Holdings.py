import streamlit as st
from st_aggrid import AgGrid
from st_aggrid import GridOptionsBuilder

from utils.data_loader import load_data
from utils.filters import filter_data
from utils.price_fetcher import get_realtime_prices

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Holdings",
    layout="wide"
)

st.title("📋 Holdings")

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

df["Cost"] = (
    df["Quantity"]
    * df["Average Cost"]
)

df["GainLoss"] = (
    df["Value"]
    - df["Cost"]
)

# =========================================================
# DISPLAY TABLE
# =========================================================

display_df = df[[
    "Yahoo Finance Symbol",
    "Price",
    "Average Cost",
    "Quantity",
    "Value",
    "GainLoss"
]]

display_df = display_df.rename(columns={
    "Yahoo Finance Symbol": "Ticker",
    "Average Cost": "Avg Cost",
    "Value": "Market Value",
    "GainLoss": "Gain/Loss"
})

# =========================================================
# AGGRID
# =========================================================

gb = GridOptionsBuilder.from_dataframe(display_df)

gb.configure_default_column(
    sortable=True,
    filter=True,
    resizable=True
)

gb.configure_pagination(
    paginationAutoPageSize=False,
    paginationPageSize=15
)

gridOptions = gb.build()

AgGrid(
    display_df.round(2),
    gridOptions=gridOptions,
    fit_columns_on_grid_load=True,
    height=600
)

# =========================================================
# TOTALS
# =========================================================

st.divider()

total_value = df["Value"].sum()

total_gain = df["GainLoss"].sum()

c1, c2 = st.columns(2)

with c1:

    st.metric(
        "Portfolio Value",
        f"{total_value:,.0f}"
    )

with c2:

    st.metric(
        "Total Gain/Loss",
        f"{total_gain:,.0f}"
    )

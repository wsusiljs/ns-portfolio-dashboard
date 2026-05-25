import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.filters import filter_data
from utils.price_fetcher import get_realtime_prices
from utils.fx import get_fx_rate
from utils.sidebar import render_sidebar

st.title("📊 Portfolio Summary")

owner_account = render_sidebar()

df = load_data()

df = filter_data(df, owner_account)

symbols = df["Yahoo Finance Symbol"].unique().tolist()

price_map = get_realtime_prices(symbols)

df["Price"] = df["Yahoo Finance Symbol"].map(price_map)

df["Value"] = df["Quantity"] * df["Price"]

cad_total = df[df["Currency"] == "CAD"]["Value"].sum()

usd_total = df[df["Currency"] == "USD"]["Value"].sum()

fx = get_fx_rate()

combined = cad_total + usd_total * fx

st.metric(
    "Combined Portfolio (CAD)",
    f"{combined:,.0f}"
)

st.metric(
    "Canadian Portfolio",
    f"{cad_total:,.0f} CAD"
)

st.metric(
    "US Portfolio",
    f"{usd_total:,.0f} USD"
)

pie_fig = px.pie(
    names=["Canada", "US"],
    values=[cad_total, usd_total],
    hole=0.4
)

st.plotly_chart(
    pie_fig,
    use_container_width=True
)

accounts = [
    "Nilmini-TFSA",
    "Nilmini-INV",
    "Susil-TFSA",
    "Susil-INV"
]

rows = []

for acc in accounts:

    owner, acct = acc.split("-")

    cad_val = df[
        (df["Currency"] == "CAD")
        & (df["Owner"] == owner)
        & (df["Account"].str.contains(acct))
    ]["Value"].sum()

    usd_val = df[
        (df["Currency"] == "USD")
        & (df["Owner"] == owner)
        & (df["Account"].str.contains(acct))
    ]["Value"].sum()

    rows.append({
        "Account": acc,
        "CAD": cad_val,
        "USD": usd_val
    })

breakdown_df = pd.DataFrame(rows)

cad_fig = px.bar(
    breakdown_df,
    x="Account",
    y="CAD",
    text_auto=".0f",
    title="Canadian Breakdown"
)

st.plotly_chart(
    cad_fig,
    use_container_width=True
)

usd_fig = px.bar(
    breakdown_df,
    x="Account",
    y="USD",
    text_auto=".0f",
    title="US Breakdown"
)

st.plotly_chart(
    usd_fig,
    use_container_width=True
)

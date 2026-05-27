import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def load_data():

    df = pd.read_csv("stock-data.csv")

    df["Market"] = (
        df["Market"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Currency"] = df["Market"].map({
        "CANADA": "CAD",
        "US": "USD"
    })
    return df

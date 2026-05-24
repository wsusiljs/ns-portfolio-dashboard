import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def load_data():

    df = pd.read_csv("stock-data.csv")

    df["Currency"] = df["Market"].map({
        "Canada": "CAD",
        "US": "USD"
    })

    return df

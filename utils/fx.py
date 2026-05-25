import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)
def get_fx_rate():

    try:

        fx = yf.Ticker("CAD=X")

        return float(
            fx.history(period="1d")["Close"].iloc[-1]
        )

    except:

        return 1.35

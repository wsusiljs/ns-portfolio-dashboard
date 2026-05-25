import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)
def get_realtime_prices(symbols):

    try:

        data = yf.download(
            symbols,
            period="2d",
            interval="1d",
            progress=False,
            group_by="ticker"
        )

        latest = {}

        for sym in symbols:

            try:

                if len(symbols) == 1:

                    series = data["Close"]

                else:

                    series = data[sym]["Close"]

                latest[sym] = float(
                    series.dropna().iloc[-1]
                )

            except:

                latest[sym] = 0

        return latest

    except:

        return {sym: 0 for sym in symbols}

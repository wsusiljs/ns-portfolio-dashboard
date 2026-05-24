import yfinance as yf
import datetime as dt
import streamlit as st

@st.cache_data(ttl=300)
def get_realtime_prices(symbols):

    now = dt.datetime.utcnow()

    market_open = now.replace(
        hour=14,
        minute=30,
        second=0,
        microsecond=0
    )

    market_close = now.replace(
        hour=21,
        minute=0,
        second=0,
        microsecond=0
    )

    try:

        if market_open <= now <= market_close:

            data = yf.download(
                symbols,
                period="1d",
                interval="1m",
                progress=False,
                group_by="ticker"
            )

        else:

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

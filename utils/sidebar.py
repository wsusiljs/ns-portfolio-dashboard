import streamlit as st

def render_sidebar():

    st.sidebar.title("📈 Portfolio")

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

    return owner_account

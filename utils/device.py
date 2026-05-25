import streamlit as st
from streamlit_js_eval import streamlit_js_eval

def is_mobile():

    width = streamlit_js_eval(
        js_expressions='screen.width',
        key='SCR'
    )

    if width is None:
        return False

    return width < 768

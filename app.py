import streamlit as st
from clarifai.modules.css import ClarifaiStreamlitCSS

st.set_page_config(layout="wide")

ClarifaiStreamlitCSS.insert_default_css(st)

"""
# Nextgen Forms

### AI powered forms for all
"""

if st.button("Let's get started", type="primary"):
    st.switch_page("pages/start.py")

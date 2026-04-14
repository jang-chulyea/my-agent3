import streamlit as st

from ui.pages.bundle_page import render as render_bundle
from ui.pages.solver_page import render as render_solver


st.set_page_config(layout="wide")

page = st.sidebar.selectbox("Menu", ["Bundle", "Solver"])

if page == "Bundle":
    render_bundle()
else:
    render_solver()

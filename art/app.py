from web import render_sidebar, render_dashboard
import streamlit as st


st.set_page_config(
    page_title="ART",
    page_icon=":musical_note:",
    layout="wide",
)

if "upload" not in st.session_state:
    st.session_state.upload = None
if "upload_orig" not in st.session_state:
    st.session_state.upload_orig = None
if "beatmap_upload" not in st.session_state:
    st.session_state.beatmap_upload = None
if "open_tab" not in st.session_state:
    st.session_state.open_tab = "c"

render_sidebar()
render_dashboard()

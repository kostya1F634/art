from web.dashboard import Dashboard
from web.sidebar import Sidebar
import streamlit as st


st.set_page_config(
    page_title="ART",
    page_icon=":musical_note:",
    layout="wide",
)

if "upload" not in st.session_state:
    st.session_state.upload = None
if "beatmap_upload" not in st.session_state:
    st.session_state.beatmap_upload = None

Sidebar().render()
Dashboard().render()

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.session_manager import init_session_state
from components.sidebar import render_sidebar
from components.header import render_header
from pages import dashboard_overview

st.set_page_config(page_title="SocialPulse AI – Dashboard Overview", page_icon="📊", layout="wide")
init_session_state()
st.session_state.current_page = "Dashboard Overview"

css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.markdown("""<style>[data-testid="stSidebarNav"] {display: none !important;}</style>""", unsafe_allow_html=True)

render_sidebar()
render_header()
dashboard_overview.render()

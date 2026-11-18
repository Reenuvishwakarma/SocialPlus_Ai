"""
SocialPulse AI - Header Component
Top navigation bar with breadcrumb, date range, comparison toggle, and action buttons.
"""
import streamlit as st
from utils.session_manager import init_session_state, get_dataset_info, is_data_loaded
from utils.formatters import format_date_range
from utils.constants import PRIMARY, TEXT_MUTED


def render_header():
    """Render the top header bar."""
    init_session_state()
    info = get_dataset_info()

    cols = st.columns([3, 2, 1, 1, 1])

    with cols[0]:
        page = st.session_state.get("current_page", "Dashboard Overview")
        st.markdown(f"""
        <div style="font-size: 0.78rem; color: {TEXT_MUTED}; padding-top:4px;">
            Console / Intelligence Workspace
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        if info["date_range"]:
            dr = format_date_range(info["date_range"][0], info["date_range"][1])
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:6px; padding-top:4px;">
                <span style="font-size:0.82rem;">📅</span>
                <span style="font-size:0.82rem; font-weight:500;">{dr}</span>
            </div>
            """, unsafe_allow_html=True)

    with cols[2]:
        if is_data_loaded():
            comp = st.checkbox("vs Prev.", value=st.session_state.get("comparison_enabled", False), key="hdr_comp")
            if comp != st.session_state.get("comparison_enabled", False):
                st.session_state.comparison_enabled = comp
                st.rerun()

    with cols[3]:
        if st.button("📁 Upload CSV", key="hdr_upload"):
            st.session_state.current_page = "CSV Upload & Prep"
            st.rerun()

    with cols[4]:
        if st.button("📄 Export Report", key="hdr_export", type="primary"):
            st.session_state.current_page = "Export & PDF Reports"
            st.rerun()

    st.markdown("<hr style='margin:4px 0 16px 0; border:none; border-top:1px solid #E8E8F0;'>", unsafe_allow_html=True)

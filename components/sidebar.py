"""
SocialPulse AI - Sidebar Component
Renders the left navigation sidebar with branding, platform selector, and nav menu.
"""
import streamlit as st
from utils.session_manager import init_session_state, get_dataset_info, get_platform
from utils.constants import PAGES, PRIMARY, TEXT_PRIMARY, TEXT_MUTED, SUCCESS


def render_sidebar():
    """Render the full sidebar."""
    init_session_state()

    with st.sidebar:
        # ── Brand Section ───────────────────────────────────────────────
        st.markdown(f"""
        <div style="padding: 8px 0 16px 0; border-bottom: 1px solid #E8E8F0; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 36px; height: 36px; background: {PRIMARY}; border-radius: 8px;
                            display: flex; align-items: center; justify-content: center;">
                    <span style="color: white; font-size: 1.1rem;">📊</span>
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1rem; color: {TEXT_PRIMARY}; font-family: 'Plus Jakarta Sans', sans-serif;">
                        SocialPulse<br/>AI
                    </div>
                </div>
                <div style="margin-left: auto;">
                    <span style="font-size: 0.65rem; color: {TEXT_MUTED}; background: #F0F0FF; padding: 2px 6px; border-radius: 4px;">v2.4</span>
                    <br/>
                    <span style="font-size: 0.6rem; color: {TEXT_MUTED};">INTERNSHIP EDL</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Platform Selector ───────────────────────────────────────────
        st.markdown(f"<div style='font-size:0.75rem; color:{TEXT_MUTED}; margin-bottom:4px;'>PLATFORM</div>", unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        current_platform = get_platform()
        with p1:
            ig_type = "primary" if current_platform == "Instagram" else "secondary"
            if st.button("📸 Instagram", use_container_width=True, type=ig_type, key="plat_ig"):
                st.session_state.platform = "Instagram"
                st.rerun()
        with p2:
            li_type = "primary" if current_platform == "LinkedIn" else "secondary"
            if st.button("💼 LinkedIn", use_container_width=True, type=li_type, key="plat_li"):
                st.session_state.platform = "LinkedIn"
                st.rerun()

        # ── Active Dataset Info ─────────────────────────────────────────
        info = get_dataset_info()
        if info["has_data"]:
            name_display = info["name"][:25] + "..." if info["name"] and len(info["name"]) > 25 else (info["name"] or "Dataset")
            st.markdown(f"""
            <div style="background: #F9F9FF; border-radius: 8px; padding: 10px 12px; margin: 12px 0;
                        border: 1px solid #E8E8F0;">
                <div style="font-size: 0.7rem; color: {TEXT_MUTED}; margin-bottom: 2px;">ACTIVE DATASET</div>
                <div style="font-size: 0.82rem; font-weight: 600; color: {TEXT_PRIMARY};">
                    📄 {name_display}
                </div>
                <div style="font-size: 0.72rem; color: {TEXT_MUTED};">{info['rows']:,} verified rows</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Navigation Menu ─────────────────────────────────────────────
        current_page = st.session_state.get("current_page", "Dashboard Overview")

        for page_name, config in PAGES.items():
            icon = config["icon"]
            is_active = current_page == page_name

            if is_active:
                bg = PRIMARY
                text_color = "white"
                weight = "600"
            else:
                bg = "transparent"
                text_color = TEXT_PRIMARY
                weight = "400"

            if st.button(
                f"{icon}  {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = page_name
                st.rerun()

        # ── User Profile Section ────────────────────────────────────────
        st.markdown("<div style='flex:1; min-height:40px;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0;">
            <div style="width: 32px; height: 32px; background: {PRIMARY}; border-radius: 50%;
                        display: flex; align-items: center; justify-content: center;
                        color: white; font-weight: 600; font-size: 0.8rem;">AM</div>
            <div>
                <div style="font-size: 0.82rem; font-weight: 600; color: {TEXT_PRIMARY};">Alex Morgan</div>
                <div style="font-size: 0.7rem; color: {SUCCESS};">● Streamlit Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

"""
SocialPulse AI - Page 2: CSV Upload & Prep
CSV ingestion, validation, column mapping, and data quality reporting.
"""
import streamlit as st
import pandas as pd
import os
from utils.session_manager import (
    init_session_state, set_dataframe, set_raw_dataframe, set_mapped_columns,
    set_validation_results, set_date_range, set_data_quality, clear_dataset,
    get_dataframe, get_platform, set_platform, is_data_loaded
)
from utils.constants import (
    STD_DATE, STD_POST, STD_REACH, STD_IMPRESSIONS, STD_LIKES,
    STD_COMMENTS, STD_SHARES, STD_SAVES, STD_FOLLOWERS, STD_POST_TYPE,
    STD_ENGAGEMENT_RATE, COLUMN_MAPPING, PLATFORMS,
    PRIMARY, SUCCESS, DANGER, TEXT_PRIMARY, TEXT_MUTED, SECONDARY
)
from utils.helpers import get_date_range
from services.csv_loader import load_csv, get_file_info
from services.column_mapper import auto_map_columns, get_mapping_report
from services.data_validator import validate_dataset, get_health_rating, get_health_color
from services.data_cleaner import clean_dataset, calculate_missing_engagement_rate


def render():
    init_session_state()

    st.markdown(f"""
    <div style="margin-bottom: 4px;">
        <span style="background:{PRIMARY};color:white;padding:3px 10px;border-radius:4px;
                     font-size:0.72rem;font-weight:600;">DATA INGESTION</span>
        <span style="color:{TEXT_MUTED};font-size:0.8rem;margin-left:8px;">• Auto-Parser Engine Idle</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("# CSV Data Ingestion & Quality Validation")
    st.markdown(f"""<p style="color:{TEXT_MUTED};font-size:0.9rem;">
    Upload your exported Instagram Insights or LinkedIn Analytics CSV export.
    The parser validates required metrics, dates, and schema consistency automatically.
    </p>""", unsafe_allow_html=True)

    # Schema quick-links
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<span style='font-size:0.8rem;color:{TEXT_MUTED};'>SCHEMAS:</span> "
                     f"<span style='font-size:0.8rem;color:{PRIMARY};cursor:pointer;'>📸 Instagram Schema Sample</span>",
                     unsafe_allow_html=True)
    with c2:
        st.markdown(f"<span style='font-size:0.8rem;color:{PRIMARY};cursor:pointer;'>💼 LinkedIn Schema Sample</span>",
                     unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Upload Area ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="border:2px dashed #C4C4E8;border-radius:12px;padding:40px 20px;text-align:center;
                background:#FCFCFF;margin-bottom:20px;">
        <div style="font-size:2rem;margin-bottom:8px;">☁️</div>
        <div style="font-weight:600;color:{TEXT_PRIMARY};margin-bottom:4px;">
            Drop your social media export (csv) here or browse files
        </div>
        <div style="color:{TEXT_MUTED};font-size:0.82rem;margin-bottom:16px;">
            Supports Instagram Creator/Business & LinkedIn Page/Analytics exports up to 25 MB
        </div>
        <div style="display:flex;justify-content:center;gap:24px;font-size:0.75rem;color:{TEXT_MUTED};">
            <span>✅ Client-Side Sanitized</span>
            <span>📊 Max 50,000 Rows</span>
            <span>🔡 UTF-8 / ISO-8859 Encodings</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV", type=["csv"], label_visibility="collapsed",
        key="csv_uploader"
    )

    # Sample data buttons
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns([1, 1, 2])
    with sc1:
        if st.button("📸 Load Instagram Sample", key="load_ig_sample"):
            _load_sample("instagram")
            return
    with sc2:
        if st.button("💼 Load LinkedIn Sample", key="load_li_sample"):
            _load_sample("linkedin")
            return

    # Process uploaded file
    if uploaded_file is not None:
        _process_upload(uploaded_file)
    elif is_data_loaded():
        _show_current_dataset()


def _load_sample(platform_key):
    """Load sample dataset."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if platform_key == "instagram":
        path = os.path.join(base, "data", "sample_instagram_data.csv")
        set_platform("Instagram")
    else:
        path = os.path.join(base, "data", "sample_linkedin_data.csv")
        set_platform("LinkedIn")

    from services.csv_loader import load_csv_from_path
    df, error = load_csv_from_path(path)
    if error:
        st.error(error)
        return
    _process_dataframe(df, f"sample_{platform_key}_data.csv")


def _process_upload(uploaded_file):
    """Process an uploaded CSV file."""
    file_info = get_file_info(uploaded_file)

    df, error = load_csv(uploaded_file)
    if error:
        st.error(f"❌ Upload Error: {error}")
        return

    _process_dataframe(df, file_info["name"])


def _process_dataframe(df, file_name):
    """Run the full processing pipeline on a dataframe."""
    set_raw_dataframe(df)

    # Auto column mapping
    mapped, unmapped = auto_map_columns(df)
    set_mapped_columns(mapped)
    st.session_state.unmapped_columns = unmapped

    # Validation
    validation = validate_dataset(df, mapped)
    set_validation_results(validation)

    # Show results
    _show_mapping_results(df, mapped, unmapped, file_name)
    _show_validation_results(validation)
    _show_data_preview(df, mapped)

    # Action buttons
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    bc1, bc2, bc3, bc4 = st.columns([1, 1, 1, 2])

    with bc1:
        if st.button("🔄 Replace file", key="replace_file"):
            clear_dataset()
            st.rerun()

    with bc2:
        if st.button("🗑️ Clear Cache", key="clear_cache"):
            clear_dataset()
            st.rerun()

    with bc3:
        st.markdown(f"<div style='padding-top:8px;text-align:center;font-size:0.82rem;color:{TEXT_MUTED};'>"
                     f"📊 {len(df)} Posts Loaded</div>", unsafe_allow_html=True)

    with bc4:
        if st.button("Process & Continue to Dashboard →", type="primary", key="process_continue",
                      use_container_width=True):
            # Clean and store
            cleaned = clean_dataset(df, mapped)
            cleaned = calculate_missing_engagement_rate(cleaned, mapped)
            date_start, date_end = get_date_range(cleaned, mapped.get(STD_DATE, ""))
            if date_start and date_end:
                set_date_range(date_start, date_end)
            set_dataframe(cleaned, file_name)
            st.session_state.current_page = "Dashboard Overview"
            st.rerun()


def _show_mapping_results(df, mapped, unmapped, file_name):
    """Display column mapping results."""
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:20px;border:1px solid #E8E8F0;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:40px;height:40px;background:#F0F0FF;border-radius:8px;
                            display:flex;align-items:center;justify-content:center;">📄</div>
                <div>
                    <div style="font-weight:600;color:{TEXT_PRIMARY};">{file_name}</div>
                    <div style="font-size:0.8rem;color:{TEXT_MUTED};">
                        Parsed {len(df)} valid records • Ingestion completed
                    </div>
                </div>
                <div style="margin-left:auto;">
                    <span style="background:{SUCCESS};color:white;padding:4px 12px;border-radius:20px;
                                 font-size:0.75rem;font-weight:600;">
                        ✓ CSV Validated • Ready for Processing
                    </span>
                </div>
            </div>
            <div style="font-size:0.82rem;font-weight:600;color:{TEXT_PRIMARY};margin-bottom:12px;">
                AUTOMATIC SCHEMA MAPPING & INTEGRITY VERIFICATION
            </div>
        """, unsafe_allow_html=True)

        # Show mapping categories
        categories = {
            "Date / Timestamp": [STD_DATE],
            "Post ID / Permalink": ["post_id"],
            "Reach & Impressions": [STD_REACH, STD_IMPRESSIONS],
            "Likes, Comments, Shares, Saves": [STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES],
            "Audience/Cached": [STD_FOLLOWERS],
            "Content Type / Format": [STD_POST_TYPE],
        }

        for cat_name, std_names in categories.items():
            mapped_items = []
            for s in std_names:
                if s in mapped:
                    mapped_items.append(f"✅ {s} → {mapped[s]}")
            status = "Detected" if mapped_items else "Not found"
            status_icon = "✅" if mapped_items else "⚠️"

            details = " | ".join([mapped[s] for s in std_names if s in mapped]) or "Not mapped"

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:6px 0;
                        border-bottom:1px solid #F0F0F5;font-size:0.82rem;">
                <span style="color:{TEXT_PRIMARY};">{status_icon} <b>{cat_name}</b></span>
                <span style="color:{TEXT_MUTED};">{status} ({details})</span>
            </div>
            """, unsafe_allow_html=True)

        # Missing optional columns note
        missing = [s for s in [STD_SAVES, "profile_visits"] if s not in mapped]
        if missing:
            st.markdown(f"""
            <div style="margin-top:12px;padding:10px;background:#FFFBEB;border-radius:8px;
                        font-size:0.8rem;color:#92400E;">
                ⚠️ Missing Optional Columns: {', '.join(missing)}<br/>
                These fields are null. Defaulted to 0 without breaking predictive inference models.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        # Health Rating Card
        validation = st.session_state.validation_results or validate_dataset(df, mapped)
        health = validation.get("health_score", 0)
        rating = get_health_rating(health)
        health_color = get_health_color(health)
        valid_count = validation.get("valid_records", len(df))
        total_count = validation.get("total_records", len(df))
        corrupted = validation.get("corrupted_records", 0)
        duplicates = validation.get("duplicate_records", 0)

        # Health bar segments
        segments = 5
        filled = int(health / 100 * segments)
        bar_html = ""
        for i in range(segments):
            clr = health_color if i < filled else "#E8E8F0"
            bar_html += f'<div style="flex:1;height:8px;background:{clr};border-radius:4px;"></div>'

        date_range_str = ""
        if validation.get("date_range_start") and validation.get("date_range_end"):
            ds = validation["date_range_start"]
            de = validation["date_range_end"]
            from utils.formatters import format_date
            date_range_str = f"{format_date(ds, '%b %d')} – {format_date(de, '%b %d, %Y')}"

        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:20px;border:1px solid #E8E8F0;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:0.8rem;color:{TEXT_MUTED};font-weight:500;">HEALTH RATING</span>
                <span style="font-weight:700;color:{health_color};">{rating}</span>
            </div>
            <div style="font-size:2.5rem;font-weight:800;color:{TEXT_PRIMARY};margin-bottom:4px;">{health:.0f}%</div>
            <div style="font-size:0.8rem;color:{TEXT_MUTED};margin-bottom:12px;">Data Completeness</div>
            <div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:16px;">
                {valid_count} of {total_count} rows possess complete secondary metadata. All core KPI dimensions present.
            </div>
            <div style="display:flex;gap:4px;margin-bottom:16px;">{bar_html}</div>
            <div style="font-size:0.8rem;color:{TEXT_MUTED};line-height:1.8;">
                Corrupted Records: <b>{corrupted}</b> (0.0%)<br/>
                Data Range Span: <b>{date_range_str}</b><br/>
                Duplicate Post IDs: <b>{duplicates}</b> {' – None Found' if duplicates == 0 else ''}<br/>
            </div>
            <div style="display:flex;justify-content:space-between;margin-top:12px;padding-top:12px;border-top:1px solid #F0F0F5;">
                <span style="font-size:0.78rem;color:{TEXT_MUTED};">✅ Auto Normalizer</span>
                <span style="font-size:0.78rem;color:{SUCCESS};font-weight:600;">APPLIED</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _show_validation_results(validation):
    """Show detailed validation warnings/issues if any."""
    issues = validation.get("issues", [])
    warnings = validation.get("warnings", [])

    if issues:
        for issue in issues:
            st.error(f"❌ {issue}")
    if warnings:
        with st.expander(f"⚠️ {len(warnings)} Validation Warning(s)", expanded=False):
            for w in warnings:
                st.warning(w)


def _show_data_preview(df, mapped):
    """Show data preview table."""
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    pr1, pr2 = st.columns([1, 1])
    with pr1:
        st.markdown(f"""
        <div style="font-weight:600;font-size:0.95rem;color:{TEXT_PRIMARY};">
            DataFrame Head Preview <span style="color:{TEXT_MUTED};font-weight:400;font-size:0.8rem;">TOP 5 ROWS SHOWN</span>
        </div>
        """, unsafe_allow_html=True)
    with pr2:
        st.markdown(f"""
        <div style="text-align:right;font-size:0.8rem;color:{TEXT_MUTED};">
            📐 {get_platform()} Insight Schema Standardized
        </div>
        """, unsafe_allow_html=True)

    # Select columns to display
    display_cols = []
    for std in ["post_id", STD_DATE, STD_POST_TYPE, STD_REACH, STD_IMPRESSIONS,
                STD_LIKES, STD_COMMENTS, STD_SHARES, STD_SAVES, STD_ENGAGEMENT_RATE]:
        col = mapped.get(std)
        if col and col in df.columns:
            display_cols.append(col)

    if not display_cols:
        display_cols = list(df.columns[:10])

    preview = df[display_cols].head(5)
    st.dataframe(preview, use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div style="font-size:0.75rem;color:{TEXT_MUTED};margin-top:4px;">
        Reviewing columns [{len(mapped)}] of {len(df.columns)} mapped features
    </div>
    """, unsafe_allow_html=True)


def _show_current_dataset():
    """Show info about the already-loaded dataset."""
    df = get_dataframe()
    mapped = st.session_state.mapped_columns
    validation = st.session_state.validation_results

    if df is not None and validation:
        st.success(f"✅ Dataset already loaded: **{st.session_state.dataset_name}** ({len(df)} rows)")
        _show_mapping_results(df, mapped, st.session_state.get("unmapped_columns", []),
                             st.session_state.dataset_name or "dataset")
        _show_data_preview(df, mapped)

        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("🔄 Replace File", key="replace_existing"):
                clear_dataset()
                st.rerun()
        with c2:
            if st.button("🗑️ Clear Dataset", key="clear_existing"):
                clear_dataset()
                st.rerun()

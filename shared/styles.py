"""
Modern Design System & Custom CSS for StudySync.
Aesthetic: Premium EdTech (Coursera / Udemy / Brilliant.org style)
Palette:
- Creme White: #FAF8F5 (canvas), #FFFFFF (cards), #F4EFE6 (secondary)
- Forest / Sage Green: #14382C (deep green), #1B4D3E (brand primary), #2D6A4F (hover), #EAF3EE (sage tint)
- Sky Blue Minutely: #0284C7 (accents), #38BDF8 (tags), #E0F2FE (badge background)
"""

import streamlit as st


THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Canvas & Base Text */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #FAF8F5 !important;
    color: #1E293B !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Ensure all text is sharp dark charcoal */
p, span, label, div, li {
    color: #1E293B;
}

h1, h2, h3, h4, h5, h6 {
    color: #14382C !important;
    font-weight: 700 !important;
    letter-spacing: -0.3px;
}

/* SIDEBAR: Elegant Sage Creme Tone with High-Contrast Text */
[data-testid="stSidebar"] {
    background-color: #F3EFE6 !important;
    border-right: 1px solid #E5E0D8 !important;
}

[data-testid="stSidebar"] * {
    color: #1E293B !important;
}

[data-testid="stSidebarNav"] span {
    color: #1E293B !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

[data-testid="stSidebarNav"] a {
    color: #1E293B !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin-bottom: 4px !important;
    transition: all 0.15s ease;
}

[data-testid="stSidebarNav"] a:hover {
    background-color: #E6E1D7 !important;
}

[data-testid="stSidebarNav"] [aria-current="page"] {
    background-color: #E2DDD5 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

[data-testid="stSidebarNav"] [aria-current="page"] span {
    color: #1B4D3E !important;
    font-weight: 800 !important;
}

/* Hero Banner (Coursera / Udemy style) */
.hero-banner {
    background: linear-gradient(135deg, #14382C 0%, #1B4D3E 55%, #0284C7 100%);
    border-radius: 16px;
    padding: 32px 36px;
    color: #FFFFFF !important;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(20, 56, 44, 0.2);
}

.hero-banner h1, .hero-banner h2, .hero-banner h3, .hero-banner p, .hero-banner span {
    color: #FFFFFF !important;
}

/* Modern Course Cards */
.course-card {
    background: #FFFFFF !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 14px !important;
    padding: 22px 24px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 4px 12px rgba(20, 56, 44, 0.03) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    position: relative;
    overflow: hidden;
}

.course-card:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 24px -4px rgba(20, 56, 44, 0.08) !important;
    border-color: #1B4D3E !important;
}

.card-strip {
    height: 4px;
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background: linear-gradient(90deg, #1B4D3E, #0284C7);
}

/* Badges */
.badge-blue {
    background-color: #E0F2FE !important;
    color: #0369A1 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 4px 9px !important;
    border-radius: 6px !important;
    border: 1px solid #BAE6FD !important;
    display: inline-block !important;
    margin-right: 6px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.badge-green {
    background-color: #EAF3EE !important;
    color: #14382C !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 4px 9px !important;
    border-radius: 6px !important;
    border: 1px solid #C7E2D3 !important;
    display: inline-block !important;
    margin-right: 6px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* Primary Button Styling */
button[kind="primary"] {
    background: #1B4D3E !important;
    border-color: #1B4D3E !important;
    color: #FFFFFF !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    padding: 8px 18px !important;
    box-shadow: 0 2px 4px rgba(27, 77, 62, 0.15) !important;
    transition: all 0.15s ease !important;
}

button[kind="primary"]:hover {
    background: #14382C !important;
    border-color: #14382C !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(20, 56, 44, 0.25) !important;
}

/* Secondary Button */
button[kind="secondary"] {
    border-radius: 9px !important;
    border: 1px solid #CBD5E1 !important;
    background-color: #FFFFFF !important;
    color: #14382C !important;
    font-weight: 600 !important;
}

button[kind="secondary"]:hover {
    border-color: #1B4D3E !important;
    color: #1B4D3E !important;
}

/* Metric KPI Tile */
.metric-box {
    background: #FFFFFF !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    text-align: left !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
}
.metric-val {
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    color: #14382C !important;
    line-height: 1.1 !important;
}
.metric-lbl {
    font-size: 0.78rem !important;
    color: #64748B !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-top: 4px !important;
}

/* Course Reader View Container */
.reader-container {
    background: #FFFFFF !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 14px !important;
    padding: 32px 36px !important;
    line-height: 1.75 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
}

.reader-container * {
    color: #1E293B !important;
}

/* Video Simulation Theater */
.video-theater {
    background: #0F172A !important;
    border-radius: 12px !important;
    padding: 24px !important;
    color: #FFFFFF !important;
    margin-bottom: 24px !important;
    border: 1px solid #1E293B !important;
}

.video-theater * {
    color: #FFFFFF !important;
}

/* Upload Dropzone Container */
.upload-card {
    background: #FFFFFF !important;
    border: 2px dashed #CBD5E1 !important;
    border-radius: 14px !important;
    padding: 24px !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
}

.upload-card:hover {
    border-color: #1B4D3E !important;
    background: #FAFBF9 !important;
}
</style>
"""


def apply_theme():
    """Inject custom styles into the active page."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, badge: str = "STUDYSYNC LEARNING"):
    """Render consistent page header with brand colors and subtle sky blue tag."""
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <span class="badge-blue">{badge}</span>
            <h1 style="color: #14382C; font-size: 2.2rem; font-weight: 800; margin-top: 6px; margin-bottom: 4px;">{title}</h1>
            <p style="color: #475569; font-size: 1.05rem; margin-top: 0;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

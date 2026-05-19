"""
CodeVantage Shared UI Components
Apple TV-inspired dark design system for Streamlit.
"""

from __future__ import annotations
import streamlit as st
from typing import Optional

# ── Global CSS ────────────────────────────────────────────────────────────────

CV_CSS = """
<style>
/* ── Base & typography ───────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                 "Helvetica Neue", Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-transform: none !important;
}
[data-testid="stAppViewContainer"] { background: #000000 !important; }
[data-testid="stMain"] > div { padding-top: 1.75rem; }
[data-testid="stMain"] { background: transparent !important; }
[data-testid="stHeader"] {
    background: rgba(0,0,0,0.72) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
}

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"] {
    background: #1c1c1e !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    min-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] a {
    color: rgba(255,255,255,0.9) !important;
    text-transform: none !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button[kind="secondary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 100px !important;
    color: rgba(255,255,255,0.9) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: none !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover,
[data-testid="stSidebar"] button:hover {
    background: rgba(255,59,48,0.3) !important;
    border-color: rgba(255,59,48,0.5) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"],
[data-testid="stSidebar"] [data-testid="stPageLink"] * {
    color: rgba(255,255,255,0.65) !important;
    text-decoration: none !important;
    text-transform: none !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    border-radius: 10px !important;
    padding: 9px 12px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.65) !important;
    text-decoration: none !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    margin: 1px 0 !important;
    line-height: 1.3 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: #0A84FF !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ── Page header ─────────────────────────────────────────────── */
.cv-header {
    background: rgba(28,28,30,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 28px 36px 24px;
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,0.1);
}
.cv-header h1 {
    margin: 0 0 6px 0;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: #FFFFFF !important;
    line-height: 1.2;
    text-transform: none !important;
}
.cv-header p {
    margin: 0;
    font-size: 0.90rem;
    color: rgba(255,255,255,0.55);
    line-height: 1.55;
}
.cv-header .cv-badge {
    display: inline-block;
    background: rgba(10,132,255,0.2);
    color: #0A84FF;
    padding: 3px 14px;
    border-radius: 100px;
    font-size: 0.74rem;
    font-weight: 600;
    margin-top: 12px;
    border: 1px solid rgba(10,132,255,0.35);
}

/* ── Cards ───────────────────────────────────────────────────── */
.cv-card {
    background: rgba(28,28,30,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 16px;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.cv-card:hover {
    border-color: rgba(10,132,255,0.4);
    transform: translateY(-1px);
}
.cv-card h3 {
    margin: 0 0 10px 0;
    font-size: 1.0rem;
    color: #FFFFFF !important;
    font-weight: 600;
    letter-spacing: -0.1px;
    text-transform: none !important;
}

/* ── Metric tiles ────────────────────────────────────────────── */
.cv-metric {
    background: rgba(28,28,30,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 20px 18px;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    border-top: 3px solid var(--mc, #0A84FF);
    transition: border-color 0.18s ease;
}
.cv-metric:hover { border-color: rgba(255,255,255,0.2); }
.cv-metric .cv-metric-val {
    font-size: 2rem;
    font-weight: 700;
    color: var(--mc, #0A84FF) !important;
    line-height: 1.1;
    margin-bottom: 7px;
    letter-spacing: -1px;
    text-transform: none !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}
.cv-metric .cv-metric-lbl {
    font-size: 0.74rem;
    color: rgba(255,255,255,0.45);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

/* ── Severity badges ─────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 100px;
    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.badge-CRITICAL { background: rgba(255,69,58,0.2);   color: #FF453A; border: 1px solid rgba(255,69,58,0.4); }
.badge-HIGH     { background: rgba(255,159,10,0.2);  color: #FF9F0A; border: 1px solid rgba(255,159,10,0.4); }
.badge-MEDIUM   { background: rgba(255,214,10,0.2);  color: #FFD60A; border: 1px solid rgba(255,214,10,0.4); }
.badge-LOW      { background: rgba(10,132,255,0.2);  color: #0A84FF; border: 1px solid rgba(10,132,255,0.4); }
.badge-INFO     { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.55); border: 1px solid rgba(255,255,255,0.15); }

/* ── Clean Core level badges ─────────────────────────────────── */
.cc-level {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 12px;
    border-radius: 100px;
    font-weight: 600;
    font-size: 0.80rem;
}
.cc-A { background: rgba(48,209,88,0.2);  color: #30D158; border: 1px solid rgba(48,209,88,0.35); }
.cc-B { background: rgba(10,132,255,0.2); color: #0A84FF; border: 1px solid rgba(10,132,255,0.35); }
.cc-C { background: rgba(255,159,10,0.2); color: #FF9F0A; border: 1px solid rgba(255,159,10,0.35); }
.cc-D { background: rgba(255,69,58,0.2);  color: #FF453A; border: 1px solid rgba(255,69,58,0.35); }

/* ── Violation row ───────────────────────────────────────────── */
.vrow {
    background: rgba(28,28,30,0.85);
    border-radius: 12px;
    padding: 14px 18px;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--vc, rgba(255,255,255,0.25));
    margin-bottom: 10px;
    transition: border-color 0.15s ease;
}
.vrow:hover { border-color: rgba(255,255,255,0.2); }
.vrow h4 { margin: 0 0 5px 0; font-size: 0.88rem; color: #FFFFFF !important; font-weight: 600; text-transform: none !important; }
.vrow p  { margin: 0; font-size: 0.82rem; color: rgba(255,255,255,0.55); line-height: 1.55; }
.vrow-CRITICAL { --vc: #FF453A; }
.vrow-HIGH     { --vc: #FF9F0A; }
.vrow-MEDIUM   { --vc: #FFD60A; }
.vrow-LOW      { --vc: #0A84FF; }
.vrow-INFO     { --vc: rgba(255,255,255,0.25); }

/* ── Code & diff ─────────────────────────────────────────────── */
.diff-container {
    background: rgba(12,12,14,0.95);
    border-radius: 12px;
    padding: 16px 20px;
    font-family: "SFMono-Regular", "Consolas", "Liberation Mono", monospace;
    font-size: 0.80rem;
    max-height: 520px;
    overflow-y: auto;
    line-height: 1.65;
    border: 1px solid rgba(255,255,255,0.1);
}
.diff-add    { color: #30D158; background: rgba(48,209,88,0.1);  padding: 1px 4px; border-radius: 3px; }
.diff-del    { color: #FF453A; background: rgba(255,69,58,0.1);  padding: 1px 4px; border-radius: 3px; }
.diff-ctx    { color: rgba(255,255,255,0.45); }
.diff-header { color: #0A84FF; font-weight: 600; margin: 10px 0 4px; }
.diff-hunk   { color: #5AC8FA; margin: 4px 0; }

/* ── Score ring ──────────────────────────────────────────────── */
.score-ring {
    width: 110px; height: 110px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; font-weight: 700;
    border: 8px solid var(--sc, #0A84FF);
    color: var(--sc, #0A84FF) !important;
    background: rgba(28,28,30,0.9);
    margin: 0 auto;
}

/* ── Streamlit widget overrides ──────────────────────────────── */
div[data-testid="stMetricValue"] { font-size: 1.7rem !important; font-weight: 700 !important; color: #FFFFFF !important; }

/* Primary button — Apple iOS pill */
.stButton > button[kind="primary"] {
    background: #0A84FF !important;
    border: none !important;
    border-radius: 100px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #FFFFFF !important;
    padding: 10px 24px !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    transition: opacity 0.15s ease !important;
    box-shadow: 0 2px 12px rgba(10,132,255,0.4) !important;
}
.stButton > button[kind="primary"]:hover { opacity: 0.88 !important; }
.stButton > button[kind="primary"]:active { opacity: 0.75 !important; }

/* Secondary button */
.stButton > button[kind="secondary"] {
    border-radius: 100px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    background: rgba(255,255,255,0.1) !important;
    color: rgba(255,255,255,0.9) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.35) !important;
}

/* Tabs — dark Apple style */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    background: transparent !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    font-size: 0.875rem;
    border-radius: 0 !important;
    padding: 10px 18px !important;
    color: rgba(255,255,255,0.45) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    text-transform: none !important;
    transition: color 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    color: #0A84FF !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #0A84FF !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: rgba(255,255,255,0.8) !important;
    background: rgba(255,255,255,0.05) !important;
}

/* Expanders */
.stExpander {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    background: rgba(28,28,30,0.85) !important;
    overflow: hidden;
}
.stExpander:hover { border-color: rgba(255,255,255,0.2) !important; }
.stExpander summary { font-weight: 600 !important; color: rgba(255,255,255,0.9) !important; font-size: 0.875rem !important; }

/* Forms */
[data-testid="stForm"] {
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 20px !important;
    background: rgba(28,28,30,0.85) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
}

/* Inputs */
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.15) !important;
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.9) !important;
}
input[type="text"], input[type="password"], textarea {
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.15) !important;
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.9) !important;
    font-size: 0.875rem !important;
}
input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
    border-color: #0A84FF !important;
    box-shadow: 0 0 0 3px rgba(10,132,255,0.25) !important;
    outline: none !important;
}

/* Hide Streamlit's submit tooltip */
[data-testid="InputInstructions"],
small[data-testid="InputInstructions"] { display: none !important; }

/* Divider */
hr { border-color: rgba(255,255,255,0.1) !important; margin: 20px 0 !important; }

/* Alerts */
[data-testid="stAlert"] { border-radius: 12px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden; }

/* Fix any lingering text-transform issues */
button, a, span, p, div, h1, h2, h3, h4, h5, label {
    text-transform: none !important;
}

/* Markdown text color */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: rgba(255,255,255,0.85) !important;
}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #FFFFFF !important;
}
</style>
"""

DIFF_CSS = """
<style>
.diff-container {
    background: rgba(12,12,14,0.95); border-radius: 12px; padding: 16px 20px;
    font-family: "SFMono-Regular", "Consolas", monospace;
    font-size: 0.80rem; max-height: 550px; overflow-y: auto; line-height: 1.65;
    border: 1px solid rgba(255,255,255,0.1);
}
</style>
"""


def inject_css() -> None:
    st.markdown(CV_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, badge: str = "") -> None:
    badge_html = f'<span class="cv-badge">{badge}</span>' if badge else ""
    st.markdown(f"""
    <div class="cv-header">
      <h1>{title}</h1>
      <p>{subtitle}</p>
      {badge_html}
    </div>""", unsafe_allow_html=True)


def metric_row(metrics: list[dict]) -> None:
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        color = m.get("color", "#0A84FF")
        delta = m.get("delta", "")
        delta_html = (
            f'<div style="font-size:.73rem;color:#706E6B;margin-top:5px">{delta}</div>'
            if delta else ""
        )
        col.markdown(
            f'<div class="cv-metric" style="--mc:{color}">'
            f'<div class="cv-metric-val">{m["value"]}</div>'
            f'<div class="cv-metric-lbl">{m["label"]}</div>'
            f'{delta_html}'
            f'</div>',
            unsafe_allow_html=True,
        )


def severity_badge(severity: str) -> str:
    return f'<span class="badge badge-{severity}">{severity}</span>'


def cc_level_badge(level: str) -> str:
    labels = {"A": "Level A", "B": "Level B", "C": "Level C", "D": "Level D"}
    icons  = {"A": "✓", "B": "●", "C": "▲", "D": "✕"}
    icon   = icons.get(level, "")
    label  = labels.get(level, level)
    return f'<span class="cc-level cc-{level}">{icon} {label}</span>'


def violation_card(v, idx: int) -> None:
    sev = v.severity
    cc_badge = (
        f'<span style="font-size:.71rem;background:rgba(255,255,255,0.1);'
        f'border:1px solid rgba(255,255,255,0.18);'
        f'border-radius:100px;padding:1px 8px;color:rgba(255,255,255,0.7);margin-left:6px;font-weight:500">'
        f'Level {v.cc_level}</span>'
        if v.cc_level else ""
    )
    st.markdown(
        f'<div class="vrow vrow-{sev}">'
        f'<h4>{severity_badge(sev)}{cc_badge}'
        f' &nbsp;<b>[{v.rule_id}]</b> {v.rule.name}'
        f'&nbsp;<span style="color:rgba(255,255,255,0.45);font-size:.78rem;font-weight:400">Line {v.line_number}</span></h4>'
        f'<p style="color:rgba(255,255,255,0.8);font-size:.82rem;margin:4px 0">'
        f'<b>Code:</b> <code style="background:rgba(255,255,255,0.1);padding:1px 6px;border-radius:6px;'
        f'font-size:.80rem;color:rgba(255,255,255,0.9)">{_html_esc(v.line_content[:120])}</code></p>'
        f'<p style="color:rgba(255,255,255,0.55);font-size:.82rem;margin:4px 0">'
        f'<b>Fix:</b> {_html_esc(v.remediation[:250])}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    has_detail = bool(v.rule.description or v.rule.example_bad or v.rule.example_good or v.context)
    if has_detail:
        with st.expander(f"Rule Details — {v.rule_id}", expanded=False):
            if v.rule.description:
                st.markdown(f"**Why this matters:** {v.rule.description}")
            if v.context:
                st.markdown("**Code context:**")
                st.code(v.context, language="abap")
            if v.rule.example_bad:
                col_bad, col_good = st.columns(2)
                with col_bad:
                    st.markdown("**Non-Compliant:**")
                    st.code(v.rule.example_bad, language="abap")
                with col_good:
                    st.markdown("**Compliant:**")
                    st.code(v.rule.example_good, language="abap")
            if v.rule.tags:
                tags_html = " ".join(
                    f'<span style="background:rgba(10,132,255,0.2);color:#0A84FF;border-radius:100px;'
                    f'padding:1px 8px;font-size:.74rem;border:1px solid rgba(10,132,255,0.35)">{t}</span>'
                    for t in v.rule.tags
                )
                st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)


def score_ring(score: int) -> None:
    if score >= 80:   color = "#30D158"
    elif score >= 50: color = "#FF9F0A"
    else:             color = "#FF453A"
    st.markdown(
        f'<div class="score-ring" style="--sc:{color}">{score}</div>',
        unsafe_allow_html=True,
    )


def sidebar_nav(current_user) -> None:
    with st.sidebar:
        # ── 1. Logo / brand block ────────────────────────────────────
        st.markdown("""
        <div style="padding:22px 18px 18px;border-bottom:1px solid rgba(255,255,255,0.08)">
          <div style="display:flex;align-items:center;gap:11px">
            <div style="
                background:#0A84FF;border-radius:10px;
                width:38px;height:38px;flex-shrink:0;
                display:flex;align-items:center;justify-content:center;
                font-size:1.25rem;
                box-shadow:0 2px 12px rgba(10,132,255,0.45);
            ">⚡</div>
            <div>
              <div style="font-size:1.05rem;font-weight:700;color:#FFFFFF;
                          letter-spacing:-0.3px;line-height:1.15">CodeVantage</div>
              <div style="font-size:0.67rem;color:rgba(255,255,255,0.45);letter-spacing:0.4px;
                          text-transform:uppercase;margin-top:1px">ABAP Intelligence</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 2. App Chain nav block ────────────────────────────────────
        st.markdown("""
        <div style="padding:14px 18px 4px">
          <div style="font-size:0.67rem;color:rgba(255,255,255,0.4);font-weight:700;
                      text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px">
            App Chain
          </div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("pages/cv_dashboard.py",        "🏠  Dashboard"),
            ("pages/2_🧹_Clean_Core.py",     "🧹  Clean Core"),
            ("pages/3_🚀_S4_Migration.py",   "🚀  S/4 Migration"),
            ("pages/4_📊_Analytics.py",      "📊  Analytics"),
            ("pages/6_📚_Rule_Reference.py", "📚  Rule Reference"),
        ]
        for page, label in nav_items:
            st.page_link(page, label=label)
        if current_user.has_permission("admin"):
            st.page_link("pages/5_👥_Admin.py", label="👥  User Admin")

        # ── 3. Spacer pushes user block to bottom ─────────────────────
        st.markdown(
            '<div style="flex:1;min-height:40px"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.09);margin:8px 0">',
            unsafe_allow_html=True,
        )

        # ── 4. User info + Sign Out pinned at bottom ──────────────────
        st.markdown(
            f'<div style="padding:10px 16px 4px">'
            f'<div style="font-size:0.67rem;color:rgba(255,255,255,0.4);font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.6px;margin-bottom:6px">Account</div>'
            f'<div style="display:flex;align-items:center;gap:9px;margin-bottom:10px">'
            f'<div style="background:#0A84FF;border-radius:50%;width:28px;height:28px;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:0.78rem;font-weight:700;color:#fff;flex-shrink:0">'
            f'{current_user.full_name[0].upper()}</div>'
            f'<div>'
            f'<div style="font-size:0.85rem;font-weight:600;color:#FFFFFF;'
            f'line-height:1.2">{current_user.full_name}</div>'
            f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.45);margin-top:1px">'
            f'{current_user.role_label()}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )

        if st.button("Sign Out", use_container_width=True, key="sidebar_signout"):
            from core.auth import logout
            logout()

        st.markdown(
            '<div style="text-align:center;padding:8px 0 10px">'
            '<span style="font-size:0.67rem;color:rgba(255,255,255,0.25)">'
            'v1.1.0 &nbsp;·&nbsp; Powered by SPRAC &nbsp;·&nbsp; 2025</span></div>',
            unsafe_allow_html=True,
        )


def add_to_analysis_history(entry: dict) -> None:
    import datetime
    if "cv_analysis_history" not in st.session_state:
        st.session_state["cv_analysis_history"] = []
    entry.setdefault("timestamp", datetime.datetime.now().strftime("%H:%M:%S"))
    history: list = st.session_state["cv_analysis_history"]
    history.append(entry)
    if len(history) > 20:
        st.session_state["cv_analysis_history"] = history[-20:]


def _html_esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

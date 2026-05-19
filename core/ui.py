"""
CodeVantage Shared UI Components
Salesforce Lightning-inspired enterprise design system for Streamlit.
"""

from __future__ import annotations
import streamlit as st
from typing import Optional

# ── Global CSS ────────────────────────────────────────────────────────────────

CV_CSS = """
<style>
/* ── Base & typography ───────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue",
                 Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-transform: none !important;
}
[data-testid="stAppViewContainer"] { background: #F3F2EF; }
[data-testid="stMain"] > div { padding-top: 1.75rem; }

/* ── Sidebar ─────────────────────────────────────────────────── */
/* Hide Streamlit's auto-generated page list */
[data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stSidebar"] {
    background: #032D60 !important;
    border-right: none !important;
    min-width: 230px !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* Force all sidebar text to white */
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] a {
    color: #FFFFFF !important;
    text-transform: none !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.12) !important;
}

/* Sign Out button — force override all global button styles */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button[kind="secondary"],
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.28) !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1px !important;
    text-transform: none !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover,
[data-testid="stSidebar"] button:hover {
    background: rgba(186,5,23,0.65) !important;
    border-color: rgba(255,140,140,0.45) !important;
    color: #FFFFFF !important;
}

/* Page-link nav items — full override */
[data-testid="stSidebar"] [data-testid="stPageLink"],
[data-testid="stSidebar"] [data-testid="stPageLink"] * {
    color: #C9D9EF !important;
    text-decoration: none !important;
    text-transform: none !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    border-radius: 6px !important;
    padding: 9px 12px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #C9D9EF !important;
    text-decoration: none !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    margin: 1px 0 !important;
    line-height: 1.3 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(255,255,255,0.10) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: #0176D3 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ── Page header ─────────────────────────────────────────────── */
.cv-header {
    background: #FFFFFF;
    padding: 28px 36px 24px;
    border-radius: 10px;
    margin-bottom: 24px;
    border: 1px solid #DDDBDA;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}
.cv-header h1 {
    margin: 0 0 6px 0;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: #181818;
    line-height: 1.2;
    text-transform: none !important;
}
.cv-header p {
    margin: 0;
    font-size: 0.90rem;
    color: #706E6B;
    line-height: 1.55;
}
.cv-header .cv-badge {
    display: inline-block;
    background: #E8F4FF;
    color: #0176D3;
    padding: 3px 12px;
    border-radius: 4px;
    font-size: 0.74rem;
    font-weight: 600;
    margin-top: 12px;
    letter-spacing: 0.2px;
    border: 1px solid #B0D4F5;
}

/* ── Cards ───────────────────────────────────────────────────── */
.cv-card {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 22px 24px;
    border: 1px solid #DDDBDA;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    margin-bottom: 16px;
    transition: box-shadow 0.2s ease;
}
.cv-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
}
.cv-card h3 {
    margin: 0 0 10px 0;
    font-size: 1.0rem;
    color: #181818;
    font-weight: 600;
    letter-spacing: -0.1px;
    text-transform: none !important;
}

/* ── Metric tiles ────────────────────────────────────────────── */
.cv-metric {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 20px 18px;
    border: 1px solid #DDDBDA;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    text-align: center;
    border-top: 3px solid var(--mc, #0176D3);
    transition: box-shadow 0.18s ease;
}
.cv-metric:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
}
.cv-metric .cv-metric-val {
    font-size: 2rem;
    font-weight: 700;
    color: var(--mc, #0176D3);
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
    color: #706E6B;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

/* ── Severity badges ─────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 0.71rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
.badge-CRITICAL { background: #FFDEDE; color: #BA0517; border: 1px solid #F5BCBC; }
.badge-HIGH     { background: #FEE3D2; color: #A33700; border: 1px solid #F5C4A8; }
.badge-MEDIUM   { background: #FEF7E2; color: #7A5600; border: 1px solid #F5E08A; }
.badge-LOW      { background: #E8F4FF; color: #0176D3; border: 1px solid #B0D4F5; }
.badge-INFO     { background: #F3F2EF; color: #706E6B; border: 1px solid #DDDBDA; }

/* ── Clean Core level badges ─────────────────────────────────── */
.cc-level {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 12px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.80rem;
}
.cc-A { background: #EAF5EA; color: #2E7D32; border: 1px solid #A5D6A7; }
.cc-B { background: #E8F4FF; color: #0064C8; border: 1px solid #B0D4F5; }
.cc-C { background: #FFF9E6; color: #7A5600; border: 1px solid #F5DFA0; }
.cc-D { background: #FFDEDE; color: #BA0517; border: 1px solid #F5BCBC; }

/* ── Violation row ───────────────────────────────────────────── */
.vrow {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 14px 18px;
    border: 1px solid #DDDBDA;
    border-left: 4px solid var(--vc, #706E6B);
    margin-bottom: 10px;
    transition: box-shadow 0.15s ease;
}
.vrow:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.vrow h4 { margin: 0 0 5px 0; font-size: 0.88rem; color: #181818; font-weight: 600; text-transform: none !important; }
.vrow p  { margin: 0; font-size: 0.82rem; color: #706E6B; line-height: 1.55; }
.vrow-CRITICAL { --vc: #BA0517; }
.vrow-HIGH     { --vc: #A33700; }
.vrow-MEDIUM   { --vc: #7A5600; }
.vrow-LOW      { --vc: #0176D3; }
.vrow-INFO     { --vc: #706E6B; }

/* ── Code & diff ─────────────────────────────────────────────── */
.diff-container {
    background: #1B1F23;
    border-radius: 8px;
    padding: 16px 20px;
    font-family: "SFMono-Regular", "Consolas", "Liberation Mono", monospace;
    font-size: 0.80rem;
    max-height: 520px;
    overflow-y: auto;
    line-height: 1.65;
    border: 1px solid #30363D;
}
.diff-add    { color: #7EE787; background: rgba(126,231,135,0.08); padding: 1px 4px; border-radius: 3px; }
.diff-del    { color: #FF7B72; background: rgba(255,123,114,0.08); padding: 1px 4px; border-radius: 3px; }
.diff-ctx    { color: #8B949E; }
.diff-header { color: #58A6FF; font-weight: 600; margin: 10px 0 4px; }
.diff-hunk   { color: #40C0C0; margin: 4px 0; }

/* ── Score ring ──────────────────────────────────────────────── */
.score-ring {
    width: 110px; height: 110px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; font-weight: 700;
    border: 8px solid var(--sc, #0176D3);
    color: var(--sc, #0176D3);
    background: white;
    margin: 0 auto;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

/* ── Streamlit widget overrides ──────────────────────────────── */
div[data-testid="stMetricValue"] { font-size: 1.7rem !important; font-weight: 700 !important; }

/* Primary button — Salesforce style */
.stButton > button[kind="primary"] {
    background: #0176D3 !important;
    border: 1px solid #0176D3 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #FFFFFF !important;
    padding: 8px 20px !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    transition: background 0.15s ease, box-shadow 0.15s ease !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.12) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #0A5FA6 !important;
    border-color: #0A5FA6 !important;
    box-shadow: 0 2px 6px rgba(1,118,211,0.35) !important;
}
.stButton > button[kind="primary"]:active {
    background: #014486 !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    border-radius: 6px !important;
    border: 1px solid #DDDBDA !important;
    background: #FFFFFF !important;
    color: #0176D3 !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #F3F2EF !important;
    border-color: #0176D3 !important;
}

/* Tabs — Salesforce underline style */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #DDDBDA !important;
    background: transparent !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    font-size: 0.875rem;
    border-radius: 0 !important;
    padding: 10px 18px !important;
    color: #706E6B !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    text-transform: none !important;
    transition: color 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    color: #0176D3 !important;
    font-weight: 600 !important;
    border-bottom: 3px solid #0176D3 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0176D3 !important;
    background: rgba(1,118,211,0.04) !important;
}

/* Expanders */
.stExpander {
    border-radius: 8px !important;
    border: 1px solid #DDDBDA !important;
    background: #FFFFFF !important;
    overflow: hidden;
}
.stExpander:hover { border-color: #B0B0B0 !important; }
.stExpander summary { font-weight: 600 !important; color: #181818 !important; font-size: 0.875rem !important; }

/* Forms */
[data-testid="stForm"] {
    border-radius: 8px !important;
    border: 1px solid #DDDBDA !important;
    padding: 20px !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

/* Inputs */
div[data-baseweb="select"] > div {
    border-radius: 6px !important;
    border-color: #DDDBDA !important;
    background: #FFFFFF !important;
}
input[type="text"], input[type="password"], textarea {
    border-radius: 6px !important;
    border-color: #DDDBDA !important;
    font-size: 0.875rem !important;
}
input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
    border-color: #0176D3 !important;
    box-shadow: 0 0 0 3px rgba(1,118,211,0.18) !important;
    outline: none !important;
}

/* Hide Streamlit's "Press Enter to submit form" instruction tooltip */
[data-testid="InputInstructions"],
small[data-testid="InputInstructions"] { display: none !important; }

/* Divider */
hr { border-color: #DDDBDA !important; margin: 20px 0 !important; }

/* Alerts */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 8px !important; overflow: hidden; }

/* Fix any lingering text-transform issues */
button, a, span, p, div, h1, h2, h3, h4, h5, label {
    text-transform: none !important;
}
</style>
"""

DIFF_CSS = """
<style>
.diff-container {
    background: #1B1F23; border-radius: 8px; padding: 16px 20px;
    font-family: "SFMono-Regular", "Consolas", monospace;
    font-size: 0.80rem; max-height: 550px; overflow-y: auto; line-height: 1.65;
    border: 1px solid #30363D;
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
        color = m.get("color", "#0176D3")
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
        f'<span style="font-size:.71rem;background:#F3F2EF;border:1px solid #DDDBDA;'
        f'border-radius:4px;padding:1px 7px;color:#3E3E3C;margin-left:6px;font-weight:500">'
        f'Level {v.cc_level}</span>'
        if v.cc_level else ""
    )
    st.markdown(
        f'<div class="vrow vrow-{sev}">'
        f'<h4>{severity_badge(sev)}{cc_badge}'
        f' &nbsp;<b>[{v.rule_id}]</b> {v.rule.name}'
        f'&nbsp;<span style="color:#706E6B;font-size:.78rem;font-weight:400">Line {v.line_number}</span></h4>'
        f'<p style="color:#3E3E3C;font-size:.82rem;margin:4px 0">'
        f'<b>Code:</b> <code style="background:#F3F2EF;padding:1px 5px;border-radius:3px;'
        f'font-size:.80rem">{_html_esc(v.line_content[:120])}</code></p>'
        f'<p style="color:#706E6B;font-size:.82rem;margin:4px 0">'
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
                    f'<span style="background:#E8F4FF;color:#0176D3;border-radius:4px;'
                    f'padding:1px 8px;font-size:.74rem;border:1px solid #B0D4F5">{t}</span>'
                    for t in v.rule.tags
                )
                st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)


def score_ring(score: int) -> None:
    if score >= 80:   color = "#2E7D32"
    elif score >= 50: color = "#7A5600"
    else:             color = "#BA0517"
    st.markdown(
        f'<div class="score-ring" style="--sc:{color}">{score}</div>',
        unsafe_allow_html=True,
    )


def sidebar_nav(current_user) -> None:
    with st.sidebar:
        # ── 1. Logo / brand block ────────────────────────────────────
        st.markdown("""
        <div style="padding:22px 18px 18px;border-bottom:1px solid rgba(255,255,255,0.09)">
          <div style="display:flex;align-items:center;gap:11px">
            <div style="
                background:#0176D3;border-radius:10px;
                width:38px;height:38px;flex-shrink:0;
                display:flex;align-items:center;justify-content:center;
                font-size:1.25rem;
                box-shadow:0 2px 8px rgba(1,118,211,0.40);
            ">⚡</div>
            <div>
              <div style="font-size:1.05rem;font-weight:700;color:#FFFFFF;
                          letter-spacing:-0.3px;line-height:1.15">CodeVantage</div>
              <div style="font-size:0.67rem;color:#6FA8D4;letter-spacing:0.4px;
                          text-transform:uppercase;margin-top:1px">ABAP Intelligence</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 2. App Chain nav block ────────────────────────────────────
        st.markdown("""
        <div style="padding:14px 18px 4px">
          <div style="font-size:0.67rem;color:#6FA8D4;font-weight:700;
                      text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px">
            App Chain
          </div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("app.py",                      "🏠  Dashboard"),
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
            f'<div style="font-size:0.67rem;color:#6FA8D4;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.6px;margin-bottom:6px">Account</div>'
            f'<div style="display:flex;align-items:center;gap:9px;margin-bottom:10px">'
            f'<div style="background:#0176D3;border-radius:50%;width:28px;height:28px;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:0.78rem;font-weight:700;color:#fff;flex-shrink:0">'
            f'{current_user.full_name[0].upper()}</div>'
            f'<div>'
            f'<div style="font-size:0.85rem;font-weight:600;color:#FFFFFF;'
            f'line-height:1.2">{current_user.full_name}</div>'
            f'<div style="font-size:0.72rem;color:#6FA8D4;margin-top:1px">'
            f'{current_user.role_label()}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )

        if st.button("Sign Out", use_container_width=True, key="sidebar_signout"):
            from core.auth import logout
            logout()

        st.markdown(
            '<div style="text-align:center;padding:8px 0 10px">'
            '<span style="font-size:0.67rem;color:#3D6E96">'
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

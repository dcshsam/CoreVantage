"""
CodeVantage — Product Launcher
Entry point after login + LLM gate. Shows 2 product cards.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="CodeVantage — Home",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from core.auth import is_authenticated, render_login_page, current_user, logout
from core.ui import inject_css

inject_css()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not is_authenticated():
    render_login_page()
    st.stop()

user = current_user()

# ── LLM gate ──────────────────────────────────────────────────────────────────
if not st.session_state.get("cv_llm_client"):
    st.switch_page("pages/1_🔑_LLM_Setup.py")

# ── Hide sidebar on launcher ──────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Each card column becomes a positioned container */
[data-testid="column"] { position: relative !important; }

/* Invisible full-column overlay — uses Streamlit SPA routing (session preserved) */
[data-testid="column"] [data-testid="stPageLink"] {
    position: absolute !important;
    inset: 0 !important;
    z-index: 20 !important;
    height: 100% !important;
    width: 100% !important;
}
/* Hide every child element of the page link */
[data-testid="column"] [data-testid="stPageLink"],
[data-testid="column"] [data-testid="stPageLink"] * {
    opacity: 0 !important;
    font-size: 0 !important;
    color: transparent !important;
}
/* But keep the anchor itself clickable and full-size */
[data-testid="column"] [data-testid="stPageLink"] a {
    display: block !important;
    position: absolute !important;
    inset: 0 !important;
    cursor: pointer !important;
    pointer-events: auto !important;
}

/* Card hover effect — Apple dark */
.cv-card { transition: border-color .2s, transform .2s; }
[data-testid="column"]:hover .cv-card {
    border-color: rgba(10,132,255,0.45) !important;
    transform: translateY(-3px);
}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:16px 4px 14px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:40px">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="background:#0A84FF;border-radius:12px;width:40px;height:40px;
                display:flex;align-items:center;justify-content:center;
                font-size:1.2rem;box-shadow:0 2px 14px rgba(10,132,255,0.45)">⚡</div>
    <div>
      <div style="font-size:1.1rem;font-weight:700;color:#FFFFFF">CodeVantage</div>
      <div style="font-size:0.68rem;color:rgba(255,255,255,0.45);font-weight:600;
                  text-transform:uppercase;letter-spacing:.5px">ABAP Intelligence Platform</div>
    </div>
  </div>
  <div style="font-size:0.82rem;color:rgba(255,255,255,0.55)">
    Signed in as <strong style="color:#FFFFFF">{user.full_name or user.username}</strong>
    &nbsp;·&nbsp;
    <span style="background:rgba(48,209,88,0.2);color:#30D158;font-size:.72rem;font-weight:600;
                 padding:2px 10px;border-radius:100px;border:1px solid rgba(48,209,88,0.4)">
      ✅ {st.session_state.get('cv_llm_display','LLM Connected')}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Welcome ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:36px">
  <h2 style="color:#FFFFFF;font-size:1.4rem;font-weight:700;margin-bottom:6px">
    Select an Application
  </h2>
  <p style="color:rgba(255,255,255,0.5);font-size:.9rem;margin:0">
    Choose a platform to get started
  </p>
</div>
""", unsafe_allow_html=True)

# ── Two product cards ─────────────────────────────────────────────────────────
CHIP_BLUE  = "background:rgba(10,132,255,0.2);color:#0A84FF;border-radius:100px;padding:2px 12px;font-size:.74rem;font-weight:600;border:1px solid rgba(10,132,255,0.4)"
CHIP_GREEN = "background:rgba(48,209,88,0.2);color:#30D158;border-radius:100px;padding:2px 12px;font-size:.74rem;font-weight:600;border:1px solid rgba(48,209,88,0.4)"
CARD_DESC  = "color:rgba(255,255,255,0.55);font-size:.875rem;margin-bottom:18px;line-height:1.6;min-height:80px"

_, col1, col2, _ = st.columns([0.5, 3, 3, 0.5], gap="large")

with col1:
    st.markdown(f"""
    <div class="cv-card" style="min-height:260px;display:flex;flex-direction:column;
         border-top:4px solid #0A84FF;padding:24px 24px 20px;cursor:pointer">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
        <div style="background:rgba(10,132,255,0.2);border-radius:12px;width:50px;height:50px;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;font-size:1.5rem;
                    border:1px solid rgba(10,132,255,0.35)">⚡</div>
        <div>
          <h3 style="margin:0;font-size:1.15rem;color:#FFFFFF;font-weight:700">CodeVantage</h3>
          <div style="font-size:0.7rem;color:#0A84FF;font-weight:600;
               text-transform:uppercase;letter-spacing:.5px">ABAP Intelligence Platform</div>
        </div>
      </div>
      <p style="{CARD_DESC}">
        Analyse ABAP code against SAP Clean Core standards (Levels A–D, August 2025 model).
        Detect violations, deprecated constructs, and security issues — then auto-remediate
        to production-ready, ABAP Cloud-compliant code with AI.
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:auto">
        <span style="{CHIP_BLUE}">38+ Rules</span>
        <span style="{CHIP_BLUE}">Clean Core A–D</span>
        <span style="{CHIP_BLUE}">S/4HANA Migration</span>
        <span style="{CHIP_BLUE}">Auto-Remediation</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/cv_dashboard.py", label="Open CodeVantage", use_container_width=True)

with col2:
    st.markdown(f"""
    <div class="cv-card" style="min-height:260px;display:flex;flex-direction:column;
         border-top:4px solid #30D158;padding:24px 24px 20px;cursor:pointer">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
        <div style="background:rgba(48,209,88,0.2);border-radius:12px;width:50px;height:50px;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;font-size:1.5rem;
                    border:1px solid rgba(48,209,88,0.35)">🔄</div>
        <div>
          <h3 style="margin:0;font-size:1.15rem;color:#FFFFFF;font-weight:700">E2E Support</h3>
          <div style="font-size:0.7rem;color:#30D158;font-weight:600;
               text-transform:uppercase;letter-spacing:.5px">End to End SAP Support</div>
        </div>
      </div>
      <p style="{CARD_DESC}">
        End-to-end SAP support tooling — from requirement to deployment.
        AI-assisted workflows for functional specifications, ABAP code review,
        and solution documentation across the full SAP delivery lifecycle.
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:auto">
        <span style="{CHIP_GREEN}">BRD → Spec → Code</span>
        <span style="{CHIP_GREEN}">ABAP / UI5 / CAP</span>
        <span style="{CHIP_GREEN}">Word / PDF Export</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/e2e_support.py", label="Open E2E Support", use_container_width=True)

# ── Sign out + footer ─────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:44px'></div>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([4, 1, 4])
with btn_col:
    if st.button("Sign Out", use_container_width=True, key="btn_signout"):
        logout()
        st.rerun()

st.markdown(
    "<div style='text-align:center;margin-top:20px;color:rgba(255,255,255,0.25);font-size:.75rem'>"
    "v1.1.0 · Powered by SPRAC · 2025</div>",
    unsafe_allow_html=True,
)

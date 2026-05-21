"""
CoreShift — Product Launcher
Entry point after login + LLM gate. Shows 2 product cards.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="CoreShift — Home",
    page_icon="🔀",
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

/* Equal-height card columns */
div[data-testid="stHorizontalBlock"] { align-items: stretch !important; }

/* Cards */
.cv-card {
    flex: 1 !important;
    transition: box-shadow .15s, transform .15s;
}

/* ── Transparent click-overlay buttons ──────────────────────────────────────
   The stVerticalBlock inside each card column becomes a positioning context.
   The stButton (rendered before the card markdown) is then positioned
   absolutely to cover the entire column — opacity 0 but fully clickable.    */
[data-testid="stColumn"]:has(.cv-card-cv)  [data-testid="stVerticalBlock"],
[data-testid="stColumn"]:has(.cv-card-e2e) [data-testid="stVerticalBlock"] {
    position: relative !important;
}
[data-testid="stColumn"]:has(.cv-card-cv)  [data-testid="stButton"],
[data-testid="stColumn"]:has(.cv-card-e2e) [data-testid="stButton"] {
    position: absolute !important;
    inset: 0 !important;
    z-index: 50 !important;
}
[data-testid="stColumn"]:has(.cv-card-cv)  [data-testid="stButton"] button,
[data-testid="stColumn"]:has(.cv-card-e2e) [data-testid="stButton"] button {
    width: 100% !important;
    height: 100% !important;
    opacity: 0 !important;
    cursor: pointer !important;
    background: transparent !important;
    border: none !important;
}
/* Hover effect: button sits above card in DOM, so ~ targets the card sibling */
[data-testid="stColumn"]:has(.cv-card-cv)  [data-testid="stButton"]:hover ~ div .cv-card,
[data-testid="stColumn"]:has(.cv-card-e2e) [data-testid="stButton"]:hover ~ div .cv-card {
    box-shadow: 0 8px 24px rgba(0,0,0,.18) !important;
    transform: translateY(-3px) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:16px 4px 14px;border-bottom:1px solid #DDDBDA;margin-bottom:40px">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="background:#0176D3;border-radius:10px;width:38px;height:38px;
                display:flex;align-items:center;justify-content:center;
                font-size:1.2rem;box-shadow:0 2px 8px rgba(1,118,211,0.35)"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M4 9L12 12L4 15" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 9L20 12L12 15" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
    <div>
      <div style="font-size:1.1rem;font-weight:700;color:#032D60">CoreShift</div>
      <div style="font-size:0.68rem;color:#706E6B;font-weight:600;
                  text-transform:uppercase;letter-spacing:.5px">SAP Move — Intelligent SAP Migration Platform</div>
    </div>
  </div>
  <div style="font-size:0.82rem;color:#706E6B">
    Signed in as <strong style="color:#032D60">{user.full_name or user.username}</strong>
    &nbsp;·&nbsp;
    <span style="background:#EEF6EC;color:#2E844A;font-size:.72rem;font-weight:600;
                 padding:2px 8px;border-radius:4px;border:1px solid #91C98C">
      ✅ {st.session_state.get('cv_llm_display','LLM Connected')}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Welcome ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:36px">
  <h2 style="color:#032D60;font-size:1.4rem;font-weight:700;margin-bottom:6px">
    Select an Application
  </h2>
  <p style="color:#706E6B;font-size:.9rem;margin:0">
    Choose a platform to get started
  </p>
</div>
""", unsafe_allow_html=True)

# ── Two product cards ─────────────────────────────────────────────────────────
CHIP_BLUE  = "background:#E8F4FF;color:#0176D3;border-radius:4px;padding:2px 10px;font-size:.74rem;font-weight:600;border:1px solid #B0D4F5"
CHIP_GREEN = "background:#EEF6EC;color:#2E844A;border-radius:4px;padding:2px 10px;font-size:.74rem;font-weight:600;border:1px solid #B8DDB0"
CARD_DESC  = "color:#706E6B;font-size:.875rem;margin-bottom:18px;line-height:1.6;min-height:80px"

_, col1, col2, _ = st.columns([0.5, 3, 3, 0.5], gap="large")

with col1:
    # Invisible overlay button — renders first so CSS ~ sibling hover reaches the card below
    if st.button("CoreShift", key="cv_card_btn", use_container_width=True):
        st.switch_page("pages/cv_dashboard.py")
    st.markdown(f"""
    <div class="cv-card cv-card-cv" style="min-height:280px;display:flex;flex-direction:column;
         border-top:4px solid #0176D3;padding:28px 26px 24px">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
        <div style="background:#E8F4FF;border-radius:10px;width:50px;height:50px;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;
                    border:1px solid #B0D4F5;box-shadow:0 2px 6px rgba(1,118,211,0.15)">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
            <path d="M4 9L12 12L4 15" stroke="#0176D3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 9L20 12L12 15" stroke="#0176D3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <h3 style="margin:0;font-size:1.15rem;color:#032D60;font-weight:700;line-height:1.2">CoreShift</h3>
          <div style="font-size:0.68rem;color:#0176D3;font-weight:600;
               text-transform:uppercase;letter-spacing:.5px;margin-top:2px">SAP Move — Intelligent SAP Migration Platform</div>
        </div>
      </div>
      <p style="{CARD_DESC}">
        Analyse ABAP code against SAP Clean Core standards (Levels A–D, August 2025 model).
        Detect violations, deprecated constructs, and security issues — then auto-remediate
        to production-ready, ABAP Cloud-compliant code with AI.
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:12px;
                  border-top:1px solid #F0F0EE">
        <span style="{CHIP_BLUE}">38+ Rules</span>
        <span style="{CHIP_BLUE}">Clean Core A–D</span>
        <span style="{CHIP_BLUE}">S/4HANA Migration</span>
        <span style="{CHIP_BLUE}">Auto-Remediation</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Invisible overlay button — renders first so CSS ~ sibling hover reaches the card below
    if st.button("E2E Support", key="e2e_card_btn", use_container_width=True):
        st.switch_page("pages/e2e_support.py")
    st.markdown(f"""
    <div class="cv-card cv-card-e2e" style="min-height:280px;display:flex;flex-direction:column;
         border-top:4px solid #2E844A;padding:28px 26px 24px">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
        <div style="background:#EEF6EC;border-radius:10px;width:50px;height:50px;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;font-size:1.5rem;
                    border:1px solid #B8DDB0;box-shadow:0 2px 6px rgba(46,132,74,0.15)">🔄</div>
        <div>
          <h3 style="margin:0;font-size:1.15rem;color:#032D60;font-weight:700;line-height:1.2">E2E Support</h3>
          <div style="font-size:0.68rem;color:#2E844A;font-weight:600;
               text-transform:uppercase;letter-spacing:.5px;margin-top:2px">End to End SAP Support</div>
        </div>
      </div>
      <p style="{CARD_DESC}">
        End-to-end SAP support tooling — from requirement to deployment.
        AI-assisted workflows for functional specifications, ABAP code review,
        and solution documentation across the full SAP delivery lifecycle.
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:12px;
                  border-top:1px solid #F0F0EE">
        <span style="{CHIP_GREEN}">Functional Spec</span>
        <span style="{CHIP_GREEN}">Technical Spec</span>
        <span style="{CHIP_GREEN}">SAP Code Gen</span>
        <span style="{CHIP_GREEN}">ZIP Export</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Sign out + footer ─────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:44px'></div>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([4, 1, 4])
with btn_col:
    if st.button("Sign Out", use_container_width=True, key="btn_signout"):
        logout()

st.markdown(
    "<div style='text-align:center;margin-top:20px;color:#706E6B;font-size:.75rem'>"
    "v1.1.0 · Powered by SPRAC · 2025</div>",
    unsafe_allow_html=True,
)

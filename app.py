"""
CodeVantage — Enterprise ABAP Intelligence Platform
Main entry point: login gate → LLM gate → executive dashboard.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="CodeVantage — ABAP Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.auth import is_authenticated, render_login_page, current_user, logout
from core.ui import inject_css, page_header, metric_row, sidebar_nav

inject_css()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not is_authenticated():
    render_login_page()
    st.stop()

user = current_user()

# ── LLM gate — redirect to setup page if not configured ──────────────────────
if not st.session_state.get("cv_llm_client"):
    st.switch_page("pages/1_🔑_LLM_Setup.py")

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_nav(user)

# ── Dashboard ─────────────────────────────────────────────────────────────────
page_header(
    "CodeVantage",
    "Enterprise ABAP Intelligence Platform — Clean Core & S/4HANA Migration",
    badge=f"AI Connected · {st.session_state.get('cv_llm_display', '')}",
)

# ── KPI row ───────────────────────────────────────────────────────────────────
from core.auth import load_users
from core.abap_rules import ALL_RULES
all_users = load_users()
total_analyses = sum(u.analyses_run for u in all_users)

metric_row([
    {"label": "Analyses Run",    "value": f"{total_analyses:,}",                       "color": "#0176D3"},
    {"label": "Platform Users",  "value": str(len(all_users)),                         "color": "#2E844A"},
    {"label": "LLM Provider",    "value": st.session_state.get("cv_llm_display", "—"), "color": "#7B2D8B"},
    {"label": "ABAP Rules",      "value": str(len(ALL_RULES)),                         "color": "#A33700"},
    {"label": "Your Role",       "value": user.role.title(),                           "color": "#0A5FA6"},
])

st.markdown("---")

# ── Feature cards ─────────────────────────────────────────────────────────────
CHIP        = "background:#E8F4FF;color:#0176D3;border-radius:4px;padding:2px 10px;font-size:.74rem;font-weight:600;border:1px solid #B0D4F5"
CHIP_ORANGE = "background:#FEE3D2;color:#A33700;border-radius:4px;padding:2px 10px;font-size:.74rem;font-weight:600;border:1px solid #F5C4A8"
CARD_DESC   = "color:#706E6B;font-size:.875rem;margin-bottom:14px;line-height:1.6;min-height:72px"

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(f"""
    <div class="cv-card" style="min-height:200px;display:flex;flex-direction:column">
      <h3>🧹 Clean Core Analysis</h3>
      <p style="{CARD_DESC}">
        Analyse ABAP code against SAP Clean Core standards (Levels A–D, August 2025 model).
        Detect API violations, deprecated constructs, and security issues —
        then auto-remediate to production-ready, ABAP Cloud-compliant code.
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:auto">
        <span style="{CHIP}">38+ Rules</span>
        <span style="{CHIP}">AI Analysis</span>
        <span style="{CHIP}">Auto-Remediation</span>
        <span style="{CHIP}">Export</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Clean Core Analyser", type="primary", use_container_width=True, key="btn_cc"):
        st.switch_page("pages/2_🧹_Clean_Core.py")

with col2:
    st.markdown(f"""
    <div class="cv-card" style="min-height:200px;display:flex;flex-direction:column">
      <h3>🚀 ECC → S/4HANA Migration</h3>
      <p style="{CARD_DESC}">
        Identify ECC-specific constructs incompatible with S/4HANA (incl. MATNR 40-char,
        RAP BAdI replacements, ATC CLOUD_READINESS checks). Get migration readiness scores,
        effort estimates, and sprint plans with AI.
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:auto">
        <span style="{CHIP_ORANGE}">Readiness Score</span>
        <span style="{CHIP_ORANGE}">Simplification List</span>
        <span style="{CHIP_ORANGE}">Sprint Roadmap</span>
        <span style="{CHIP_ORANGE}">RC2 Upload</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Migration Analyser", type="primary", use_container_width=True, key="btn_s4"):
        st.switch_page("pages/3_🚀_S4_Migration.py")

col3, col4 = st.columns(2, gap="medium")

with col3:
    st.markdown("""
    <div class="cv-card" style="min-height:140px">
      <h3>📚 Rule Reference Catalog</h3>
      <p style="color:#706E6B;font-size:.875rem;line-height:1.6;min-height:60px">
        Browse, search, and filter all 38+ built-in ABAP rules with descriptions,
        non-compliant/compliant examples, and Clean Core level classification.
        Includes the August 2025 A–D extensibility guide.
      </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Browse Rule Catalog", use_container_width=True, key="btn_rules"):
        st.switch_page("pages/6_📚_Rule_Reference.py")

with col4:
    st.markdown("""
    <div class="cv-card" style="min-height:140px">
      <h3>📊 Analytics & Reports</h3>
      <p style="color:#706E6B;font-size:.875rem;line-height:1.6;min-height:60px">
        Visualise compliance trends, violation distributions, and migration readiness
        across your custom code landscape. Track session history and generate
        executive-level compliance reports.
      </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Analytics", use_container_width=True, key="btn_analytics"):
        st.switch_page("pages/4_📊_Analytics.py")

st.markdown("---")

with st.expander("📖 Quick Start Guide", expanded=total_analyses == 0):
    st.markdown("""
    ### Getting Started with CodeVantage

    **Step 1 — Configure your LLM** *(done ✅)*

    **Step 2 — Analyse your ABAP code**
    Choose your input method on the Clean Core or S/4 Migration page:
    - 📋 **Paste code** directly into the editor
    - 🔗 **Connect SAP system** (ECC/S4) via REST/ADT API
    - 📁 **Upload SAP Readiness Check 2** Excel report

    **Step 3 — Review & Remediate**
    - Clean Core maturity level (A–D per August 2025 SAP model)
    - Violations with rule details, context snippets, and compliant code examples
    - AI-powered deep analysis and auto-generated remediated code with diff view

    **Step 4 — Export & Deploy**
    Download remediated code, Word/PDF reports, or Excel violation lists.
    """)

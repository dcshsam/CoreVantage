"""
CodeVantage — ABAP Intelligence Dashboard
Reached from the launcher (app.py) after LLM is connected.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="CodeVantage — ABAP Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.auth import require_auth
from core.ui import inject_css, page_header, metric_row, sidebar_nav

inject_css()
user = require_auth()

# ── Sidebar ───────────────────────────────────────────────────────────────────
sidebar_nav(user)

# ── Dashboard header ──────────────────────────────────────────────────────────
page_header(
    "CodeVantage",
    "Enterprise ABAP Intelligence Platform — Clean Core & S/4HANA Migration",
    badge="AI Connected" if st.session_state.get("cv_llm_client") else "Configure LLM to enable AI",
)

# ── KPI row ───────────────────────────────────────────────────────────────────
from core.auth import load_users
from core.abap_rules import ALL_RULES
all_users      = load_users()
total_analyses = sum(u.analyses_run for u in all_users)
llm_connected  = bool(st.session_state.get("cv_llm_client"))

metric_row([
    {"label": "Analyses Run",   "value": f"{total_analyses:,}",                       "color": "#0A84FF"},
    {"label": "Platform Users", "value": str(len(all_users)),                         "color": "#30D158"},
    {"label": "LLM Provider",   "value": st.session_state.get("cv_llm_display", "—"), "color": "#BF5AF2"},
    {"label": "ABAP Rules",     "value": str(len(ALL_RULES)),                         "color": "#FF9F0A"},
    {"label": "Your Role",      "value": user.role.title(),                           "color": "#5AC8FA"},
])

st.markdown("---")

# ── Feature cards — 2×2 grid ──────────────────────────────────────────────────
CHIP        = "background:rgba(10,132,255,0.2);color:#0A84FF;border-radius:100px;padding:2px 12px;font-size:.74rem;font-weight:600;border:1px solid rgba(10,132,255,0.4)"
CHIP_ORANGE = "background:rgba(255,159,10,0.2);color:#FF9F0A;border-radius:100px;padding:2px 12px;font-size:.74rem;font-weight:600;border:1px solid rgba(255,159,10,0.4)"
CARD_DESC   = "color:rgba(255,255,255,0.55);font-size:.875rem;margin-bottom:14px;line-height:1.6;min-height:72px"

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown(f"""
    <div class="cv-card" style="min-height:200px;display:flex;flex-direction:column;border-top:3px solid #0A84FF">
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
    if st.button("Open Clean Core Analyser", type="primary", use_container_width=True):
        st.switch_page("pages/2_🧹_Clean_Core.py")

with col2:
    st.markdown(f"""
    <div class="cv-card" style="min-height:200px;display:flex;flex-direction:column;border-top:3px solid #FF9F0A">
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
    if st.button("Open Migration Analyser", type="primary", use_container_width=True):
        st.switch_page("pages/3_🚀_S4_Migration.py")

col3, col4 = st.columns(2, gap="medium")

with col3:
    st.markdown("""
    <div class="cv-card" style="min-height:140px">
      <h3>📚 Rule Reference Catalog</h3>
      <p style="color:rgba(255,255,255,0.55);font-size:.875rem;line-height:1.6;min-height:60px">
        Browse, search, and filter all 38+ built-in ABAP rules with descriptions,
        non-compliant/compliant examples, and Clean Core level classification.
        Includes the August 2025 A–D extensibility guide.
      </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Browse Rule Catalog", use_container_width=True):
        st.switch_page("pages/6_📚_Rule_Reference.py")

with col4:
    st.markdown("""
    <div class="cv-card" style="min-height:140px">
      <h3>📊 Analytics & Reports</h3>
      <p style="color:rgba(255,255,255,0.55);font-size:.875rem;line-height:1.6;min-height:60px">
        Visualise compliance trends, violation distributions, and migration readiness
        across your custom code landscape. Track session history and generate
        executive-level compliance reports.
      </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Analytics", use_container_width=True):
        st.switch_page("pages/4_📊_Analytics.py")

st.markdown("---")

# ── Quick-start guide ─────────────────────────────────────────────────────────
with st.expander("📖 Quick Start Guide", expanded=total_analyses == 0):
    st.markdown("""
    ### Getting Started with CodeVantage

    **Step 1 — Analyse your ABAP code**
    Choose your input method on the Clean Core or S/4 Migration page:
    - 📋 **Paste code** directly into the editor
    - 🔗 **Connect SAP system** (ECC/S4) via REST/ADT API
    - 📁 **Upload SAP Readiness Check 2** Excel report

    **Step 2 — Review & Remediate**
    CodeVantage shows:
    - Clean Core maturity level (A–D per August 2025 SAP model)
    - Violations with rule details, context snippets, and compliant code examples
    - AI-powered deep analysis and hidden risk detection (if LLM configured)
    - Auto-generated remediated code with diff view

    **Step 3 — Export & Deploy**
    Download remediated code, Word/PDF reports, or Excel violation lists.

    **Step 4 — Browse Rules**
    Use the **📚 Rule Reference** page to understand all 38+ detection rules and study
    compliant code examples before writing new ABAP.

    ---
    **Default credentials:** `admin` / `Admin@123` — change after first login via **👥 User Admin**.
    """)

# ── Competitor comparison (collapsible) ───────────────────────────────────────
with st.expander("🏆 Why CodeVantage — Competitive Advantage"):
    st.markdown("""
    | Feature | **CodeVantage** | Panaya | smartShift | KTern.AI | RedRays |
    |---|---|---|---|---|---|
    | Clean Core + S/4 Migration | ✅ **Both** | ✅ Clean Core | ✅ Migration | ✅ Migration | ❌ Security only |
    | Aug 2025 A–D Level Model | ✅ **Native** | ❌ | ❌ | ❌ | ❌ |
    | Data stays on-premise | ✅ **BTP-native** | ❌ SaaS | ❌ SaaS | ❌ SaaS | ❌ SaaS |
    | SAP-native AI (AI Core) | ✅ **Default** | ❌ | ❌ | ❌ | ❌ |
    | Claude 4 / GPT-4o support | ✅ **All** | Partial | ❌ | Partial | ❌ |
    | Readiness Check 2 Upload | ✅ | ❌ | ❌ | ✅ | ❌ |
    | Rule Reference Catalog | ✅ **38+ rules** | ❌ | ❌ | ❌ | ❌ |
    | Open Source / Extensible | ✅ | ❌ | ❌ | ❌ | ❌ |
    | ADT + Web dual mode | ✅ | ❌ | ❌ | Web only | ADT only |
    | Security scanning | ✅ **OWASP ABAP** | ❌ | ❌ | ❌ | ✅ |
    | Free / No licence cost | ✅ | ❌ Licence | ❌ Fixed price | ❌ Licence | ❌ Licence |
    """)

"""
CoreShift — ABAP Rule Reference Catalog
Searchable, filterable guide to all 38+ built-in ABAP rules.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.auth import require_auth
from core.ui import inject_css, page_header, sidebar_nav, severity_badge
from core.abap_rules import ALL_RULES, SEVERITY_ORDER, SEVERITY_COLORS

st.set_page_config(page_title="Rule Reference — CoreShift", page_icon="📚", layout="wide")
inject_css()
user = require_auth()
sidebar_nav(user)

page_header(
    "📚 ABAP Rule Reference Catalog",
    "Complete guide to all built-in Clean Core, S/4HANA Migration, Security, and Performance rules",
    badge=f"{len(ALL_RULES)} Rules",
)

# ── Stats bar ─────────────────────────────────────────────────────────────────
cats = {}
sevs = {}
for r in ALL_RULES:
    cats[r.category] = cats.get(r.category, 0) + 1
    sevs[r.severity] = sevs.get(r.severity, 0) + 1

cat_colors = {
    "CLEAN_CORE":   "#0176D3",
    "S4_MIGRATION": "#A33700",
    "SECURITY":     "#BA0517",
    "PERFORMANCE":  "#2E844A",
}

cols = st.columns(len(cats))
for col, (cat, cnt) in zip(cols, cats.items()):
    label = cat.replace("_", " ").title()
    color = cat_colors.get(cat, "#888")
    col.markdown(
        f'<div class="cv-metric" style="--mc:{color}">'
        f'<div class="cv-metric-val">{cnt}</div>'
        f'<div class="cv-metric-lbl">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Filters ───────────────────────────────────────────────────────────────────
st.markdown("#### Filter Rules")
f1, f2, f3 = st.columns(3)

search_text = f1.text_input(
    "🔍 Search",
    placeholder="e.g. SELECT, BDC, MATNR, injection…",
    label_visibility="collapsed",
)

all_cats = sorted({r.category for r in ALL_RULES})
all_sevs = sorted({r.severity for r in ALL_RULES}, key=lambda s: SEVERITY_ORDER.get(s, 99))
all_levels = sorted({r.cc_level for r in ALL_RULES if r.cc_level})

sel_cats = f2.multiselect(
    "Category",
    all_cats,
    default=all_cats,
    format_func=lambda c: c.replace("_", " ").title(),
)
sel_sevs = f3.multiselect(
    "Severity",
    all_sevs,
    default=all_sevs,
)

# ── Filter logic ──────────────────────────────────────────────────────────────
filtered = [
    r for r in ALL_RULES
    if r.category in sel_cats
    and r.severity in sel_sevs
    and (
        not search_text
        or search_text.lower() in r.name.lower()
        or search_text.lower() in r.description.lower()
        or search_text.lower() in r.remediation.lower()
        or search_text.lower() in r.id.lower()
        or any(search_text.lower() in t for t in r.tags)
    )
]

filtered.sort(key=lambda r: (SEVERITY_ORDER.get(r.severity, 99), r.id))

st.markdown(f"**{len(filtered)}** of {len(ALL_RULES)} rules shown")
st.markdown("---")

# ── Rule cards ────────────────────────────────────────────────────────────────
LEVEL_COLORS = {"A": "#2E844A", "B": "#0176D3", "C": "#7A5600", "D": "#BA0517"}
LEVEL_LABELS = {"A": "Level A", "B": "Level B", "C": "Level C", "D": "Level D"}

for rule in filtered:
    sev_color  = SEVERITY_COLORS.get(rule.severity, "#888")
    cat_color  = cat_colors.get(rule.category, "#888")
    cat_label  = rule.category.replace("_", " ").title()
    level_color = LEVEL_COLORS.get(rule.cc_level, "#888") if rule.cc_level else "#AAA"
    level_label = LEVEL_LABELS.get(rule.cc_level, "") if rule.cc_level else ""

    badges = (
        f'<span style="background:{sev_color}18;color:{sev_color};border:1px solid {sev_color}60;'
        f'border-radius:4px;padding:2px 9px;font-size:.72rem;font-weight:700">{rule.severity}</span>'
        f'&nbsp;'
        f'<span style="background:{cat_color}12;color:{cat_color};border:1px solid {cat_color}50;'
        f'border-radius:4px;padding:2px 9px;font-size:.72rem;font-weight:600">{cat_label}</span>'
    )
    if level_label:
        badges += (
            f'&nbsp;<span style="background:{level_color}12;color:{level_color};border:1px solid {level_color}50;'
            f'border-radius:4px;padding:2px 9px;font-size:.72rem;font-weight:600">{level_label}</span>'
        )
    if rule.s4_impact:
        badges += (
            f'&nbsp;<span style="background:#FEE3D2;color:#A33700;border:1px solid #F5C4A880;'
            f'border-radius:4px;padding:2px 9px;font-size:.72rem;font-weight:600">S/4 Impact</span>'
        )

    with st.expander(f"**[{rule.id}]** {rule.name}", expanded=False):
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown("")

        st.markdown(f"**Description**")
        st.markdown(rule.description)

        st.markdown(f"**Remediation**")
        st.info(rule.remediation)

        if rule.example_bad or rule.example_good:
            col_b, col_g = st.columns(2)
            with col_b:
                st.markdown("**❌ Non-compliant example:**")
                if rule.example_bad:
                    st.code(rule.example_bad, language="abap")
                else:
                    st.caption("No example available")
            with col_g:
                st.markdown("**✅ Compliant example:**")
                if rule.example_good:
                    st.code(rule.example_good, language="abap")
                else:
                    st.caption("No example available")

        if rule.tags:
            tags_html = " ".join(
                f'<span style="background:#E8F4FF;color:#0176D3;border-radius:4px;'
                f'padding:2px 9px;font-size:.72rem;font-weight:500;border:1px solid #B0D4F5;'
                f'margin:2px;display:inline-block">{t}</span>'
                for t in rule.tags
            )
            st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)

        # Pattern count info
        st.caption(f"Rule ID: `{rule.id}` · {len(rule.patterns)} detection pattern(s)")

st.markdown("---")

# ── Clean Core level guide ────────────────────────────────────────────────────
with st.expander("📖 SAP Clean Core A–D Level Guide (August 2025)", expanded=False):
    st.markdown("""
    SAP formalised the **A–D extensibility maturity model** in **August 2025** to give teams a
    consistent way to classify every custom extension and manage upgrade risk.

    | Level | Label | ATC Result | Description |
    |---|---|---|---|
    | **A** | Gold Standard | ✅ No findings | Uses only released SAP APIs via ABAP Cloud or BTP side-by-side. Fully upgrade-safe. |
    | **B** | Conditionally Acceptable | ℹ️ Informational | Classic stable APIs (BAPIs, IDocs, RFCs). Governance-approved. Generally upgrade-stable. |
    | **C** | Needs Remediation | ⚠️ Warnings | Accesses SAP internal objects. Carries upgrade risk. Needs a documented remediation roadmap. |
    | **D** | Non-Compliant | ❌ Errors | Core modifications, direct writes to SAP tables, implicit enhancements. Transport blocker. Retirement timeline required. |

    **Key tools:**
    - **ATC CLOUD_READINESS** — Run via SCI transaction or ADT to auto-classify all extensions as A–D
    - **SYCM** — S/4HANA Simplification Database — identifies breaking changes before upgrade
    - **api.sap.com** — SAP Business Accelerator Hub — find released APIs and RAP BAdIs
    - **SAP Note 3565942** — Delivers clean core ATC checks on S/4HANA 2023 systems

    **Target:** All new development should be Level A. Level C code needs a 12-month refactor plan.
    Level D code needs an immediate retirement timeline.
    """)

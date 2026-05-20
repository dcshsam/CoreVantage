"""
CoreShift — E2E Support: End-to-End SAP Solution Generator
5-step AI wizard: LLM Config → BRD → Functional Spec → Technical Spec → SAP Code
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="E2E Support — CoreShift",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.auth import require_auth
from core.ui import inject_css, sidebar_nav

inject_css()
user = require_auth()
sidebar_nav(user)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("e2e_step",      1),
    ("e2e_brd",       ""),
    ("e2e_func_spec", ""),
    ("e2e_tech_spec", ""),
    ("e2e_code",      ""),
    ("e2e_code_type", "abap"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

STEPS = [
    ("🔑", "LLM Configuration"),
    ("📋", "Business Requirements"),
    ("📊", "Functional Specification"),
    ("⚙️", "Technical Specification"),
    ("💻", "SAP Code Generation"),
]

step = st.session_state.e2e_step
llm  = st.session_state.get("cv_llm_client")

# ── Layout ────────────────────────────────────────────────────────────────────
nav_col, main_col = st.columns([1.8, 4.2], gap="large")

# ── Left navigation panel ─────────────────────────────────────────────────────
with nav_col:
    rows = ""
    for i, (icon, label) in enumerate(STEPS, 1):
        if i < step:
            rows += f"""<div style="display:flex;align-items:center;gap:10px;padding:7px 10px;border-radius:6px">
                          <span>✅</span>
                          <span style="font-size:.86rem;color:#2E844A;font-weight:600">{label}</span>
                        </div>"""
        elif i == step:
            rows += f"""<div style="display:flex;align-items:center;gap:10px;padding:7px 10px;
                             border-radius:6px;background:#E8F4FF">
                          <span style="font-size:1rem">{icon}</span>
                          <span style="font-size:.86rem;color:#0176D3;font-weight:700">{label}</span>
                        </div>"""
        else:
            rows += f"""<div style="display:flex;align-items:center;gap:10px;padding:7px 10px;border-radius:6px">
                          <span style="font-size:1rem;opacity:.35">{icon}</span>
                          <span style="font-size:.86rem;color:#B0B0B0">{label}</span>
                        </div>"""

    progress_pct = int(step / len(STEPS) * 100)

    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #DDDBDA;border-radius:10px;padding:20px 16px 16px">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
        <span style="font-size:1.3rem">🏭</span>
        <span style="font-size:1.0rem;font-weight:700;color:#032D60">SAP AI Assistant</span>
      </div>
      <div style="font-size:.77rem;color:#706E6B;font-style:italic;margin-bottom:16px">
        End-to-End SAP Solution Generator
      </div>
      <hr style="border:none;border-top:1px solid #EAEAEA;margin:0 0 8px">
      {rows}
      <hr style="border:none;border-top:1px solid #EAEAEA;margin:8px 0 10px">
      <div style="font-size:.76rem;color:#706E6B;margin-bottom:5px">Step {step} of {len(STEPS)}</div>
      <div style="background:#E8F4FF;border-radius:4px;height:6px;overflow:hidden">
        <div style="background:#0176D3;width:{progress_pct}%;height:100%;border-radius:4px"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if step > 1:
        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
        if st.button("🔁 Start Over", use_container_width=True, key="nav_reset"):
            for k in ["e2e_step","e2e_brd","e2e_func_spec","e2e_tech_spec","e2e_code","e2e_code_type"]:
                st.session_state.pop(k, None)
            st.rerun()

# ── Main content ──────────────────────────────────────────────────────────────
with main_col:

    # ── Step 1: LLM Configuration ─────────────────────────────────────────────
    if step == 1:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          🔑 LLM Configuration
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:20px">
          An AI provider must be connected to power the document generation pipeline.
        </p>
        """, unsafe_allow_html=True)

        if llm:
            st.success(f"✅ LLM Connected: **{st.session_state.get('cv_llm_display', 'Connected')}**")
            st.markdown("You're all set — click **Next** to enter your business requirements.")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Next →", type="primary", key="s1_next"):
                st.session_state.e2e_step = 2
                st.rerun()
        else:
            st.warning("⚠️ No LLM connected. Please configure one first.")
            if st.button("🔑 Go to LLM Setup", type="primary", key="s1_setup"):
                st.switch_page("pages/1_🔑_LLM_Setup.py")

    # ── Step 2: Business Requirements ─────────────────────────────────────────
    elif step == 2:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          📋 Business Requirements
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          Describe the business problem or requirement in detail — include process context,
          SAP module, stakeholders, and expected outcomes.
        </p>
        """, unsafe_allow_html=True)

        brd = st.text_area(
            "Business Requirement Document (BRD)",
            value=st.session_state.e2e_brd,
            height=340,
            placeholder="""Example:
We need to automate vendor invoice processing in SAP MM. Currently invoices are manually
entered via MIRO by the AP team.

Requirements:
- Auto-read invoice PDFs from a shared folder
- 3-way matching against PO, GR and Invoice
- Auto-post when match is found; route for approval on discrepancy
- Email notifications for approvals/rejections
- Weekly reconciliation report

SAP Module: MM-LIV (Logistics Invoice Verification)
Target: SAP S/4HANA 2023
Users: AP Team (20), Finance Managers (5 approvers)""",
        )

        c1, c2 = st.columns([1, 5])
        with c1:
            if st.button("← Back", key="s2_back", use_container_width=True):
                st.session_state.e2e_step = 1
                st.rerun()
        with c2:
            if st.button("Next →", type="primary", key="s2_next", disabled=not brd.strip()):
                st.session_state.e2e_brd       = brd
                st.session_state.e2e_func_spec = ""
                st.session_state.e2e_tech_spec = ""
                st.session_state.e2e_code      = ""
                st.session_state.e2e_step      = 3
                st.rerun()

    # ── Step 3: Functional Specification ──────────────────────────────────────
    elif step == 3:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          📊 Functional Specification
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          AI generates a comprehensive SAP Functional Specification from your business requirements.
          You can edit the output before proceeding.
        </p>
        """, unsafe_allow_html=True)

        if not st.session_state.e2e_func_spec:
            c1, c2 = st.columns([2, 5])
            with c1:
                if st.button("⚡ Generate Functional Spec", type="primary", key="s3_gen",
                             use_container_width=True):
                    from prompts.e2e_templates import FUNCTIONAL_SPEC_SYSTEM, functional_spec_prompt
                    with st.spinner("Generating Functional Specification — this may take a minute…"):
                        try:
                            result = llm.complete(
                                FUNCTIONAL_SPEC_SYSTEM,
                                functional_spec_prompt(st.session_state.e2e_brd),
                                max_tokens=4000,
                            )
                            st.session_state.e2e_func_spec = result
                            st.session_state.e2e_tech_spec = ""
                            st.session_state.e2e_code      = ""
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Generation failed: {exc}")
            with c2:
                if st.button("← Back", key="s3_back_pre"):
                    st.session_state.e2e_step = 2
                    st.rerun()
        else:
            edited = st.text_area(
                "Functional Specification (editable)",
                value=st.session_state.e2e_func_spec,
                height=460,
                key="s3_edit",
            )
            st.session_state.e2e_func_spec = edited

            dl, regen, _, back, nxt = st.columns([1.6, 1.4, 2, 1, 1])
            with dl:
                st.download_button("⬇️ Download .txt", data=edited,
                                   file_name="functional_spec.txt", mime="text/plain",
                                   use_container_width=True)
            with regen:
                if st.button("🔄 Regenerate", key="s3_regen", use_container_width=True):
                    st.session_state.e2e_func_spec = ""
                    st.rerun()
            with back:
                if st.button("← Back", key="s3_back", use_container_width=True):
                    st.session_state.e2e_step = 2
                    st.rerun()
            with nxt:
                if st.button("Next →", type="primary", key="s3_next", use_container_width=True):
                    st.session_state.e2e_step = 4
                    st.rerun()

    # ── Step 4: Technical Specification ───────────────────────────────────────
    elif step == 4:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          ⚙️ Technical Specification
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          AI generates a detailed SAP Technical Specification from the Functional Specification.
          You can edit the output before proceeding to code generation.
        </p>
        """, unsafe_allow_html=True)

        if not st.session_state.e2e_tech_spec:
            c1, c2 = st.columns([2, 5])
            with c1:
                if st.button("⚡ Generate Technical Spec", type="primary", key="s4_gen",
                             use_container_width=True):
                    from prompts.e2e_templates import TECHNICAL_SPEC_SYSTEM, technical_spec_prompt
                    with st.spinner("Generating Technical Specification — this may take a minute…"):
                        try:
                            result = llm.complete(
                                TECHNICAL_SPEC_SYSTEM,
                                technical_spec_prompt(st.session_state.e2e_func_spec),
                                max_tokens=4000,
                            )
                            st.session_state.e2e_tech_spec = result
                            st.session_state.e2e_code      = ""
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Generation failed: {exc}")
            with c2:
                if st.button("← Back", key="s4_back_pre"):
                    st.session_state.e2e_step = 3
                    st.rerun()
        else:
            edited = st.text_area(
                "Technical Specification (editable)",
                value=st.session_state.e2e_tech_spec,
                height=460,
                key="s4_edit",
            )
            st.session_state.e2e_tech_spec = edited

            dl, regen, _, back, nxt = st.columns([1.6, 1.4, 2, 1, 1])
            with dl:
                st.download_button("⬇️ Download .txt", data=edited,
                                   file_name="technical_spec.txt", mime="text/plain",
                                   use_container_width=True)
            with regen:
                if st.button("🔄 Regenerate", key="s4_regen", use_container_width=True):
                    st.session_state.e2e_tech_spec = ""
                    st.rerun()
            with back:
                if st.button("← Back", key="s4_back", use_container_width=True):
                    st.session_state.e2e_step = 3
                    st.rerun()
            with nxt:
                if st.button("Next →", type="primary", key="s4_next", use_container_width=True):
                    st.session_state.e2e_step = 5
                    st.rerun()

    # ── Step 5: SAP Code Generation ───────────────────────────────────────────
    elif step == 5:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          💻 SAP Code Generation
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          Generate production-ready SAP code from the Technical Specification.
        </p>
        """, unsafe_allow_html=True)

        CODE_OPTIONS = {
            "abap":     ("🔷 ABAP (S/4HANA)",  "text"),
            "ui5":      ("🌐 SAPUI5 / Fiori",   "javascript"),
            "cap_node": ("🟢 CAP Node.js",       "javascript"),
            "cap_java": ("☕ CAP Java",           "java"),
        }
        EXT_MAP = {"abap": "abap", "ui5": "js", "cap_node": "js", "cap_java": "java"}

        code_type = st.selectbox(
            "Select Code Type",
            options=list(CODE_OPTIONS.keys()),
            format_func=lambda x: CODE_OPTIONS[x][0],
            index=list(CODE_OPTIONS.keys()).index(st.session_state.e2e_code_type),
        )
        if code_type != st.session_state.e2e_code_type:
            st.session_state.e2e_code_type = code_type
            st.session_state.e2e_code = ""
            st.rerun()

        if not st.session_state.e2e_code:
            c1, c2 = st.columns([2, 5])
            with c1:
                if st.button(f"⚡ Generate {CODE_OPTIONS[code_type][0]}", type="primary",
                             key="s5_gen", use_container_width=True):
                    from prompts.e2e_templates import (
                        ABAP_CODE_SYSTEM, abap_code_prompt,
                        UI5_CODE_SYSTEM,  ui5_code_prompt,
                        CAP_NODE_SYSTEM,  cap_node_prompt,
                        CAP_JAVA_SYSTEM,  cap_java_prompt,
                    )
                    PROMPT_MAP = {
                        "abap":     (ABAP_CODE_SYSTEM,  abap_code_prompt),
                        "ui5":      (UI5_CODE_SYSTEM,   ui5_code_prompt),
                        "cap_node": (CAP_NODE_SYSTEM,   cap_node_prompt),
                        "cap_java": (CAP_JAVA_SYSTEM,   cap_java_prompt),
                    }
                    sys_p, prompt_fn = PROMPT_MAP[code_type]
                    with st.spinner(f"Generating {CODE_OPTIONS[code_type][0]} code…"):
                        try:
                            result = llm.complete(
                                sys_p,
                                prompt_fn(st.session_state.e2e_tech_spec),
                                max_tokens=4000,
                            )
                            st.session_state.e2e_code = result
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Code generation failed: {exc}")
            with c2:
                if st.button("← Back", key="s5_back_pre"):
                    st.session_state.e2e_step = 4
                    st.rerun()
        else:
            lang = CODE_OPTIONS[code_type][1]
            ext  = EXT_MAP[code_type]
            st.code(st.session_state.e2e_code, language=lang)

            dl, regen, _, back, restart = st.columns([1.6, 1.4, 2, 1, 1.5])
            with dl:
                st.download_button(f"⬇️ Download .{ext}", data=st.session_state.e2e_code,
                                   file_name=f"generated_{code_type}.{ext}", mime="text/plain",
                                   use_container_width=True)
            with regen:
                if st.button("🔄 Regenerate", key="s5_regen", use_container_width=True):
                    st.session_state.e2e_code = ""
                    st.rerun()
            with back:
                if st.button("← Back", key="s5_back", use_container_width=True):
                    st.session_state.e2e_step = 4
                    st.rerun()
            with restart:
                if st.button("🔁 New Session", key="s5_restart", use_container_width=True):
                    for k in ["e2e_step","e2e_brd","e2e_func_spec","e2e_tech_spec","e2e_code","e2e_code_type"]:
                        st.session_state.pop(k, None)
                    st.rerun()

            st.success("✅ Generation complete! Download the file above or start a new session.")

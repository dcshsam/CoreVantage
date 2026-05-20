"""
SAP AI Assistant — End-to-End SAP Solution Generator
5-step wizard: LLM Status → BRD → Functional Spec → Technical Spec → SAP Code
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="SAP AI Assistant — E2E",
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
_DEFAULTS = {
    "step":                 1,
    "business_requirement": "",
    "functional_spec":      "",
    "technical_spec":       "",
    "generated_code":       {},   # {"abap": {"code":..,"label":..}, ...}
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

STEPS = [
    ("🔑", "LLM Configuration"),
    ("📋", "Business Requirements"),
    ("📊", "Functional Specification"),
    ("⚙️", "Technical Specification"),
    ("💻", "SAP Code Generation"),
]

step = st.session_state.step
llm  = st.session_state.get("cv_llm_client")

# ── Layout ────────────────────────────────────────────────────────────────────
nav_col, main_col = st.columns([1.8, 4.2], gap="large")

# ── Left panel ────────────────────────────────────────────────────────────────
with nav_col:
    rows = ""
    for i, (icon, label) in enumerate(STEPS, 1):
        if i < step:
            rows += f"""
            <div style="display:flex;align-items:center;gap:9px;padding:6px 10px;border-radius:6px">
              <span style="font-size:.9rem">✅</span>
              <span style="font-size:.84rem;color:#2E844A;font-weight:600">{label}</span>
            </div>"""
        elif i == step:
            rows += f"""
            <div style="display:flex;align-items:center;gap:9px;padding:6px 10px;
                 border-radius:6px;background:#E8F4FF">
              <span style="font-size:.9rem">▶</span>
              <span style="font-size:.84rem;color:#0176D3;font-weight:700">{icon} {label}</span>
            </div>"""
        else:
            rows += f"""
            <div style="display:flex;align-items:center;gap:9px;padding:6px 10px;border-radius:6px">
              <span style="font-size:.9rem;opacity:.3">{icon}</span>
              <span style="font-size:.84rem;color:#B0B0B0">{label}</span>
            </div>"""

    llm_badge = ""
    if llm:
        display = st.session_state.get("cv_llm_display", "Connected")
        llm_badge = f"""
        <div style="margin-top:12px;padding:8px 10px;background:#EEF6EC;border-radius:6px;
                    border:1px solid #B8DDB0">
          <div style="font-size:.72rem;color:#706E6B;font-weight:600;text-transform:uppercase;
                      letter-spacing:.4px;margin-bottom:2px">Connected LLM</div>
          <div style="font-size:.82rem;color:#2E844A;font-weight:700">🤖 {display}</div>
        </div>"""

    progress_pct = int(step / len(STEPS) * 100)

    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #DDDBDA;border-radius:10px;padding:20px 16px 16px">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">
        <span style="font-size:1.4rem">🏭</span>
        <span style="font-size:1.02rem;font-weight:700;color:#032D60">SAP AI Assistant</span>
      </div>
      <div style="font-size:.76rem;color:#706E6B;font-style:italic;margin-bottom:14px">
        End-to-End SAP Solution Generator
      </div>
      <hr style="border:none;border-top:1px solid #EAEAEA;margin:0 0 6px">
      {rows}
      <hr style="border:none;border-top:1px solid #EAEAEA;margin:6px 0 10px">
      <div style="font-size:.75rem;color:#706E6B;margin-bottom:5px">Step {step} of {len(STEPS)}</div>
      <div style="background:#E8F4FF;border-radius:4px;height:6px;overflow:hidden">
        <div style="background:#0176D3;width:{progress_pct}%;height:100%;border-radius:4px"></div>
      </div>
      {llm_badge}
    </div>
    """, unsafe_allow_html=True)

    if step > 1:
        st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
        if st.button("🔁 Start Over", use_container_width=True, key="nav_reset"):
            for k in _DEFAULTS:
                st.session_state[k] = _DEFAULTS[k]
            st.rerun()

# ── Helper: navigation row ────────────────────────────────────────────────────
def _nav(back_step=None, next_step=None, next_label="Next →",
         next_disabled=False, back_key="back", next_key="next"):
    c1, c2 = st.columns([1, 5])
    with c1:
        if back_step and st.button("← Back", key=back_key, use_container_width=True):
            st.session_state.step = back_step
            st.rerun()
    with c2:
        if next_step and st.button(next_label, type="primary", key=next_key,
                                   disabled=next_disabled):
            st.session_state.step = next_step
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
            st.success(f"✅ **LLM Connected:** {st.session_state.get('cv_llm_display', 'Connected')}")
            st.info("Your LLM is already configured via the CoreShift LLM Setup. Click **Next** to begin.")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Next →", type="primary", key="s1_next"):
                st.session_state.step = 2
                st.rerun()
        else:
            st.warning("⚠️ No LLM connected. Please configure one first via the CoreShift LLM Setup.")
            if st.button("🔑 Go to LLM Setup", type="primary", key="s1_setup"):
                st.switch_page("pages/1_🔑_LLM_Setup.py")

    # ── Step 2: Business Requirements ─────────────────────────────────────────
    elif step == 2:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          📋 Business Requirements
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          Upload a BRD document or enter requirements manually.
          Include process context, SAP module, stakeholders, and expected outcomes.
        </p>
        """, unsafe_allow_html=True)

        tab_upload, tab_manual = st.tabs(["📁 Upload Document", "✏️ Manual Entry"])

        with tab_upload:
            uploaded = st.file_uploader(
                "Upload BRD (PDF, DOCX, TXT)",
                type=["pdf", "docx", "txt"],
                key="brd_upload",
            )
            if uploaded:
                from utils.doc_parser import parse_document
                try:
                    text = parse_document(uploaded)
                    st.session_state.business_requirement = text
                    st.success(f"✅ Parsed **{uploaded.name}** — {len(text):,} characters")
                    with st.expander("Preview (first 3,000 chars)"):
                        st.text(text[:3000])
                except Exception as exc:
                    st.error(f"Failed to parse document: {exc}")

        with tab_manual:
            brd = st.text_area(
                "Business Requirement Document (BRD)",
                value=st.session_state.business_requirement,
                height=360,
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
            if brd != st.session_state.business_requirement:
                st.session_state.business_requirement = brd

        st.markdown("<br>", unsafe_allow_html=True)
        _nav(
            back_step=1, next_step=3,
            next_disabled=not st.session_state.business_requirement.strip(),
            back_key="s2_back", next_key="s2_next",
        )

    # ── Step 3: Functional Specification ──────────────────────────────────────
    elif step == 3:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          📊 Functional Specification
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          AI generates a comprehensive SAP Functional Specification from your business requirements.
          Edit the output before proceeding.
        </p>
        """, unsafe_allow_html=True)

        if not st.session_state.functional_spec:
            c1, c2 = st.columns([2.2, 4])
            with c1:
                if st.button("⚡ Generate Functional Spec", type="primary",
                             key="s3_gen", use_container_width=True):
                    from prompts.e2e_templates import FUNCTIONAL_SPEC_SYSTEM, functional_spec_prompt
                    with st.spinner("Generating Functional Specification — this may take a minute…"):
                        try:
                            st.session_state.functional_spec = llm.complete(
                                FUNCTIONAL_SPEC_SYSTEM,
                                functional_spec_prompt(st.session_state.business_requirement),
                                max_tokens=4096,
                            )
                            st.session_state.technical_spec = ""
                            st.session_state.generated_code = {}
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Generation failed: {exc}")
            with c2:
                if st.button("← Back", key="s3_back_pre"):
                    st.session_state.step = 2
                    st.rerun()
        else:
            edited = st.text_area(
                "Functional Specification (editable)",
                value=st.session_state.functional_spec,
                height=500,
                key="s3_edit",
            )
            st.session_state.functional_spec = edited

            # Export + nav row
            from utils.doc_exporter import export_to_word, export_to_pdf
            word_bytes = export_to_word("SAP Functional Specification", edited)
            pdf_bytes  = export_to_pdf("SAP Functional Specification", edited)

            c_word, c_pdf, c_regen, _, c_back, c_next = st.columns([1.2, 1.2, 1.2, 1.4, 0.9, 0.9])
            with c_word:
                st.download_button("⬇️ Word", data=word_bytes,
                                   file_name="functional_spec.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   use_container_width=True)
            with c_pdf:
                st.download_button("⬇️ PDF", data=pdf_bytes,
                                   file_name="functional_spec.pdf",
                                   mime="application/pdf",
                                   use_container_width=True)
            with c_regen:
                if st.button("🔄 Regenerate", key="s3_regen", use_container_width=True):
                    st.session_state.functional_spec = ""
                    st.rerun()
            with c_back:
                if st.button("← Back", key="s3_back", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
            with c_next:
                if st.button("Next →", type="primary", key="s3_next", use_container_width=True):
                    st.session_state.step = 4
                    st.rerun()

    # ── Step 4: Technical Specification ───────────────────────────────────────
    elif step == 4:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          ⚙️ Technical Specification
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          AI generates an implementation-ready SAP Technical Specification from the Functional Specification.
          Edit the output before proceeding to code generation.
        </p>
        """, unsafe_allow_html=True)

        if not st.session_state.technical_spec:
            c1, c2 = st.columns([2.2, 4])
            with c1:
                if st.button("⚡ Generate Technical Spec", type="primary",
                             key="s4_gen", use_container_width=True):
                    from prompts.e2e_templates import TECHNICAL_SPEC_SYSTEM, technical_spec_prompt
                    with st.spinner("Generating Technical Specification — this may take a minute…"):
                        try:
                            st.session_state.technical_spec = llm.complete(
                                TECHNICAL_SPEC_SYSTEM,
                                technical_spec_prompt(st.session_state.functional_spec),
                                max_tokens=4096,
                            )
                            st.session_state.generated_code = {}
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Generation failed: {exc}")
            with c2:
                if st.button("← Back", key="s4_back_pre"):
                    st.session_state.step = 3
                    st.rerun()
        else:
            edited = st.text_area(
                "Technical Specification (editable)",
                value=st.session_state.technical_spec,
                height=500,
                key="s4_edit",
            )
            st.session_state.technical_spec = edited

            from utils.doc_exporter import export_to_word, export_to_pdf
            word_bytes = export_to_word("SAP Technical Specification", edited)
            pdf_bytes  = export_to_pdf("SAP Technical Specification", edited)

            c_word, c_pdf, c_regen, _, c_back, c_next = st.columns([1.2, 1.2, 1.2, 1.4, 0.9, 0.9])
            with c_word:
                st.download_button("⬇️ Word", data=word_bytes,
                                   file_name="technical_spec.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   use_container_width=True)
            with c_pdf:
                st.download_button("⬇️ PDF", data=pdf_bytes,
                                   file_name="technical_spec.pdf",
                                   mime="application/pdf",
                                   use_container_width=True)
            with c_regen:
                if st.button("🔄 Regenerate", key="s4_regen", use_container_width=True):
                    st.session_state.technical_spec = ""
                    st.rerun()
            with c_back:
                if st.button("← Back", key="s4_back", use_container_width=True):
                    st.session_state.step = 3
                    st.rerun()
            with c_next:
                if st.button("Next →", type="primary", key="s4_next", use_container_width=True):
                    st.session_state.step = 5
                    st.rerun()

    # ── Step 5: SAP Code Generation ───────────────────────────────────────────
    elif step == 5:
        st.markdown("""
        <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
          💻 SAP Code Generation
        </h2>
        <p style="color:#706E6B;font-size:.9rem;margin-bottom:16px">
          Generate production-ready SAP code from the Technical Specification.
          You can generate multiple code types in one session.
        </p>
        """, unsafe_allow_html=True)

        CODE_TYPES = {
            "abap":     ("🔷 ABAP — Classic SAP Development",          "text"),
            "ui5":      ("🌐 SAPUI5 / Fiori — Frontend Application",    "javascript"),
            "cap_node": ("🟢 CAP Node.js — Cloud Application Programming", "javascript"),
            "cap_java": ("☕ CAP Java — Cloud Application Programming",  "java"),
        }
        EXT = {"abap": "abap", "ui5": "js", "cap_node": "js", "cap_java": "java"}

        sel = st.selectbox(
            "Select Code Type to Generate",
            options=list(CODE_TYPES.keys()),
            format_func=lambda x: CODE_TYPES[x][0],
        )

        c1, c2 = st.columns([2.2, 4])
        with c1:
            already_done = sel in st.session_state.generated_code
            btn_label = f"🔄 Regenerate {CODE_TYPES[sel][0]}" if already_done else f"⚡ Generate {CODE_TYPES[sel][0]}"
            if st.button(btn_label, type="primary", key="s5_gen", use_container_width=True):
                from prompts.e2e_templates import (
                    ABAP_CODE_SYSTEM,  abap_code_prompt,
                    UI5_CODE_SYSTEM,   ui5_code_prompt,
                    CAP_NODE_SYSTEM,   cap_node_prompt,
                    CAP_JAVA_SYSTEM,   cap_java_prompt,
                )
                PROMPT_MAP = {
                    "abap":     (ABAP_CODE_SYSTEM,  abap_code_prompt),
                    "ui5":      (UI5_CODE_SYSTEM,   ui5_code_prompt),
                    "cap_node": (CAP_NODE_SYSTEM,   cap_node_prompt),
                    "cap_java": (CAP_JAVA_SYSTEM,   cap_java_prompt),
                }
                sys_p, prompt_fn = PROMPT_MAP[sel]
                with st.spinner(f"Generating {CODE_TYPES[sel][0]}…"):
                    try:
                        code = llm.complete(sys_p, prompt_fn(st.session_state.technical_spec),
                                            max_tokens=4096)
                        st.session_state.generated_code[sel] = {
                            "code":  code,
                            "label": CODE_TYPES[sel][0],
                        }
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Code generation failed: {exc}")
        with c2:
            if st.button("← Back", key="s5_back_pre"):
                st.session_state.step = 4
                st.rerun()

        # ── Show all generated artifacts ──────────────────────────────────────
        if st.session_state.generated_code:
            st.markdown("---")

            for code_key, artifact in list(st.session_state.generated_code.items()):
                lang = CODE_TYPES[code_key][1]
                ext  = EXT[code_key]
                with st.expander(f"**{artifact['label']}**", expanded=(code_key == sel)):
                    st.code(artifact["code"], language=lang)
                    da, db, dc = st.columns([1.5, 1.5, 3])
                    with da:
                        st.download_button(
                            f"⬇️ Download .{ext}",
                            data=artifact["code"],
                            file_name=f"generated_{code_key}.{ext}",
                            mime="text/plain",
                            use_container_width=True,
                            key=f"dl_{code_key}",
                        )
                    with db:
                        if st.button("🗑️ Remove", key=f"del_{code_key}", use_container_width=True):
                            del st.session_state.generated_code[code_key]
                            st.rerun()

            # ZIP download of everything
            st.markdown("<br>", unsafe_allow_html=True)
            from utils.zip_packager import package_code_as_zip
            zip_bytes = package_code_as_zip(
                st.session_state.generated_code,
                functional_spec=st.session_state.functional_spec,
                technical_spec=st.session_state.technical_spec,
            )
            za, zb, _, zc = st.columns([2, 2, 2, 1.5])
            with za:
                st.download_button(
                    "📦 Download All as ZIP",
                    data=zip_bytes,
                    file_name="sap_solution_package.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key="dl_zip",
                )
            with zb:
                st.info(f"📁 {len(st.session_state.generated_code)} artifact(s) generated")
            with zc:
                if st.button("🔁 New Session", key="s5_restart", use_container_width=True):
                    for k in _DEFAULTS:
                        st.session_state[k] = _DEFAULTS[k]
                    st.rerun()

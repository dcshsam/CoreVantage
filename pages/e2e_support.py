"""
SAP AI Assistant — End-to-End SAP Solution Generator
4-step wizard: BRD → Functional Spec → Technical Spec → SAP Code
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
from core.ui import inject_css

inject_css()
user = require_auth()

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

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
    ("📋", "Business Requirements"),
    ("📊", "Functional Specification"),
    ("⚙️", "Technical Specification"),
    ("💻", "SAP Code Generation"),
]

step = st.session_state.step
llm  = st.session_state.get("cv_llm_client")

# Redirect to LLM setup if not connected — no step needed for this
if not llm:
    st.warning("⚠️ No LLM connected. Please configure one first.")
    if st.button("🔑 Go to LLM Setup", type="primary"):
        st.switch_page("pages/1_🔑_LLM_Setup.py")
    st.stop()

# ── Sidebar nav panel ─────────────────────────────────────────────────────────
with st.sidebar:
    # ── Brand block ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:22px 18px 18px;border-bottom:1px solid rgba(255,255,255,0.09)">
      <div style="display:flex;align-items:center;gap:11px">
        <div style="background:#0176D3;border-radius:10px;width:38px;height:38px;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;
                    box-shadow:0 2px 8px rgba(1,118,211,0.40)">
          <span style="font-size:1.2rem">🏭</span>
        </div>
        <div>
          <div style="font-size:1.05rem;font-weight:700;color:#FFFFFF;letter-spacing:-0.3px;line-height:1.15">
            SAP AI Assistant
          </div>
          <div style="font-size:0.67rem;color:#6FA8D4;letter-spacing:0.4px;text-transform:uppercase;margin-top:1px">
            E2E SAP Solution Generator
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Steps section label ───────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:14px 18px 4px">
      <div style="font-size:0.67rem;color:#6FA8D4;font-weight:700;
                  text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px">
        Workflow Steps
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Step rows ─────────────────────────────────────────────────────────────
    rows = ""
    for i, (icon, label) in enumerate(STEPS, 1):
        if i < step:
            rows += (
                f'<div style="display:flex;align-items:center;gap:9px;padding:7px 18px;'
                f'border-radius:0;margin:1px 0">'
                f'<span style="color:#4CAF50;font-size:.85rem">✅</span>'
                f'<span style="font-size:.84rem;color:#A8D5A2;font-weight:600">{label}</span>'
                f'</div>'
            )
        elif i == step:
            rows += (
                f'<div style="display:flex;align-items:center;gap:9px;padding:7px 12px 7px 14px;'
                f'margin:1px 6px;border-radius:6px;background:#0176D3">'
                f'<span style="color:#FFFFFF;font-size:.85rem">▶</span>'
                f'<span style="font-size:.84rem;color:#FFFFFF;font-weight:700">{icon} {label}</span>'
                f'</div>'
            )
        else:
            rows += (
                f'<div style="display:flex;align-items:center;gap:9px;padding:7px 18px;'
                f'border-radius:0;margin:1px 0;opacity:.5">'
                f'<span style="font-size:.85rem">{icon}</span>'
                f'<span style="font-size:.84rem;color:#C9D9EF">{label}</span>'
                f'</div>'
            )

    progress_pct = int(step / len(STEPS) * 100)

    st.markdown(
        f'<div style="padding:0 0 8px">{rows}</div>'
        f'<div style="padding:4px 18px 12px">'
        f'<div style="font-size:.72rem;color:#6FA8D4;margin-bottom:5px">Step {step} of {len(STEPS)}</div>'
        f'<div style="background:rgba(255,255,255,0.12);border-radius:4px;height:5px;overflow:hidden">'
        f'<div style="background:#0176D3;width:{progress_pct}%;height:100%;border-radius:4px"></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── LLM status ────────────────────────────────────────────────────────────
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.09);margin:4px 0">', unsafe_allow_html=True)
    if llm:
        display = st.session_state.get("cv_llm_display", "Connected")
        st.markdown(
            f'<div style="padding:10px 18px">'
            f'<div style="font-size:.67rem;color:#6FA8D4;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:.6px;margin-bottom:4px">Connected LLM</div>'
            f'<div style="font-size:.82rem;color:#FFFFFF;font-weight:600">🤖 {display}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="padding:10px 18px">'
            '<div style="font-size:.72rem;color:#F5A623;font-weight:600">⚠️ No LLM connected</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Start Over button ─────────────────────────────────────────────────────
    if step > 1:
        st.markdown('<div style="padding:4px 8px 8px">', unsafe_allow_html=True)
        if st.button("🔁 Start Over", use_container_width=True, key="nav_reset"):
            for k in _DEFAULTS:
                st.session_state[k] = _DEFAULTS[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="text-align:center;padding:8px 0 10px;margin-top:auto">'
        '<span style="font-size:0.67rem;color:#3D6E96">v1.1.0 &nbsp;·&nbsp; Powered by SPRAC &nbsp;·&nbsp; 2025</span>'
        '</div>',
        unsafe_allow_html=True,
    )

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
if True:

    # ── Step 1: Business Requirements ─────────────────────────────────────────
    if step == 1:
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
            back_step=None, next_step=2,
            next_disabled=not st.session_state.business_requirement.strip(),
            back_key="s1_back", next_key="s1_next",
        )

    # ── Step 2: Functional Specification ──────────────────────────────────────
    elif step == 2:
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
                if st.button("← Back", key="s2_back_pre"):
                    st.session_state.step = 1
                    st.rerun()
        else:
            edited = st.text_area(
                "Functional Specification (editable)",
                value=st.session_state.functional_spec,
                height=500,
                key="s2_edit",
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
                if st.button("🔄 Regenerate", key="s2_regen", use_container_width=True):
                    st.session_state.functional_spec = ""
                    st.rerun()
            with c_back:
                if st.button("← Back", key="s2_back", use_container_width=True):
                    st.session_state.step = 1
                    st.rerun()
            with c_next:
                if st.button("Next →", type="primary", key="s2_next", use_container_width=True):
                    st.session_state.step = 3
                    st.rerun()

    # ── Step 3: Technical Specification ───────────────────────────────────────
    elif step == 3:
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
                if st.button("← Back", key="s3_back_pre"):
                    st.session_state.step = 2
                    st.rerun()
        else:
            edited = st.text_area(
                "Technical Specification (editable)",
                value=st.session_state.technical_spec,
                height=500,
                key="s3_edit",
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
                if st.button("🔄 Regenerate", key="s3_regen", use_container_width=True):
                    st.session_state.technical_spec = ""
                    st.rerun()
            with c_back:
                if st.button("← Back", key="s3_back", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
            with c_next:
                if st.button("Next →", type="primary", key="s3_next", use_container_width=True):
                    st.session_state.step = 4
                    st.rerun()

    # ── Step 4: SAP Code Generation ───────────────────────────────────────────
    elif step == 4:
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
            if st.button("← Back", key="s4_back_pre"):
                st.session_state.step = 3
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

"""
CoreVantage — E2E Support
End-to-end SAP solution generator: BRD → Functional Spec → Technical Spec → Code.
Ported from dcshsam/SAP_MAIN; uses CoreVantage auth + LLM session state.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="E2E Support — CoreVantage",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.auth import require_auth
from core.ui import inject_css

inject_css()
user = require_auth()

# ── E2E dark theme CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
.sap-header {
    background: rgba(10,132,255,0.15);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 20px 24px; border-radius: 16px;
    border: 1px solid rgba(10,132,255,0.3);
    color: white; margin-bottom: 24px;
}
.sap-header h2 { margin: 0 0 4px 0; font-size: 1.4rem; color: #FFFFFF; }
.sap-header p  { margin: 0; color: rgba(255,255,255,0.6); font-size: .92rem; }

.sap-sub-header {
    background: rgba(28,28,30,0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 14px 20px; border-radius: 12px;
    border: 1px solid rgba(10,132,255,0.25);
    color: white; margin: 18px 0 16px 0;
}
.sap-sub-header h3 { margin: 0 0 2px 0; font-size: 1.1rem; color: #FFFFFF; }
.sap-sub-header p  { margin: 0; color: rgba(255,255,255,0.55); font-size: .82rem; }

.llm-badge {
    display: inline-block;
    background: rgba(10,132,255,0.2);
    color: #0A84FF;
    padding: 3px 14px; border-radius: 100px;
    font-size: .82rem; font-weight: 600;
    border: 1px solid rgba(10,132,255,0.35);
}
.step-done   { color: #30D158; font-weight: 600; }
.step-active { color: #0A84FF; font-weight: 700; }
.step-todo   { color: rgba(255,255,255,0.3); }

.cred-table { width: 100%; border-collapse: collapse; margin: 12px 0; border-radius: 12px; overflow: hidden; }
.cred-table th { background: rgba(10,132,255,0.25); color: white; padding: 10px 12px; text-align: left; font-size: .85rem; }
.cred-table td { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.08); font-size: .85rem; color: rgba(255,255,255,0.8); }
.cred-table tr:nth-child(even) { background: rgba(255,255,255,0.03); }
.stTextArea textarea { font-family: 'Courier New', Courier, monospace; font-size: .88rem; }
</style>
""", unsafe_allow_html=True)

# ── E2E wizard session state (prefixed e2e_ to avoid conflicts) ───────────────
_DEFAULTS = {
    "e2e_step"              : 1,
    "e2e_business_req"      : "",
    "e2e_functional_spec"   : "",
    "e2e_technical_spec"    : "",
    "e2e_generated_code"    : {},
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Helpers ───────────────────────────────────────────────────────────────────
def _llm():
    """Return CoreVantage's connected LLM client."""
    return st.session_state.get("cv_llm_client")

def _llm_name():
    return st.session_state.get("cv_llm_display", "LLM Connected")

def sap_header(title, subtitle):
    st.markdown(
        f'<div class="sap-header"><h2>{title}</h2><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )

# ── E2E-only sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:8px 0 12px">
      <div style="background:rgba(48,209,88,0.2);border-radius:10px;width:36px;height:36px;flex-shrink:0;
                  display:flex;align-items:center;justify-content:center;font-size:1.1rem;
                  border:1px solid rgba(48,209,88,0.35)">🔄</div>
      <div>
        <div style="font-size:1rem;font-weight:700;color:#FFFFFF">E2E Support</div>
        <div style="font-size:.65rem;color:rgba(255,255,255,0.4);font-weight:600;text-transform:uppercase;
                    letter-spacing:.5px">End to End SAP</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:.7rem;color:rgba(255,255,255,0.4);font-weight:600;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px">E2E Workflow</div>', unsafe_allow_html=True)

    steps = [
        (1, "📋 Business Requirements"),
        (2, "📊 Functional Specification"),
        (3, "⚙️ Technical Specification"),
        (4, "💻 SAP Code Generation"),
    ]
    cur = st.session_state.e2e_step
    for num, label in steps:
        if num == cur:
            st.markdown(f'<span class="step-active">▶ {label}</span>', unsafe_allow_html=True)
        elif num < cur:
            if st.button(f"✅ {label}", key=f"e2e_nav_{num}", use_container_width=True):
                st.session_state.e2e_step = num
                st.rerun()
        else:
            st.markdown(f'<span class="step-todo">　{label}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress((cur - 1) / 3, text=f"Step {cur} of 4")
    st.markdown(f'<span class="llm-badge">🤖 {_llm_name()}</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.page_link("app.py", label="← Back to Home", icon="🏠")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
  <div style="background:rgba(48,209,88,0.2);border-radius:12px;width:44px;height:44px;flex-shrink:0;
              display:flex;align-items:center;justify-content:center;font-size:1.4rem;
              border:1px solid rgba(48,209,88,0.35)">🔄</div>
  <div>
    <div style="font-size:1.2rem;font-weight:700;color:#FFFFFF">E2E Support</div>
    <div style="font-size:.72rem;color:#30D158;font-weight:600;text-transform:uppercase;
                letter-spacing:.5px">End to End SAP Support</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STEP 1 — Business Requirements ───────────────────────────────────────────
def screen_requirements():
    sap_header(
        "📋 Step 1 — Business Requirements",
        "Upload a BRD document or describe the SAP requirements manually",
    )

    tab_upload, tab_manual = st.tabs(["📁 Upload Document", "✏️ Manual Entry"])

    with tab_upload:
        uploaded = st.file_uploader(
            "Upload Business Requirement Document",
            type=["pdf", "docx", "txt"],
            help="Supported: PDF, Word (.docx), Plain Text (.txt)",
        )
        if uploaded:
            with st.spinner(f"Parsing {uploaded.name}…"):
                try:
                    from utils.doc_parser import parse_document
                    text = parse_document(uploaded)
                    st.session_state.e2e_business_req = text
                    st.success(f"✅ Parsed **{uploaded.name}** — {len(text):,} characters extracted.")
                    with st.expander("Preview extracted text (first 3 000 chars)"):
                        st.text(text[:3000] + ("…" if len(text) > 3000 else ""))
                except Exception as exc:
                    st.error(f"Document parsing failed: {exc}")

    with tab_manual:
        manual_text = st.text_area(
            "Describe your SAP Business Requirements",
            value=st.session_state.e2e_business_req,
            height=420,
            placeholder=(
                "Example:\n\n"
                "We need to implement a Purchase Order approval workflow in SAP MM.\n"
                "Requirements:\n"
                "1. Requestors create purchase requisitions in ME51N\n"
                "2. Approval routing by value: >$1,000 → Manager, >$10,000 → Director\n"
                "3. Email notifications at each approval stage\n"
                "4. Budget availability check via SAP FI before approval\n"
                "5. Weekly summary report of all open POs\n"
            ),
        )
        if manual_text != st.session_state.e2e_business_req:
            st.session_state.e2e_business_req = manual_text

    if st.session_state.e2e_business_req:
        st.success(f"✅ Requirements captured — {len(st.session_state.e2e_business_req):,} characters.")

    st.markdown("---")
    if st.button("Generate Functional Specification →", type="primary"):
        if not st.session_state.e2e_business_req.strip():
            st.error("Please upload a document or enter requirements before proceeding.")
        else:
            st.session_state.e2e_functional_spec = ""
            st.session_state.e2e_step = 2
            st.rerun()


# ── STEP 2 — Functional Specification ────────────────────────────────────────
def screen_functional_spec():
    sap_header(
        "📊 Step 2 — Functional Specification",
        "AI-generated SAP Functional Specification — review, edit, and export",
    )

    if not st.session_state.e2e_functional_spec:
        with st.spinner("🤖 Generating Functional Specification… (30–60 seconds)"):
            try:
                from prompts.e2e_templates import FUNCTIONAL_SPEC_SYSTEM, functional_spec_prompt
                fs = _llm().complete(
                    FUNCTIONAL_SPEC_SYSTEM,
                    functional_spec_prompt(st.session_state.e2e_business_req),
                    max_tokens=4096,
                )
                st.session_state.e2e_functional_spec = fs
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
                return

    col_title, col_regen = st.columns([5, 1])
    with col_title:
        st.markdown("#### Functional Specification Document")
    with col_regen:
        if st.button("🔄 Regenerate"):
            st.session_state.e2e_functional_spec = ""
            st.rerun()

    edited = st.text_area(
        "Review and edit — changes are saved in this session:",
        value=st.session_state.e2e_functional_spec,
        height=520,
        key="e2e_fs_editor",
    )
    st.session_state.e2e_functional_spec = edited

    st.markdown("---")
    st.markdown("#### Export Functional Specification")
    col_w, col_p, _ = st.columns([1, 1, 4])
    with col_w:
        try:
            from utils.doc_exporter import export_to_word
            st.download_button(
                "📄 Download Word",
                data=export_to_word("Functional Specification", edited),
                file_name="SAP_Functional_Specification.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as exc:
            st.error(f"Word export error: {exc}")
    with col_p:
        try:
            from utils.doc_exporter import export_to_pdf
            st.download_button(
                "📋 Download PDF",
                data=export_to_pdf("Functional Specification", edited),
                file_name="SAP_Functional_Specification.pdf",
                mime="application/pdf",
            )
        except Exception as exc:
            st.error(f"PDF export error: {exc}")

    st.markdown("---")
    col_back, col_next = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            st.session_state.e2e_step = 1
            st.rerun()
    with col_next:
        if st.button("Generate Technical Specification →", type="primary"):
            st.session_state.e2e_technical_spec = ""
            st.session_state.e2e_step = 3
            st.rerun()


# ── STEP 3 — Technical Specification ─────────────────────────────────────────
def screen_technical_spec():
    sap_header(
        "⚙️ Step 3 — Technical Specification",
        "AI-generated SAP Technical Specification derived from the Functional Specification",
    )

    if not st.session_state.e2e_technical_spec:
        with st.spinner("🤖 Generating Technical Specification… (30–60 seconds)"):
            try:
                from prompts.e2e_templates import TECHNICAL_SPEC_SYSTEM, technical_spec_prompt
                ts = _llm().complete(
                    TECHNICAL_SPEC_SYSTEM,
                    technical_spec_prompt(st.session_state.e2e_functional_spec),
                    max_tokens=4096,
                )
                st.session_state.e2e_technical_spec = ts
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
                return

    col_title, col_regen = st.columns([5, 1])
    with col_title:
        st.markdown("#### Technical Specification Document")
    with col_regen:
        if st.button("🔄 Regenerate"):
            st.session_state.e2e_technical_spec = ""
            st.rerun()

    edited = st.text_area(
        "Review and edit — changes are saved in this session:",
        value=st.session_state.e2e_technical_spec,
        height=520,
        key="e2e_ts_editor",
    )
    st.session_state.e2e_technical_spec = edited

    st.markdown("---")
    st.markdown("#### Export Technical Specification")
    col_w, col_p, _ = st.columns([1, 1, 4])
    with col_w:
        try:
            from utils.doc_exporter import export_to_word
            st.download_button(
                "📄 Download Word",
                data=export_to_word("Technical Specification", edited),
                file_name="SAP_Technical_Specification.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as exc:
            st.error(f"Word export error: {exc}")
    with col_p:
        try:
            from utils.doc_exporter import export_to_pdf
            st.download_button(
                "📋 Download PDF",
                data=export_to_pdf("Technical Specification", edited),
                file_name="SAP_Technical_Specification.pdf",
                mime="application/pdf",
            )
        except Exception as exc:
            st.error(f"PDF export error: {exc}")

    st.markdown("---")
    col_back, col_next = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            st.session_state.e2e_step = 2
            st.rerun()
    with col_next:
        if st.button("Proceed to SAP Code Generation →", type="primary"):
            st.session_state.e2e_step = 4
            st.rerun()


# ── STEP 4 — SAP Code Generation ─────────────────────────────────────────────
def screen_code_generation():
    sap_header(
        "💻 Step 4 — SAP Code Generation",
        "Generate production-ready SAP code and download as a ZIP package",
    )

    _CODE_TYPES = {
        "ABAP — Classic SAP Development"            : "abap",
        "SAPUI5 / Fiori — Frontend Application"     : "ui5",
        "CAP Node.js — Cloud Application Programming": "cap_node",
        "CAP Java — Cloud Application Programming"  : "cap_java",
    }

    col_sel, col_gen = st.columns([3, 1])
    with col_sel:
        code_label = st.selectbox("Select SAP Code Type", list(_CODE_TYPES.keys()))
    with col_gen:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_clicked = st.button("🚀 Generate Code", type="primary", use_container_width=True)

    if generate_clicked:
        key = _CODE_TYPES[code_label]
        with st.spinner(f"🤖 Generating {code_label} code… (up to 90 seconds)"):
            try:
                from prompts.e2e_templates import (
                    ABAP_CODE_SYSTEM, abap_code_prompt,
                    UI5_CODE_SYSTEM,  ui5_code_prompt,
                    CAP_NODE_SYSTEM,  cap_node_prompt,
                    CAP_JAVA_SYSTEM,  cap_java_prompt,
                )
                systems = {
                    "abap"    : (ABAP_CODE_SYSTEM, abap_code_prompt),
                    "ui5"     : (UI5_CODE_SYSTEM,  ui5_code_prompt),
                    "cap_node": (CAP_NODE_SYSTEM,  cap_node_prompt),
                    "cap_java": (CAP_JAVA_SYSTEM,  cap_java_prompt),
                }
                sys_prompt, user_fn = systems[key]
                code = _llm().complete(
                    sys_prompt,
                    user_fn(st.session_state.e2e_technical_spec),
                    max_tokens=4096,
                )
                st.session_state.e2e_generated_code[key] = {"code": code, "label": code_label, "type": code_label}
                st.success(f"✅ {code_label} generated successfully!")
            except Exception as exc:
                st.error(f"Code generation failed: {exc}")

    if st.session_state.e2e_generated_code:
        st.markdown("---")
        st.markdown("### Generated Code Artifacts")

        for key, data in list(st.session_state.e2e_generated_code.items()):
            with st.expander(f"📝 {data['label']}", expanded=True):
                col_code, col_del = st.columns([10, 1])
                with col_del:
                    if st.button("🗑️", key=f"e2e_del_{key}", help="Remove this artifact"):
                        del st.session_state.e2e_generated_code[key]
                        st.rerun()
                edited_code = st.text_area(
                    "Review / edit the generated code:",
                    value=data["code"],
                    height=450,
                    key=f"e2e_code_editor_{key}",
                )
                st.session_state.e2e_generated_code[key]["code"] = edited_code

        st.markdown("---")
        st.markdown("### 📦 Download All Generated Code")
        st.info(
            "The ZIP package contains all generated code files plus the Functional and Technical "
            "Specifications as text documents, and a README with deployment instructions."
        )
        try:
            from utils.zip_packager import package_code_as_zip
            zip_bytes = package_code_as_zip(
                st.session_state.e2e_generated_code,
                functional_spec=st.session_state.e2e_functional_spec,
                technical_spec=st.session_state.e2e_technical_spec,
            )
            st.download_button(
                "⬇️ Download ZIP Package",
                data=zip_bytes,
                file_name="SAP_AI_Generated_Solution.zip",
                mime="application/zip",
            )
        except Exception as exc:
            st.error(f"ZIP packaging failed: {exc}")
    else:
        st.info("Select a code type above and click **🚀 Generate Code** to begin.")

    st.markdown("---")
    col_back, col_restart, _ = st.columns([1, 2, 4])
    with col_back:
        if st.button("← Back"):
            st.session_state.e2e_step = 3
            st.rerun()
    with col_restart:
        if st.button("🔄 Start New Project"):
            for k in ("e2e_business_req", "e2e_functional_spec", "e2e_technical_spec"):
                st.session_state[k] = ""
            st.session_state.e2e_generated_code = {}
            st.session_state.e2e_step = 1
            st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
step = st.session_state.e2e_step
if step == 1:
    screen_requirements()
elif step == 2:
    screen_functional_spec()
elif step == 3:
    screen_technical_spec()
elif step == 4:
    screen_code_generation()

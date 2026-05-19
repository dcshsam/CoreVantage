"""
CoreShift — Clean Core Analysis & Auto-Remediation Page
Three input modes: paste code | SAP system connect | upload file
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.auth import require_auth, increment_analyses
from core.ui import (inject_css, page_header, sidebar_nav, metric_row,
                     severity_badge, cc_level_badge, violation_card, score_ring)
from core.abap_rules import SEVERITY_COLORS, LEVEL_META, ALL_RULES

st.set_page_config(page_title="Clean Core — CoreShift", page_icon="🧹", layout="wide")
inject_css()
user = require_auth()
sidebar_nav(user)

page_header(
    "🧹 Clean Core Analysis & Remediation",
    "Analyse ABAP code against SAP Clean Core standards and auto-remediate to Level A/B",
    badge="Powered by SAP AI Core",
)

llm_client = st.session_state.get("cv_llm_client")
if not llm_client:
    st.warning("⚠️ No LLM connected. Rule-based analysis will run. For AI insights + remediation, [configure LLM first](1_🔑_LLM_Setup).")

# ── Input mode tabs ───────────────────────────────────────────────────────────
st.markdown("#### Step 1 — Input ABAP Code")
tab_paste, tab_system, tab_upload = st.tabs([
    "📋 Paste / Type Code",
    "🔗 Connect SAP System",
    "📁 Upload File",
])

code_input = ""

_CC_SAMPLE = """\
REPORT zorder_processor.

DATA: lt_orders TYPE TABLE OF vbak,
      ls_order  TYPE vbak,
      lt_items  TYPE TABLE OF vbap,
      ls_item   TYPE vbap.

FORM process_orders USING iv_customer TYPE kunnr.
  " Direct table access — no API usage (CC-001)
  SELECT * FROM vbak INTO TABLE lt_orders
    WHERE kunnr = iv_customer.

  LOOP AT lt_orders INTO ls_order.
    " N+1 problem — SELECT inside LOOP (CC-005)
    SELECT * FROM vbap INTO TABLE lt_items
      WHERE vbeln = ls_order-vbeln.

    LOOP AT lt_items INTO ls_item.
      " Classic string concatenation (CC-011)
      DATA: lv_msg TYPE string.
      CONCATENATE 'Order:' ls_order-vbeln ' Item:' ls_item-posnr INTO lv_msg.

      " Message instead of exception (CC-007)
      IF ls_item-netwr < 0.
        MESSAGE e001(zorders) WITH ls_item-posnr.
      ENDIF.
    ENDLOOP.
  ENDLOOP.

  " COMMIT without BAPI pattern
  COMMIT WORK.
ENDFORM.

" Classic BDC instead of BAPI (S4-002)
FORM create_order_bdc.
  DATA: lt_bdc TYPE TABLE OF bdcdata.
  PERFORM bdc_dynpro USING 'SAPMV45A' '0101'.
  PERFORM bdc_field  USING 'BDC_OKCODE' '/00'.
  CALL TRANSACTION 'VA01' USING lt_bdc MODE 'N'.
ENDFORM.

" Hardcoded client (CC-003)
FORM read_company_data.
  SELECT * FROM t001 CLIENT SPECIFIED
    WHERE mandt = '100'.
ENDFORM.
"""

with tab_paste:
    st.markdown('<div class="cv-card"><h3>Paste ABAP Source Code</h3></div>', unsafe_allow_html=True)
    sample = st.checkbox("Load sample code with violations", value=False)
    if sample:
        # Write directly into the widget's session state key BEFORE the widget renders
        st.session_state["paste_area"]    = _CC_SAMPLE
        st.session_state["cv_code_input"] = _CC_SAMPLE
    elif st.session_state.get("paste_area") == _CC_SAMPLE:
        # User unchecked — clear the sample so the textarea goes back to blank
        st.session_state.pop("paste_area", None)
        st.session_state.pop("cv_code_input", None)

    code_input = st.text_area(
        "ABAP Code",
        value=st.session_state.get("cv_code_input", ""),
        height=380,
        placeholder="Paste your ABAP program, function module, or class here…",
        key="paste_area",
    )
    if code_input:
        st.session_state["cv_code_input"] = code_input

with tab_system:
    st.markdown("""
    <div class="cv-card">
      <h3>Connect to SAP ECC / S/4HANA System</h3>
      <p style="color:#706E6B;font-size:.9rem">
        Connect via SAP ADT REST API. Fetches ABAP source directly from your system.
        Requires SAP ADT (ABAP Development Tools) services activated on the backend.
      </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("sap_connect_form"):
        c1, c2, c3 = st.columns(3)
        sap_host    = c1.text_input("Host",     value=st.session_state.get("sap_host", ""),    placeholder="sap-host.example.com")
        sap_client  = c2.text_input("Client",   value=st.session_state.get("sap_client", "100"))
        sap_sysnr   = c3.text_input("Sys Nr",   value=st.session_state.get("sap_sysnr", "00"))
        c4, c5 = st.columns(2)
        sap_user    = c4.text_input("User",     value=st.session_state.get("sap_user", ""))
        sap_pass    = c5.text_input("Password", type="password")
        prog_name   = st.text_input("Program / Object Name", placeholder="ZORDER_PROCESSOR")
        col_test, col_fetch = st.columns(2)
        test_conn  = col_test.form_submit_button("🔌 Test Connection")
        fetch_code = col_fetch.form_submit_button("⬇️ Fetch Source", type="primary")

    if test_conn and sap_host:
        from core.sap_connector import SAPConnector
        conn = SAPConnector(sap_host, sap_client, sap_user, sap_pass, sap_sysnr)
        ok, msg = conn.ping()
        if ok:
            st.success(f"✅ {msg}")
            for k, v in [("sap_host", sap_host), ("sap_client", sap_client),
                          ("sap_sysnr", sap_sysnr), ("sap_user", sap_user)]:
                st.session_state[k] = v
        else:
            st.error(f"Connection failed: {msg}")

    if fetch_code and sap_host and prog_name:
        from core.sap_connector import SAPConnector
        with st.spinner(f"Fetching {prog_name} from {sap_host}…"):
            conn = SAPConnector(sap_host, sap_client, sap_user, sap_pass, sap_sysnr)
            src  = conn.get_program_source(prog_name)
        if src:
            code_input = src
            st.session_state["cv_code_input"] = src
            st.success(f"✅ Fetched {len(src):,} characters from {prog_name}")
            st.code(src[:500] + "…" if len(src) > 500 else src, language="abap")
        else:
            st.error("Could not fetch source. Ensure ADT services are active and user has S_DEVELOP authorization.")

with tab_upload:
    st.markdown('<div class="cv-card"><h3>Upload ABAP Source File</h3></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload .abap, .txt, or .prog file",
                                 type=["abap", "txt", "prog", "fugr", "clas"])
    if uploaded:
        code_input = uploaded.read().decode("utf-8", errors="replace")
        st.session_state["cv_code_input"] = code_input
        st.success(f"✅ Loaded **{uploaded.name}** — {len(code_input):,} characters")
        with st.expander("Preview (first 60 lines)"):
            st.code("\n".join(code_input.splitlines()[:60]), language="abap")

# Use persisted code if nothing new entered
if not code_input:
    code_input = st.session_state.get("cv_code_input", "")

# ── Program name ──────────────────────────────────────────────────────────────
prog_name_input = st.text_input(
    "Program / Object Name (for report)",
    value=st.session_state.get("cv_prog_name", "ZANALYSIS"),
    placeholder="ZORDER_PROCESSOR",
)
st.session_state["cv_prog_name"] = prog_name_input

# ── Analysis options ──────────────────────────────────────────────────────────
with st.expander("⚙️ Analysis Options", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        run_llm        = col1.checkbox("AI deep analysis (requires LLM)", value=True and bool(llm_client))
        run_clean_core = col1.checkbox("Clean Core rules", value=True)
    with col2:
        run_security   = col2.checkbox("Security scan", value=True)
        run_performance= col2.checkbox("Performance scan", value=True)

# ── Run analysis ──────────────────────────────────────────────────────────────
st.markdown("---")
col_run, col_clear = st.columns([3, 1])
with col_run:
    run_btn = st.button("🔍 Run Clean Core Analysis", type="primary",
                         use_container_width=True,
                         disabled=not bool(code_input.strip()))
with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):
        for k in ["cv_code_input", "cv_cc_result"]:
            st.session_state.pop(k, None)
        st.rerun()

if run_btn and code_input.strip():
    categories = []
    if run_clean_core: categories += ["CLEAN_CORE"]
    if run_security:   categories += ["SECURITY"]
    if run_performance:categories += ["PERFORMANCE"]
    if not categories: categories = None

    with st.spinner("🔍 Running rule-based scan…"):
        from core import clean_code_engine
        result = clean_code_engine.analyse(
            code=code_input,
            program_name=prog_name_input,
            llm_client=llm_client if run_llm else None,
            categories=categories,
        )
    st.session_state["cv_cc_result"] = result
    increment_analyses(user.id)
    from core.ui import add_to_analysis_history
    add_to_analysis_history({
        "type": "Clean Core",
        "program_name": prog_name_input,
        "level": result.clean_core_level,
        "violations": result.total_violations,
        "lines": result.total_lines,
        "critical": result.critical_count,
        "high": result.high_count,
    })
    st.rerun()

# ── Display results ───────────────────────────────────────────────────────────
result = st.session_state.get("cv_cc_result")

if result:
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    lm = result.level_meta
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(
        f'<div class="cv-metric" style="--mc:{lm["color"]}">'
        f'<div class="cv-metric-val">{cc_level_badge(result.clean_core_level)}</div>'
        f'<div class="cv-metric-lbl">Clean Core Level</div></div>',
        unsafe_allow_html=True,
    )
    col2.markdown(
        f'<div class="cv-metric" style="--mc:#BA0517">'
        f'<div class="cv-metric-val">{result.critical_count}</div>'
        f'<div class="cv-metric-lbl">Critical</div></div>', unsafe_allow_html=True)
    col3.markdown(
        f'<div class="cv-metric" style="--mc:#A33700">'
        f'<div class="cv-metric-val">{result.high_count}</div>'
        f'<div class="cv-metric-lbl">High</div></div>', unsafe_allow_html=True)
    col4.markdown(
        f'<div class="cv-metric" style="--mc:#7A5600">'
        f'<div class="cv-metric-val">{result.medium_count}</div>'
        f'<div class="cv-metric-lbl">Medium</div></div>', unsafe_allow_html=True)
    col5.markdown(
        f'<div class="cv-metric" style="--mc:#0176D3">'
        f'<div class="cv-metric-val">{result.total_lines:,}</div>'
        f'<div class="cv-metric-lbl">Lines Analysed</div></div>', unsafe_allow_html=True)

    # Level explanation
    st.markdown(f"""
    <div class="cv-card" style="border-left:5px solid {lm['color']};background:{lm['bg']}">
      <h3 style="color:{lm['color']}">{lm['icon']} {lm['label']}</h3>
      <p style="color:#444;margin:0;font-size:.9rem">
        {"No violations detected. This code meets SAP Clean Core Level A standards." if result.clean_core_level == "A"
         else f"Found {result.total_violations} violation(s) across {len(result.violations_by_category())} categories. "
              f"Remediation required to reach Level A compliance."}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Violations + AI analysis + Remediation tabs
    v_tab, ai_tab, rem_tab, export_tab = st.tabs([
        f"🔴 Violations ({result.total_violations})",
        "🤖 AI Analysis",
        "🔧 Auto-Remediation",
        "📥 Export",
    ])

    with v_tab:
        if not result.violations:
            st.success("✅ No violations found. Clean Core Level A achieved!")
        else:
            # Filter & sort controls
            fc1, fc2 = st.columns([2, 2])
            filter_sev = fc1.multiselect(
                "Filter by Severity",
                ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
                default=["CRITICAL", "HIGH", "MEDIUM"],
            )
            filter_cat = fc2.multiselect(
                "Filter by Category",
                list(result.violations_by_category().keys()),
                default=list(result.violations_by_category().keys()),
            )

            shown = [v for v in result.violations
                     if v.severity in filter_sev and v.category in filter_cat]
            st.markdown(f"Showing **{len(shown)}** of {result.total_violations} violations")

            for i, v in enumerate(shown[:50]):
                violation_card(v, i)

            if len(shown) > 50:
                st.info(f"Showing first 50 of {len(shown)} violations. Export Excel for full list.")

    with ai_tab:
        if result.llm_analysis:
            st.markdown(result.llm_analysis)
        elif not llm_client:
            st.info("Configure an LLM provider in **🔑 LLM Setup** to enable AI-powered deep analysis.")
        else:
            st.info("No AI analysis available for this result.")

    with rem_tab:
        if not user.has_permission("remediate"):
            st.error("Your role does not have remediation permission.")
        elif not llm_client:
            st.warning("LLM required for auto-remediation. Configure in **🔑 LLM Setup**.")
        elif not result.violations:
            st.success("✅ No violations to remediate.")
        else:
            st.markdown("""
            <div class="cv-card">
              <h3>🔧 AI-Powered Auto-Remediation</h3>
              <p style="color:#706E6B;font-size:.9rem">
                CoreShift will generate a Clean Core-compliant version of your code.
                All business logic is preserved — only the implementation pattern changes.
                Review the diff carefully before deploying to production.
              </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Generate Remediated Code", type="primary"):
                with st.spinner("🤖 Generating Clean Core-compliant code…"):
                    from core import clean_code_engine
                    remed_code, diff_html = clean_code_engine.remediate(
                        code_input, result.violations, llm_client
                    )
                    coverage = clean_code_engine.compute_remediation_coverage(
                        result.violations, remed_code
                    )
                st.session_state["cv_remed_code"]  = remed_code
                st.session_state["cv_diff_html"]   = diff_html
                st.session_state["cv_remed_cover"] = coverage
                st.session_state["cv_cc_result"].remediated_code = remed_code
                st.session_state["cv_cc_result"].diff_html = diff_html
                st.rerun()

            if st.session_state.get("cv_remed_code"):
                coverage = st.session_state.get("cv_remed_cover", 0)
                st.success(f"✅ Remediation complete — estimated {coverage}% of violations addressed.")

                r_tab, d_tab = st.tabs(["📄 Remediated Code", "🔀 Diff View"])
                with r_tab:
                    st.code(st.session_state["cv_remed_code"], language="abap")
                    st.download_button(
                        "⬇️ Download Remediated Code (.abap)",
                        data=st.session_state["cv_remed_code"],
                        file_name=f"{prog_name_input}_remediated.abap",
                        mime="text/plain",
                    )
                with d_tab:
                    st.markdown(st.session_state["cv_diff_html"], unsafe_allow_html=True)

    with export_tab:
        st.markdown("### Export Analysis Results")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export Word Report", use_container_width=True):
                from core.report_exporter import export_clean_core_word
                buf = export_clean_core_word(result)
                st.download_button(
                    "⬇️ Download .docx",
                    data=buf,
                    file_name=f"{prog_name_input}_CleanCore.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

        with col2:
            if st.button("📊 Export Excel (Violations)", use_container_width=True):
                from core.report_exporter import export_violations_excel
                buf = export_violations_excel(result.violations, prog_name_input)
                st.download_button(
                    "⬇️ Download .xlsx",
                    data=buf,
                    file_name=f"{prog_name_input}_violations.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        with col3:
            if st.button("📋 Export PDF Summary", use_container_width=True):
                from core.report_exporter import export_pdf
                content = (result.llm_analysis or
                           f"Program: {result.program_name}\n"
                           f"Clean Core Level: {result.clean_core_level}\n"
                           f"Violations: {result.total_violations}\n\n"
                           + "\n".join(f"- [{v.rule_id}] Line {v.line_number}: {v.rule.name}"
                                       for v in result.violations[:30]))
                buf = export_pdf("Clean Core Analysis Report", content, prog_name_input)
                st.download_button(
                    "⬇️ Download .pdf",
                    data=buf,
                    file_name=f"{prog_name_input}_CleanCore.pdf",
                    mime="application/pdf",
                )

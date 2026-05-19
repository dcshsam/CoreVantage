"""
CodeVantage — ECC to S/4HANA Migration Analysis Page
Three input modes: paste code | SAP system | SAP Readiness Check 2 upload
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.auth import require_auth, increment_analyses
from core.ui import (inject_css, page_header, sidebar_nav, metric_row,
                     severity_badge, violation_card, score_ring)

st.set_page_config(page_title="S/4 Migration — CodeVantage", page_icon="🚀", layout="wide")
inject_css()
user = require_auth()
sidebar_nav(user)

page_header(
    "🚀 ECC → S/4HANA Migration Analyser",
    "Identify migration blockers, estimate effort, and generate AI-powered migration plans",
    badge="Powered by SAP AI Core",
)

llm_client = st.session_state.get("cv_llm_client")
if not llm_client:
    st.warning("⚠️ No LLM connected. Rule-based scan will run. For migration plans + remediation, [configure LLM first](1_🔑_LLM_Setup).")

# ── Input tabs ────────────────────────────────────────────────────────────────
st.markdown("#### Step 1 — Input Source")
tab_paste, tab_system, tab_readiness = st.tabs([
    "📋 Paste ABAP Code",
    "🔗 Connect SAP System",
    "📁 SAP Readiness Check 2",
])

code_input = ""
readiness_result = None

with tab_paste:
    st.markdown('<div class="cv-card"><h3>Paste ABAP Source Code</h3></div>', unsafe_allow_html=True)
    sample = st.checkbox("Load ECC sample code with migration issues")
    if sample:
        default_code = """\
REPORT zecc_sd_order_proc.

" ECC-specific: Logical Database (S4-001)
LOGICAL DATABASE F1L.
NODES: vbak, vbap.

GET vbak.
  " Classic ALV Grid (S4-004)
  DATA: lo_alv TYPE REF TO cl_gui_alv_grid,
        lo_cnt TYPE REF TO cl_gui_custom_container.

  " OCCURS clause (S4-008)
  DATA: lt_orders TYPE TABLE OF vbak OCCURS 0.

  " Old FIELD-GROUPS (S4-009)
  FIELD-GROUPS: header, details.
  INSERT kunnr vbeln erdat INTO header.

  " Classic BDC (S4-002)
  FORM create_via_bdc.
    DATA: lt_bdc LIKE TABLE OF bdcdata.
    PERFORM bdc_dynpro USING 'SAPMV45A' '0101'.
    CALL TRANSACTION 'VA01' USING lt_bdc MODE 'N' UPDATE 'S'.
  ENDFORM.

  " SAP Script (S4-003)
  FORM print_order.
    CALL FUNCTION 'OPEN_FORM'
      EXPORTING form   = 'ZORDER_FORM'
                device = 'PRINTER'.
    CALL FUNCTION 'WRITE_FORM'
      EXPORTING element = 'ORDER_HEADER'.
    CALL FUNCTION 'CLOSE_FORM'.
  ENDFORM.

  " Non-Unicode (S4-006)
  DATA: lv_hex TYPE x LENGTH 4.
  OVERLAY lv_hex WITH '0000'.

  " User Exit instead of BAdI (S4-010)
  CALL CUSTOMER-FUNCTION '001'
    EXPORTING i_vbak = vbak.
"""
    else:
        default_code = ""
    code_input = st.text_area(
        "ECC ABAP Code",
        value=st.session_state.get("cv_s4_code", default_code),
        height=380,
        placeholder="Paste your ECC ABAP program for S/4HANA migration analysis…",
    )
    if code_input:
        st.session_state["cv_s4_code"] = code_input

with tab_system:
    st.markdown("""
    <div class="cv-card">
      <h3>Connect to ECC / S/4HANA Backend</h3>
      <p style="color:rgba(255,255,255,0.55);font-size:.9rem">
        Retrieve and analyse programs directly from your SAP system.
        Supports bulk analysis of multiple objects.
      </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("sap_s4_form"):
        c1, c2, c3 = st.columns(3)
        s4_host    = c1.text_input("Host",   placeholder="sap-host.example.com")
        s4_client  = c2.text_input("Client", value="100")
        s4_sysnr   = c3.text_input("SysNr",  value="00")
        c4, c5 = st.columns(2)
        s4_user    = c4.text_input("User")
        s4_pass    = c5.text_input("Password", type="password")
        s4_prog    = st.text_input("Program Name", placeholder="ZECC_PROGRAM")
        fetch_s4   = st.form_submit_button("⬇️ Fetch & Analyse", type="primary")

    if fetch_s4 and s4_host and s4_prog:
        from core.sap_connector import SAPConnector
        with st.spinner(f"Fetching {s4_prog}…"):
            conn = SAPConnector(s4_host, s4_client, s4_user, s4_pass, s4_sysnr)
            src  = conn.get_program_source(s4_prog)
        if src:
            code_input = src
            st.session_state["cv_s4_code"] = src
            st.success(f"✅ Fetched {len(src):,} chars from {s4_prog}")
        else:
            st.error("Could not fetch source. Check ADT services and authorization.")

with tab_readiness:
    st.markdown("""
    <div class="cv-card">
      <h3>SAP Readiness Check 2 — Report Upload</h3>
      <p style="color:rgba(255,255,255,0.55);font-size:.9rem">
        Upload the Excel report exported from SAP Readiness Check 2
        (<b>Transaction: /SDF/RC_START_CHECK</b> or SAP Readiness Check portal).
        CodeVantage will parse all custom code findings and generate a migration plan.
      </p>
      <p style="color:#888;font-size:.82rem">
        Supported formats: <b>.xlsx</b>, <b>.xls</b>, <b>.csv</b>
      </p>
    </div>
    """, unsafe_allow_html=True)

    rc_file = st.file_uploader(
        "Upload SAP Readiness Check 2 Export",
        type=["xlsx", "xls", "csv"],
        key="rc_upload",
    )
    if rc_file:
        with st.spinner("Parsing Readiness Check 2 report…"):
            try:
                from core.readiness_parser import parse_readiness_check
                readiness_result = parse_readiness_check(rc_file.read(), rc_file.name)
                st.session_state["cv_rc_result"] = readiness_result
                st.success(f"✅ {readiness_result.summary_text}")
            except Exception as exc:
                st.error(f"Parse failed: {exc}")

    if st.session_state.get("cv_rc_result"):
        rc = st.session_state["cv_rc_result"]
        st.markdown("#### Readiness Check Summary")
        metric_row([
            {"label": "Total Objects",    "value": str(rc.total_objects),  "color": "#0176D3"},
            {"label": "Critical",         "value": str(rc.critical_count), "color": "#BA0517"},
            {"label": "High",             "value": str(rc.high_count),     "color": "#A33700"},
            {"label": "Readiness Score",  "value": f"{rc.readiness_score}/100",
             "color": "#2E844A" if rc.readiness_score >= 80 else "#7A5600"},
        ])

        if rc.items:
            import pandas as pd
            df = pd.DataFrame([
                {"Object": i.object_name, "Type": i.object_type,
                 "Severity": i.severity, "Description": i.description[:100]}
                for i in rc.items[:100]
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

# ── Program name ──────────────────────────────────────────────────────────────
if not code_input:
    code_input = st.session_state.get("cv_s4_code", "")

prog_name_s4 = st.text_input(
    "Program / Object Name",
    value=st.session_state.get("cv_s4_prog_name", "ZECC_PROGRAM"),
)
st.session_state["cv_s4_prog_name"] = prog_name_s4

# ── Run analysis ──────────────────────────────────────────────────────────────
st.markdown("---")
source_is_readiness = bool(readiness_result or st.session_state.get("cv_rc_result"))
source_is_code      = bool(code_input.strip())

col_run, col_plan, col_clear = st.columns([2, 2, 1])
with col_run:
    run_btn  = st.button("🔍 Run Migration Analysis", type="primary",
                          use_container_width=True,
                          disabled=not (source_is_code or source_is_readiness))
with col_plan:
    plan_btn = st.button("📋 Generate Migration Plan (AI)", use_container_width=True,
                          disabled=not (st.session_state.get("cv_s4_result") and llm_client))
with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):
        for k in ["cv_s4_code", "cv_s4_result", "cv_rc_result", "cv_s4_plan"]:
            st.session_state.pop(k, None)
        st.rerun()

if run_btn and source_is_code:
    with st.spinner("🔍 Analysing ECC code for S/4HANA compatibility…"):
        from core import s4_migration_engine
        result = s4_migration_engine.analyse(
            code=code_input,
            program_name=prog_name_s4,
            llm_client=llm_client,
        )
    st.session_state["cv_s4_result"] = result
    increment_analyses(user.id)
    from core.ui import add_to_analysis_history
    add_to_analysis_history({
        "type": "S/4 Migration",
        "program_name": prog_name_s4,
        "level": "D" if result.readiness_score < 50 else ("C" if result.readiness_score < 80 else "B"),
        "violations": result.total_violations,
        "lines": result.total_lines,
        "score": result.readiness_score,
        "effort": result.effort_days,
        "risk": result.risk_level,
    })
    st.rerun()

if plan_btn:
    with st.spinner("🤖 Generating sprint-by-sprint migration plan…"):
        from core import s4_migration_engine
        plan = s4_migration_engine.generate_migration_plan(
            st.session_state["cv_s4_result"], llm_client
        )
    st.session_state["cv_s4_plan"] = plan
    st.rerun()

# ── Display results ───────────────────────────────────────────────────────────
result = st.session_state.get("cv_s4_result")

if result:
    st.markdown("---")
    st.markdown("## 📊 Migration Analysis Results")

    score_color = result.score_color()
    approach_colors = {
        "BROWNFIELD": "#30D158",
        "SELECTIVE_DATA": "#FF9F0A",
        "GREENFIELD": "#FF453A",
    }

    metric_row([
        {"label": "Readiness Score",    "value": f"{result.readiness_score}/100",
         "color": score_color},
        {"label": "S/4 Issues Found",   "value": str(result.total_violations), "color": "#FF9F0A"},
        {"label": "Estimated Effort",   "value": f"{result.effort_days}d",      "color": "#0A84FF"},
        {"label": "Risk Level",         "value": result.risk_level,            "color": score_color},
        {"label": "Recommended Path",   "value": result.approach.replace("_", " "),
         "color": approach_colors.get(result.approach, "#0A84FF")},
    ])

    _approach_desc = {
        "BROWNFIELD":     "Minimal disruption path. Migrate in-place with targeted code fixes.",
        "SELECTIVE_DATA": "Moderate rework required. Consider selective data transition to clean up legacy data.",
        "GREENFIELD":     "Significant custom code rewrite needed. Greenfield implementation recommended for clean break.",
    }.get(result.approach, "")
    st.markdown(f"""
    <div class="cv-card" style="border-left:5px solid {score_color}">
      <h3 style="color:{score_color}">{result.score_label()}</h3>
      <p style="color:rgba(255,255,255,0.55);font-size:.9rem">
        Approach recommendation: <b>{result.approach.replace("_"," ")}</b> — {_approach_desc}
      </p>
    </div>
    """, unsafe_allow_html=True)

    v_tab, ai_tab, rem_tab, plan_tab, export_tab = st.tabs([
        f"🔴 Issues ({result.total_violations})",
        "🤖 AI Analysis",
        "🔧 Migrate Code",
        "📋 Migration Plan",
        "📥 Export",
    ])

    with v_tab:
        if not result.s4_violations:
            st.success("✅ No S/4HANA migration issues detected. Code is ready for S/4HANA.")
        else:
            for i, v in enumerate(result.s4_violations[:50]):
                violation_card(v, i)

    with ai_tab:
        if result.llm_analysis:
            st.markdown(result.llm_analysis)
        else:
            st.info("Configure LLM in **🔑 LLM Setup** for AI-powered migration analysis.")

    with rem_tab:
        if not user.has_permission("remediate"):
            st.error("Remediation permission required.")
        elif not llm_client:
            st.warning("LLM required. Configure in **🔑 LLM Setup**.")
        elif not result.s4_violations:
            st.success("✅ No migration issues to fix.")
        else:
            st.markdown("""
            <div class="cv-card">
              <h3>🔧 AI-Powered ECC → S/4HANA Code Migration</h3>
              <p style="color:rgba(255,255,255,0.55);font-size:.9rem">
                CodeVantage will generate S/4HANA-compatible code, replacing deprecated APIs,
                removing obsolete constructs, and modernising the ABAP syntax.
              </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Migrate Code to S/4HANA", type="primary"):
                with st.spinner("🤖 Migrating ECC code to S/4HANA…"):
                    from core import s4_migration_engine
                    migrated, diff_html = s4_migration_engine.remediate(
                        code_input, result.s4_violations, llm_client
                    )
                st.session_state["cv_s4_migrated"]  = migrated
                st.session_state["cv_s4_diff"]      = diff_html
                st.rerun()

            if st.session_state.get("cv_s4_migrated"):
                st.success("✅ Code migration complete.")
                r_tab, d_tab = st.tabs(["📄 Migrated Code", "🔀 Diff View"])
                with r_tab:
                    st.code(st.session_state["cv_s4_migrated"], language="abap")
                    st.download_button(
                        "⬇️ Download Migrated Code",
                        data=st.session_state["cv_s4_migrated"],
                        file_name=f"{prog_name_s4}_s4hana.abap",
                        mime="text/plain",
                    )
                with d_tab:
                    st.markdown(st.session_state["cv_s4_diff"], unsafe_allow_html=True)

    with plan_tab:
        if st.session_state.get("cv_s4_plan"):
            st.markdown(st.session_state["cv_s4_plan"])
            st.download_button(
                "⬇️ Download Migration Plan (.md)",
                data=st.session_state["cv_s4_plan"],
                file_name=f"{prog_name_s4}_migration_plan.md",
                mime="text/markdown",
            )
        else:
            st.info("Click **📋 Generate Migration Plan (AI)** above to create a sprint-by-sprint plan.")

    with export_tab:
        st.markdown("### Export Reports")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Word Report", use_container_width=True):
                from core.report_exporter import export_s4_migration_word
                st.session_state["cv_s4_result"].migration_plan = st.session_state.get("cv_s4_plan", "")
                buf = export_s4_migration_word(result)
                st.download_button("⬇️ Download .docx", data=buf,
                    file_name=f"{prog_name_s4}_S4Migration.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with col2:
            if st.button("📊 Excel (Issues)", use_container_width=True):
                from core.report_exporter import export_violations_excel
                buf = export_violations_excel(result.violations, prog_name_s4)
                st.download_button("⬇️ Download .xlsx", data=buf,
                    file_name=f"{prog_name_s4}_s4_issues.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col3:
            if st.button("📋 PDF Summary", use_container_width=True):
                from core.report_exporter import export_pdf
                content = (result.llm_analysis or
                           f"Migration Score: {result.readiness_score}/100\n"
                           f"Effort: {result.effort_days} days\nRisk: {result.risk_level}")
                buf = export_pdf("S/4HANA Migration Analysis", content, prog_name_s4)
                st.download_button("⬇️ Download .pdf", data=buf,
                    file_name=f"{prog_name_s4}_migration.pdf", mime="application/pdf")

"""
CodeVantage — LLM Setup Page
Configure and test LLM providers: SAP AI Core (default), GROQ, Anthropic, OpenAI.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.auth import require_auth
from core.ui import inject_css, page_header, sidebar_nav

st.set_page_config(page_title="LLM Setup — CodeVantage", page_icon="🔑", layout="wide")
inject_css()
user = require_auth()
sidebar_nav(user)

page_header(
    "🔑 LLM Configuration",
    "Connect to SAP AI Core (default) or a fallback LLM provider",
    badge="Step 1 of 1",
)

# ── Current status ────────────────────────────────────────────────────────────
if st.session_state.get("cv_llm_client"):
    st.success(f"✅ **Active LLM:** {st.session_state.get('cv_llm_display', '—')}")
else:
    st.warning("⚠️ No LLM configured yet. Rule-based analysis works without LLM, but AI insights and auto-remediation require a connection.")

st.markdown("---")

tab_sap, tab_groq, tab_anthropic, tab_openai = st.tabs([
    "🏢 SAP AI Core (Recommended)",
    "⚡ GROQ (Free)",
    "🤖 Anthropic Claude",
    "🧠 OpenAI GPT",
])

# ── SAP AI Core ───────────────────────────────────────────────────────────────
with tab_sap:
    st.markdown("""
    <div class="cv-card">
      <h3>SAP AI Core — Enterprise-Grade AI on SAP BTP</h3>
      <p style="color:#706E6B;font-size:.875rem">
        Recommended for enterprise use. Credentials are read from your <code>.env</code> file.
        Data processed through SAP AI Core stays within your BTP landscape.
      </p>
    </div>
    """, unsafe_allow_html=True)

    _fields = {
        "Client ID"     : os.getenv("AICORE_CLIENT_ID", ""),
        "Client Secret" : os.getenv("AICORE_CLIENT_SECRET", ""),
        "Auth URL"      : os.getenv("AICORE_AUTH_URL", ""),
        "Base URL"      : os.getenv("AICORE_BASE_URL", ""),
        "Resource Group": os.getenv("AICORE_RESOURCE_GROUP", ""),
    }
    _optional = {"Resource Group"}
    _missing  = [k for k, v in _fields.items() if not v and k not in _optional]

    rows_html = ""
    for field_name, value in _fields.items():
        if value:
            masked  = value[:4] + "●" * min(8, len(value) - 4)
            status  = '<span style="color:#2E844A;font-weight:700">✅ Loaded</span>'
            display = f'<code>{masked}</code>'
        elif field_name in _optional:
            status  = '<span style="color:#7A5600;font-weight:700">⚠️ Optional</span>'
            display = "—"
        else:
            status  = '<span style="color:#BA0517;font-weight:700">❌ Missing</span>'
            display = "—"
        rows_html += f"<tr><td style='padding:6px 12px'>{field_name}</td><td style='padding:6px 12px'>{status}</td><td style='padding:6px 12px'>{display}</td></tr>"

    model_env = os.getenv("AICORE_MODEL", "gpt-4o")
    rows_html += (
        f"<tr><td style='padding:6px 12px'>Model</td>"
        f"<td style='padding:6px 12px'><span style='color:#2E844A;font-weight:700'>✅ Set</span></td>"
        f"<td style='padding:6px 12px'><code>{model_env}</code></td></tr>"
    )

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)">
      <thead><tr style="background:#032D60;color:white">
        <th style="padding:8px 12px;text-align:left">Field</th>
        <th style="padding:8px 12px;text-align:left">Status</th>
        <th style="padding:8px 12px;text-align:left">Value</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

    col_m, col_btn = st.columns([2, 1])
    with col_m:
        sap_model = st.selectbox(
            "Model",
            ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-35-turbo",
             "gemini-1.5-pro", "claude-3-5-sonnet",
             "meta--llama3-70b-instruct", "mistralai--mixtral-8x7b-instruct-v01"],
            index=0,
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        test_sap = st.button("🔌 Test SAP AI Core", type="primary",
                              use_container_width=True, disabled=bool(_missing))

    if _missing:
        st.error(f"Missing required .env variables: **{', '.join(_missing)}**")

    if test_sap:
        with st.spinner("Authenticating with SAP AI Core…"):
            try:
                from core.llm_client import LLMClient
                client = LLMClient(provider="sap_ai_core", model_name=sap_model)
                reply  = client.ping()
                st.session_state["cv_llm_client"]  = client
                st.session_state["cv_llm_display"] = f"SAP AI Core | {sap_model}"
                st.success(f"✅ Connected! Model **{sap_model}** replied: **{reply}**")
            except Exception as exc:
                st.error(f"Connection failed: {exc}")
                st.info("Tips: Ensure AICORE_BASE_URL ends with `/v2`. Check deployment is Running in AI Launchpad.")

# ── GROQ ──────────────────────────────────────────────────────────────────────
with tab_groq:
    st.markdown("""
    <div class="cv-card">
      <h3>GROQ — Free High-Speed Inference</h3>
      <p style="color:#706E6B;font-size:.875rem">
        Free tier available at <b>console.groq.com</b>. Excellent for development and testing.
        Llama 3.3 70B is recommended for ABAP analysis quality.
      </p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        groq_key = st.text_input("GROQ API Key", value=os.getenv("GROQ_API_KEY", ""),
                                  type="password", placeholder="gsk_...")
    with col2:
        groq_model = st.selectbox("Model", [
            "llama-3.3-70b-versatile", "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768", "gemma2-9b-it",
        ])
    if st.button("🔌 Test GROQ", type="primary"):
        if not groq_key:
            st.error("Enter your GROQ API key.")
        else:
            with st.spinner("Testing GROQ connection…"):
                try:
                    from core.llm_client import LLMClient
                    client = LLMClient(provider="groq", api_key=groq_key, model=groq_model)
                    reply  = client.ping()
                    st.session_state["cv_llm_client"]  = client
                    st.session_state["cv_llm_display"] = f"GROQ | {groq_model}"
                    st.success(f"✅ Connected! **{groq_model}** replied: **{reply}**")
                except Exception as exc:
                    st.error(f"Failed: {exc}")

# ── Anthropic ─────────────────────────────────────────────────────────────────
with tab_anthropic:
    st.markdown("""
    <div class="cv-card">
      <h3>Anthropic Claude</h3>
      <p style="color:#706E6B;font-size:.875rem">
        Excellent ABAP analysis quality. <b>Claude Sonnet 4.6</b> is the recommended model —
        it delivers deep SAP domain reasoning with fast response times.
        Claude Opus 4.7 provides the highest accuracy for complex migration plans.
      </p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        ant_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY", ""),
                                 type="password", placeholder="sk-ant-...")
    with col2:
        ant_model = st.selectbox("Model", [
            "claude-sonnet-4-6",
            "claude-opus-4-7",
            "claude-haiku-4-5-20251001",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ])
    if st.button("🔌 Test Anthropic", type="primary"):
        if not ant_key:
            st.error("Enter your Anthropic API key.")
        else:
            with st.spinner("Testing Anthropic connection…"):
                try:
                    from core.llm_client import LLMClient
                    client = LLMClient(provider="anthropic", api_key=ant_key, model=ant_model)
                    reply  = client.ping()
                    st.session_state["cv_llm_client"]  = client
                    st.session_state["cv_llm_display"] = f"Anthropic | {ant_model}"
                    st.success(f"✅ Connected! Replied: **{reply}**")
                except Exception as exc:
                    st.error(f"Failed: {exc}")

# ── OpenAI ────────────────────────────────────────────────────────────────────
with tab_openai:
    st.markdown('<div class="cv-card"><h3>OpenAI GPT</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        oai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""),
                                 type="password", placeholder="sk-...")
    with col2:
        oai_model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"])
    if st.button("🔌 Test OpenAI", type="primary"):
        if not oai_key:
            st.error("Enter your OpenAI API key.")
        else:
            with st.spinner("Testing OpenAI connection…"):
                try:
                    from core.llm_client import LLMClient
                    client = LLMClient(provider="openai", api_key=oai_key, model=oai_model)
                    reply  = client.ping()
                    st.session_state["cv_llm_client"]  = client
                    st.session_state["cv_llm_display"] = f"OpenAI | {oai_model}"
                    st.success(f"✅ Connected! Replied: **{reply}**")
                except Exception as exc:
                    st.error(f"Failed: {exc}")

# ── Proceed ───────────────────────────────────────────────────────────────────
st.markdown("---")
if st.session_state.get("cv_llm_client"):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Clean Core Analysis", type="primary", use_container_width=True):
            st.switch_page("pages/2_🧹_Clean_Core.py")
    with col2:
        if st.button("Go to S/4 Migration", type="primary", use_container_width=True):
            st.switch_page("pages/3_🚀_S4_Migration.py")

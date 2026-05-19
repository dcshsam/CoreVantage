"""
CodeVantage — Dedicated LLM Setup Page
First stop after login. Must connect an LLM to proceed to the dashboard.
"""

import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.auth import require_auth
from core.ui import inject_css

st.set_page_config(
    page_title="LLM Setup — CodeVantage",
    page_icon="🔑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
user = require_auth()

# ── Hide sidebar on this page ─────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.cv-proceed-btn [data-testid="stPageLink"] a,
.cv-proceed-btn [data-testid="stPageLink"] a:visited {
    display: block !important; width: 100% !important; text-align: center !important;
    background: #0176D3 !important; color: #FFFFFF !important;
    padding: 12px 20px !important; border-radius: 6px !important;
    font-weight: 700 !important; font-size: 1rem !important;
    text-decoration: none !important; text-transform: none !important;
    border: none !important; box-shadow: 0 2px 8px rgba(1,118,211,.35) !important;
    letter-spacing: 0.1px !important;
}
.cv-proceed-btn [data-testid="stPageLink"] a:hover { background: #0265B8 !important; }
/* Disabled state — grayed out, not clickable */
[data-testid="stButton"] button:disabled {
    background: #E8E8E8 !important; color: #AAAAAA !important;
    border-color: #DDDBDA !important; cursor: not-allowed !important;
    box-shadow: none !important; opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

llm_connected = bool(st.session_state.get("cv_llm_client"))

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:16px 4px 14px;border-bottom:1px solid #DDDBDA;margin-bottom:28px">
  <div style="display:flex;align-items:center;gap:12px">
    <div style="background:#0176D3;border-radius:10px;width:38px;height:38px;
                display:flex;align-items:center;justify-content:center;
                font-size:1.2rem;box-shadow:0 2px 8px rgba(1,118,211,0.35)">⚡</div>
    <div>
      <div style="font-size:1.1rem;font-weight:700;color:#032D60">CodeVantage</div>
      <div style="font-size:0.68rem;color:#706E6B;font-weight:600;
                  text-transform:uppercase;letter-spacing:.5px">ABAP Intelligence Platform</div>
    </div>
  </div>
  <div style="font-size:0.82rem;color:#706E6B">
    Signed in as <strong style="color:#032D60">{user.full_name or user.username}</strong>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Page title ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:24px">
  <h2 style="color:#032D60;font-size:1.35rem;font-weight:700;margin-bottom:4px">
    🔑 Connect an LLM Provider
  </h2>
  <p style="color:#706E6B;font-size:.88rem;margin:0">
    Select a provider below, enter your credentials, and click Test Connection.
    Once connected the <strong>Go to Dashboard</strong> button will activate.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Status banner ─────────────────────────────────────────────────────────────
if llm_connected:
    col_msg, col_switch = st.columns([5, 1])
    with col_msg:
        st.success(f"✅ **Connected:** {st.session_state.get('cv_llm_display', '—')}  —  You can now proceed to the dashboard.")
    with col_switch:
        if st.button("Switch Provider", use_container_width=True):
            st.session_state.pop("cv_llm_client", None)
            st.session_state.pop("cv_llm_display", None)
            st.rerun()
else:
    st.info("⚠️ No LLM connected yet. Choose a provider tab and test your connection.")

st.markdown("---")

# ── Provider tabs ─────────────────────────────────────────────────────────────
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

    _fields   = {
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
    <table style="width:100%;border-collapse:collapse;background:white;border-radius:8px;
                  overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:12px">
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
        sap_model = st.selectbox("Model", [
            "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-35-turbo",
            "gemini-1.5-pro", "claude-3-5-sonnet",
            "meta--llama3-70b-instruct", "mistralai--mixtral-8x7b-instruct-v01",
        ])
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
                st.rerun()
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
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed: {exc}")

# ── Anthropic ─────────────────────────────────────────────────────────────────
with tab_anthropic:
    st.markdown("""
    <div class="cv-card">
      <h3>Anthropic Claude</h3>
      <p style="color:#706E6B;font-size:.875rem">
        Excellent ABAP analysis quality. <b>Claude Sonnet 4.6</b> is the recommended model —
        deep SAP domain reasoning with fast response times.
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
                    st.rerun()
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
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed: {exc}")

# ── Proceed button ────────────────────────────────────────────────────────────
st.markdown("---")
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    if llm_connected:
        st.markdown('<div class="cv-proceed-btn">', unsafe_allow_html=True)
        st.page_link("app.py", label="Go to Dashboard →", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.button("Go to Dashboard →", use_container_width=True,
                  disabled=True, key="btn_proceed_disabled")
        st.caption("Connect an LLM above to enable this button.")

# ── Sign out ──────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
_, so_col, _ = st.columns([4, 1, 4])
with so_col:
    if st.button("Sign Out", use_container_width=True, key="btn_signout"):
        from core.auth import logout
        logout()
        st.rerun()

st.markdown(
    "<div style='text-align:center;margin-top:16px;color:#706E6B;font-size:.75rem'>"
    "v1.1.0 · Powered by SPRAC · 2025</div>",
    unsafe_allow_html=True,
)

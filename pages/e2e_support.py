"""
CoreShift — E2E Support
Placeholder page for the End-to-End SAP Support product.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="E2E Support — CoreShift",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.auth import require_auth
from core.ui import inject_css, sidebar_nav

inject_css()
user = require_auth()
sidebar_nav(user)

st.markdown("""
<div style="text-align:center;padding:60px 0 30px">
  <div style="background:#EEF6EC;border-radius:16px;width:72px;height:72px;
              display:inline-flex;align-items:center;justify-content:center;
              font-size:2.2rem;border:1px solid #B8DDB0;margin-bottom:20px">🔄</div>
  <h2 style="color:#032D60;font-size:1.6rem;font-weight:700;margin-bottom:8px">
    E2E Support
  </h2>
  <p style="color:#2E844A;font-size:.8rem;font-weight:600;text-transform:uppercase;
            letter-spacing:.8px;margin-bottom:16px">End to End SAP Support</p>
  <p style="color:#706E6B;font-size:.95rem;max-width:480px;margin:0 auto;line-height:1.7">
    End-to-end SAP support tooling — from requirement to deployment.<br>
    AI-assisted workflows for functional specifications, ABAP code review,
    and solution documentation across the full SAP delivery lifecycle.
  </p>
  <div style="margin-top:28px">
    <span style="background:#EEF6EC;color:#2E844A;border-radius:6px;padding:6px 18px;
                 font-size:.85rem;font-weight:600;border:1px solid #91C98C">
      🚧 Coming Soon
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

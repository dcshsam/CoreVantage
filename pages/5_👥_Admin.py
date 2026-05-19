"""
CodeVantage — User, Role & Custom Rule Administration (Admin only)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.auth import (require_auth, require_permission, load_users,
                       create_user, update_user, delete_user, ROLES)
from core.ui import inject_css, page_header, sidebar_nav
from core.custom_rules import (
    load_custom_rules, create_custom_rule, update_custom_rule,
    delete_custom_rule, toggle_custom_rule, CATEGORIES, SEVERITIES, CC_LEVELS,
)

st.set_page_config(page_title="Admin — CodeVantage", page_icon="👥", layout="wide")
inject_css()
user = require_auth()
require_permission("admin")
sidebar_nav(user)

page_header(
    "👥 Administration",
    "Manage users, roles, and custom ABAP detection rules",
    badge="Admin Only",
)

tab_users, tab_rules, tab_system = st.tabs([
    "👥  User Management",
    "📋  Custom Rules",
    "⚙️  System Info",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — User Management
# ═══════════════════════════════════════════════════════════════════════════════
with tab_users:
    with st.expander("📖 Role Reference (SAP Authorization Model)", expanded=False):
        cols = st.columns(len(ROLES))
        for col, (role_key, role_info) in zip(cols, ROLES.items()):
            col.markdown(f"""
            <div class="cv-card" style="border-top:4px solid {role_info['color']}">
              <h3 style="color:{role_info['color']}">{role_info['icon']} {role_info['label']}</h3>
              <div style="font-size:.8rem;color:#706E6B;font-family:monospace">
                SAP Role: {role_info['sap_role']}
              </div>
              <div style="margin-top:8px;font-size:.82rem">
                {'<br>'.join(f"✓ {p}" for p in sorted(role_info['permissions']))}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Registered Users")
    all_users = load_users()

    if not all_users:
        st.info("No users found.")
    else:
        for u in all_users:
            role_info = ROLES.get(u.role, {})
            icon      = role_info.get("icon", "⚪")
            with st.expander(
                f"{icon} {u.full_name} (@{u.username}) — {u.role_label()}"
                + (" 🔴 INACTIVE" if not u.active else ""),
                expanded=False,
            ):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"""
                    **ID:** `{u.id}`
                    **Email:** {u.email}
                    **Analyses Run:** {u.analyses_run}
                    **Created:** {u.created_at[:10] if u.created_at else '—'}
                    **Last Login:** {u.last_login[:10] if u.last_login else 'Never'}
                    """)
                with col2:
                    with st.form(f"edit_{u.id}"):
                        st.markdown("**Edit User**")
                        new_name   = st.text_input("Full Name", value=u.full_name,  key=f"name_{u.id}")
                        new_email  = st.text_input("Email",     value=u.email,      key=f"email_{u.id}")
                        new_role   = st.selectbox("Role", list(ROLES.keys()),
                                                  index=list(ROLES.keys()).index(u.role) if u.role in ROLES else 0,
                                                  key=f"role_{u.id}")
                        new_pass   = st.text_input("New Password (blank = no change)",
                                                   type="password", key=f"pass_{u.id}")
                        new_active = st.checkbox("Active", value=u.active, key=f"active_{u.id}")
                        if st.form_submit_button("Save Changes", type="primary"):
                            kwargs = {"full_name": new_name, "email": new_email,
                                      "role": new_role, "active": new_active}
                            if new_pass:
                                kwargs["password"] = new_pass
                            ok, msg = update_user(u.id, **kwargs)
                            if ok: st.success(msg); st.rerun()
                            else:  st.error(msg)
                with col3:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    if u.id != user.id:
                        if st.button("Delete", key=f"del_{u.id}"):
                            ok, msg = delete_user(u.id, user.id)
                            if ok: st.success(msg); st.rerun()
                            else:  st.error(msg)
                    else:
                        st.caption("(you)")

    st.markdown("---")
    st.markdown("### Create New User")
    with st.form("create_user_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nu_username  = c1.text_input("Username *",   placeholder="j.smith")
        nu_fullname  = c2.text_input("Full Name *",  placeholder="Jane Smith")
        nu_email     = c1.text_input("Email *",      placeholder="j.smith@company.com")
        nu_role      = c2.selectbox("Role *",        list(ROLES.keys()))
        nu_password  = c1.text_input("Password *",   type="password")
        nu_password2 = c2.text_input("Confirm Password *", type="password")
        create_sub   = st.form_submit_button("Create User", type="primary")

    if create_sub:
        if not all([nu_username, nu_fullname, nu_email, nu_password]):
            st.error("All fields marked * are required.")
        elif nu_password != nu_password2:
            st.error("Passwords do not match.")
        elif len(nu_password) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            ok, msg = create_user(nu_username, nu_password, nu_fullname, nu_email, nu_role)
            if ok: st.success(f"✅ {msg}"); st.rerun()
            else:  st.error(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Custom Rules
# ═══════════════════════════════════════════════════════════════════════════════
with tab_rules:
    custom_rules = load_custom_rules()

    # ── Stats row ─────────────────────────────────────────────────────────────
    enabled_count  = sum(1 for r in custom_rules if r.get("enabled", True))
    disabled_count = len(custom_rules) - enabled_count

    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f'<div class="cv-metric" style="--mc:#0176D3">'
        f'<div class="cv-metric-val">{len(custom_rules)}</div>'
        f'<div class="cv-metric-lbl">Total Custom Rules</div></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="cv-metric" style="--mc:#2E844A">'
        f'<div class="cv-metric-val">{enabled_count}</div>'
        f'<div class="cv-metric-lbl">Active</div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="cv-metric" style="--mc:#706E6B">'
        f'<div class="cv-metric-val">{disabled_count}</div>'
        f'<div class="cv-metric-lbl">Disabled</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Existing custom rules ─────────────────────────────────────────────────
    if not custom_rules:
        st.info("No custom rules yet. Use the form below to create your first rule.")
    else:
        st.markdown(f"### Custom Rules ({len(custom_rules)})")
        SEV_COLOR = {"CRITICAL":"#BA0517","HIGH":"#A33700","MEDIUM":"#7A5600",
                     "LOW":"#0176D3","INFO":"#706E6B"}
        CAT_COLOR = {"CLEAN_CORE":"#0176D3","S4_MIGRATION":"#A33700",
                     "SECURITY":"#BA0517","PERFORMANCE":"#2E844A"}

        for idx, cr in enumerate(custom_rules):
            rid      = cr["id"]
            enabled  = cr.get("enabled", True)
            sev      = cr.get("severity","MEDIUM")
            cat      = cr.get("category","CLEAN_CORE")
            sc       = SEV_COLOR.get(sev,"#888")
            cc       = CAT_COLOR.get(cat,"#888")
            status   = "🟢 Active" if enabled else "⚫ Disabled"

            with st.expander(
                f"**[{rid}]** {cr['name']}  —  {status}",
                expanded=False,
            ):
                # Badge row
                st.markdown(
                    f'<span style="background:{sc}18;color:{sc};border:1px solid {sc}60;'
                    f'border-radius:4px;padding:2px 9px;font-size:.72rem;font-weight:700">{sev}</span>'
                    f'&nbsp;'
                    f'<span style="background:{cc}12;color:{cc};border:1px solid {cc}50;'
                    f'border-radius:4px;padding:2px 9px;font-size:.72rem;font-weight:600">'
                    f'{cat.replace("_"," ").title()}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown("")

                col_info, col_actions = st.columns([3, 1])

                with col_info:
                    st.markdown(f"**Description:** {cr.get('description','—')}")
                    st.markdown(f"**Remediation:** {cr.get('remediation','—')}")
                    patterns = cr.get("patterns", [])
                    st.markdown(
                        "**Patterns:** " +
                        " · ".join(f"`{p}`" for p in patterns[:5]) +
                        (f" _(+{len(patterns)-5} more)_" if len(patterns) > 5 else "")
                    )
                    meta = []
                    if cr.get("cc_level"):  meta.append(f"Level {cr['cc_level']}")
                    if cr.get("s4_impact"): meta.append("S/4 Impact")
                    if cr.get("tags"):      meta.append("Tags: " + ", ".join(cr["tags"]))
                    if cr.get("created_by"):meta.append(f"By: {cr['created_by']}")
                    if meta: st.caption(" · ".join(meta))

                with col_actions:
                    new_state = st.toggle(
                        "Enabled", value=enabled, key=f"toggle_{rid}",
                    )
                    if new_state != enabled:
                        toggle_custom_rule(rid, new_state)
                        st.rerun()

                    if st.button("Edit", key=f"edit_btn_{rid}", use_container_width=True):
                        st.session_state[f"editing_{rid}"] = True

                    if st.button("Delete", key=f"delete_btn_{rid}", use_container_width=True):
                        ok, msg = delete_custom_rule(rid)
                        if ok: st.success(msg); st.rerun()
                        else:  st.error(msg)

                # ── Inline edit form ──────────────────────────────────────────
                if st.session_state.get(f"editing_{rid}"):
                    st.markdown("---")
                    st.markdown("#### Edit Rule")
                    with st.form(f"edit_rule_{rid}"):
                        e1, e2 = st.columns(2)
                        e_name  = e1.text_input("Rule Name *",    value=cr["name"])
                        e_cat   = e2.selectbox("Category *", CATEGORIES,
                                               index=CATEGORIES.index(cr.get("category","CLEAN_CORE")))
                        e3, e4  = st.columns(2)
                        e_sev   = e3.selectbox("Severity *", SEVERITIES,
                                               index=SEVERITIES.index(cr.get("severity","MEDIUM")))
                        e_lvl   = e4.selectbox("Clean Core Level", CC_LEVELS,
                                               index=CC_LEVELS.index(cr.get("cc_level","")) if cr.get("cc_level","") in CC_LEVELS else 0)
                        e_desc  = st.text_area("Description", value=cr.get("description",""), height=80)
                        e_pats  = st.text_area("Detection Patterns (one per line) *",
                                               value="\n".join(cr.get("patterns",[])), height=120)
                        e_rem   = st.text_area("Remediation *", value=cr.get("remediation",""), height=100)
                        e5, e6  = st.columns(2)
                        e_bad   = e5.text_area("Example — Non-Compliant",  value=cr.get("example_bad",""),  height=100)
                        e_good  = e6.text_area("Example — Compliant",      value=cr.get("example_good",""), height=100)
                        e7, e8  = st.columns(2)
                        e_tags  = e7.text_input("Tags (comma-separated)",
                                                value=", ".join(cr.get("tags",[])))
                        e_s4    = e8.checkbox("S/4HANA Impact", value=cr.get("s4_impact", False))
                        e_sub, e_cancel = st.columns(2)
                        save_edit   = e_sub.form_submit_button("Save Changes", type="primary", use_container_width=True)
                        cancel_edit = e_cancel.form_submit_button("Cancel", use_container_width=True)

                    if save_edit:
                        ok, msg = update_custom_rule(rid, {
                            "name": e_name, "category": e_cat, "severity": e_sev,
                            "cc_level": e_lvl, "description": e_desc,
                            "patterns": [p for p in e_pats.splitlines() if p.strip()],
                            "remediation": e_rem, "example_bad": e_bad, "example_good": e_good,
                            "tags": [t.strip() for t in e_tags.split(",") if t.strip()],
                            "s4_impact": e_s4,
                        })
                        if ok:
                            st.success(msg)
                            st.session_state.pop(f"editing_{rid}", None)
                            st.rerun()
                        else:
                            st.error(msg)
                    if cancel_edit:
                        st.session_state.pop(f"editing_{rid}", None)
                        st.rerun()

    # ── Create new custom rule ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Create New Custom Rule")
    st.caption("Custom rules run alongside built-in rules on every analysis. Patterns are Python regex (case-insensitive).")

    with st.form("new_custom_rule", clear_on_submit=True):
        r1, r2 = st.columns(2)
        nr_id   = r1.text_input("Rule ID", placeholder="CX-001 (auto-generated if blank)")
        nr_name = r2.text_input("Rule Name *", placeholder="e.g. Hardcoded Mandate Code")

        r3, r4 = st.columns(2)
        nr_cat  = r3.selectbox("Category *", CATEGORIES)
        nr_sev  = r4.selectbox("Severity *", SEVERITIES, index=2)

        r5, r6  = st.columns(2)
        nr_lvl  = r5.selectbox("Clean Core Level", CC_LEVELS)
        nr_s4   = r6.checkbox("S/4HANA Impact")

        nr_desc = st.text_area("Description *",
                               placeholder="Explain what this rule detects and why it matters.",
                               height=80)
        nr_pats = st.text_area(
            "Detection Patterns — one regex per line *",
            placeholder="CALL TRANSACTION\nSUBMIT.*AND RETURN\nSELECT.*FROM.*MANDT",
            height=120,
        )
        nr_rem  = st.text_area("Remediation Guidance *",
                               placeholder="Replace CALL TRANSACTION with BAPI_... or RAP EML.",
                               height=100)

        r7, r8  = st.columns(2)
        nr_bad  = r7.text_area("Example — Non-Compliant Code",
                               placeholder="CALL TRANSACTION 'VA01' USING lt_bdc.", height=100)
        nr_good = r8.text_area("Example — Compliant Code",
                               placeholder="MODIFY ENTITY i_salesordertp ...", height=100)

        nr_tags = st.text_input("Tags (comma-separated)",
                                placeholder="ABAP-Cloud, RAP, BAdI")

        nr_sub  = st.form_submit_button("Create Rule", type="primary", use_container_width=True)

    if nr_sub:
        patterns = [p.strip() for p in nr_pats.splitlines() if p.strip()]
        ok, msg = create_custom_rule({
            "id":           nr_id,
            "name":         nr_name,
            "category":     nr_cat,
            "severity":     nr_sev,
            "cc_level":     nr_lvl,
            "s4_impact":    nr_s4,
            "description":  nr_desc,
            "patterns":     patterns,
            "remediation":  nr_rem,
            "example_bad":  nr_bad,
            "example_good": nr_good,
            "tags":         [t.strip() for t in nr_tags.split(",") if t.strip()],
            "enabled":      True,
            "created_by":   user.full_name,
        })
        if ok: st.success(f"✅ {msg}"); st.rerun()
        else:  st.error(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — System Info
# ═══════════════════════════════════════════════════════════════════════════════
with tab_system:
    all_users = load_users()
    from core.abap_rules import ALL_RULES

    st.markdown("### Platform Statistics")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Users",        len(all_users))
    s2.metric("Active Users",       sum(1 for u in all_users if u.active))
    s3.metric("Total Analyses",     sum(u.analyses_run for u in all_users))
    s4.metric("Built-in Rules",     len(ALL_RULES))

    st.markdown("---")

    with st.expander("Audit Log (Session)", expanded=False):
        st.markdown(f"- Current user: **{user.full_name}** (`{user.role}`)")
        st.markdown(f"- Session started: `{st.session_state.get('cv_user', {}).get('last_login', 'N/A')}`")
        st.markdown(f"- LLM configured: **{st.session_state.get('cv_llm_display', 'No')}**")
        st.markdown(f"- Analyses this session: **{user.analyses_run}**")

    with st.expander("Change My Password", expanded=False):
        with st.form("change_pass"):
            old_pass  = st.text_input("Current Password", type="password")
            new_pass  = st.text_input("New Password",     type="password")
            new_pass2 = st.text_input("Confirm",          type="password")
            if st.form_submit_button("Change Password", type="primary"):
                from core.auth import verify_password, get_user
                current = get_user(user.username)
                if not verify_password(old_pass, current.password_hash):
                    st.error("Current password is incorrect.")
                elif new_pass != new_pass2:
                    st.error("New passwords do not match.")
                elif len(new_pass) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    ok, msg = update_user(user.id, password=new_pass)
                    if ok:
                        st.success("Password changed. Please sign in again.")
                        from core.auth import logout
                        logout()

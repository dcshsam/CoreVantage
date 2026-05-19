"""
CodeVantage — Analytics & Executive Dashboard
Visualises compliance trends, violation distributions, and migration readiness.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.auth import require_auth
from core.ui import inject_css, page_header, sidebar_nav, metric_row

st.set_page_config(page_title="Analytics — CodeVantage", page_icon="📊", layout="wide")
inject_css()
user = require_auth()
sidebar_nav(user)

page_header(
    "📊 Analytics & Compliance Dashboard",
    "Executive view of your SAP Clean Core and S/4HANA migration readiness landscape",
)

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    st.warning("Install `plotly` for interactive charts: `pip install plotly`")

# ── Session data ──────────────────────────────────────────────────────────────
cc_result  = st.session_state.get("cv_cc_result")
s4_result  = st.session_state.get("cv_s4_result")
has_data   = bool(cc_result or s4_result)

if not has_data:
    st.info("📊 No analysis data yet. Run **Clean Core** or **S/4 Migration** analysis first, then return here for visualisations.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Clean Core Analysis", type="primary", use_container_width=True):
            st.switch_page("pages/2_🧹_Clean_Core.py")
    with col2:
        if st.button("Go to S/4 Migration Analysis", type="primary", use_container_width=True):
            st.switch_page("pages/3_🚀_S4_Migration.py")
    st.stop()

# ── Summary KPIs ──────────────────────────────────────────────────────────────
kpis = []
if cc_result:
    kpis += [
        {"label": "Clean Core Level",       "value": f"Level {cc_result.clean_core_level}", "color": "#0176D3"},
        {"label": "Total CC Violations",    "value": str(cc_result.total_violations),        "color": "#A33700"},
        {"label": "Lines Analysed (CC)",    "value": f"{cc_result.total_lines:,}",           "color": "#2E844A"},
    ]
if s4_result:
    kpis += [
        {"label": "S/4 Readiness Score",    "value": f"{s4_result.readiness_score}/100",    "color": s4_result.score_color()},
        {"label": "Migration Effort",       "value": f"{s4_result.effort_days}d",            "color": "#7B2D8B"},
    ]
metric_row(kpis[:5])
st.markdown("---")

# ── Charts ────────────────────────────────────────────────────────────────────
if HAS_PLOTLY:
    col1, col2 = st.columns(2)

    if cc_result and cc_result.violations:
        with col1:
            st.markdown("#### Violations by Severity")
            sev_counts = {}
            for v in cc_result.violations:
                sev_counts[v.severity] = sev_counts.get(v.severity, 0) + 1

            sev_colors = {
                "CRITICAL": "#BA0517", "HIGH": "#A33700",
                "MEDIUM":   "#7A5600", "LOW":  "#0176D3", "INFO": "#706E6B",
            }
            labels = list(sev_counts.keys())
            values = list(sev_counts.values())
            colors = [sev_colors.get(s, "#888") for s in labels]

            fig = go.Figure(data=[go.Pie(
                labels=labels, values=values,
                marker=dict(colors=colors),
                hole=0.45,
                textinfo="label+percent",
            )])
            fig.update_layout(
                showlegend=True, height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white", plot_bgcolor="white",
                legend=dict(font=dict(size=11)),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Violations by Category")
            cat_counts = {}
            for v in cc_result.violations:
                cat_counts[v.category] = cat_counts.get(v.category, 0) + 1

            cat_colors = {
                "CLEAN_CORE":   "#0176D3",
                "S4_MIGRATION": "#A33700",
                "SECURITY":     "#BA0517",
                "PERFORMANCE":  "#2E844A",
            }
            fig2 = go.Figure(data=[go.Bar(
                x=list(cat_counts.keys()),
                y=list(cat_counts.values()),
                marker_color=[cat_colors.get(c, "#888") for c in cat_counts.keys()],
                text=list(cat_counts.values()),
                textposition="outside",
            )])
            fig2.update_layout(
                height=300, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white", plot_bgcolor="white",
                xaxis=dict(tickfont=dict(size=11)),
                yaxis_title="Count",
            )
            st.plotly_chart(fig2, use_container_width=True)

    if cc_result and cc_result.violations:
        st.markdown("#### Top Violated Rules")
        rule_counts = {}
        for v in cc_result.violations:
            key = f"[{v.rule_id}] {v.rule.name}"
            rule_counts[key] = rule_counts.get(key, 0) + 1

        top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        rules_df = pd.DataFrame(top_rules, columns=["Rule", "Count"])

        fig3 = px.bar(rules_df, x="Count", y="Rule", orientation="h",
                      color="Count", color_continuous_scale=["#E8F4FF", "#BA0517"],
                      height=max(300, len(top_rules) * 35 + 80))
        fig3.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_showscale=False,
            yaxis=dict(tickfont=dict(size=11)),
        )
        st.plotly_chart(fig3, use_container_width=True)

    if s4_result:
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### Migration Readiness Gauge")
            score = s4_result.readiness_score
            fig4 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                gauge=dict(
                    axis=dict(range=[0, 100]),
                    bar=dict(color=s4_result.score_color()),
                    steps=[
                        dict(range=[0,  50], color="#FFEAEA"),
                        dict(range=[50, 80], color="#FFF8E0"),
                        dict(range=[80,100], color="#E8F5E9"),
                    ],
                    threshold=dict(line=dict(color="black", width=3), value=80),
                ),
                title=dict(text="S/4HANA Readiness Score"),
                number=dict(suffix="/100", font=dict(size=32)),
            ))
            fig4.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20),
                                paper_bgcolor="white")
            st.plotly_chart(fig4, use_container_width=True)

        with col4:
            st.markdown("#### Migration Effort by Severity")
            from core.abap_rules import SEVERITY_COLORS
            if s4_result.s4_violations:
                effort_data = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
                effort_days = {"CRITICAL": 5, "HIGH": 3, "MEDIUM": 1, "LOW": 0.5}
                for v in s4_result.s4_violations:
                    sev = v.severity if v.severity in effort_data else "LOW"
                    effort_data[sev] += effort_days.get(sev, 1)

                fig5 = go.Figure(data=[go.Bar(
                    x=list(effort_data.keys()),
                    y=list(effort_data.values()),
                    marker_color=[SEVERITY_COLORS.get(s, "#888") for s in effort_data.keys()],
                    text=[f"{v:.1f}d" for v in effort_data.values()],
                    textposition="outside",
                )])
                fig5.update_layout(
                    height=300, yaxis_title="Est. Days",
                    paper_bgcolor="white", plot_bgcolor="white",
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig5, use_container_width=True)

# ── Detailed violations table ─────────────────────────────────────────────────
if cc_result and cc_result.violations:
    st.markdown("---")
    st.markdown("#### 📋 Violations Detail Table")
    import pandas as pd
    df = pd.DataFrame([{
        "Rule ID":    v.rule_id,
        "Severity":   v.severity,
        "Category":   v.category,
        "Line":       v.line_number,
        "Rule Name":  v.rule.name,
        "Code":       v.line_content[:80],
        "Remediation":v.remediation[:120],
    } for v in cc_result.violations])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Severity": st.column_config.TextColumn(width="small"),
            "Line":     st.column_config.NumberColumn(width="small"),
        }
    )

    from core.report_exporter import export_violations_excel
    buf = export_violations_excel(cc_result.violations, cc_result.program_name)
    st.download_button(
        "⬇️ Export Full Violations Table (.xlsx)",
        data=buf,
        file_name="codevantage_violations.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# ── Session Analysis History ───────────────────────────────────────────────────
history = st.session_state.get("cv_analysis_history", [])
if history:
    st.markdown("---")
    st.markdown("#### 🕒 Session Analysis History")

    if HAS_PLOTLY and len(history) > 1:
        import pandas as pd
        hist_df = pd.DataFrame(history)

        col_h1, col_h2 = st.columns(2)

        with col_h1:
            st.markdown("##### Violation Count Over Analyses")
            fig_h = go.Figure()
            for atype in hist_df["type"].unique():
                subset = hist_df[hist_df["type"] == atype].reset_index(drop=True)
                fig_h.add_trace(go.Scatter(
                    x=list(range(1, len(subset) + 1)),
                    y=subset["violations"].tolist(),
                    mode="lines+markers",
                    name=atype,
                    line=dict(width=2),
                ))
            fig_h.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white", plot_bgcolor="white",
                xaxis_title="Analysis #", yaxis_title="Violations",
                legend=dict(font=dict(size=11)),
            )
            st.plotly_chart(fig_h, use_container_width=True)

        with col_h2:
            st.markdown("##### Clean Core Level Distribution")
            level_counts = {}
            for h in history:
                lvl = h.get("level", "?")
                level_counts[lvl] = level_counts.get(lvl, 0) + 1
            lv_colors = {"A": "#2E844A", "B": "#0176D3", "C": "#7A5600", "D": "#BA0517", "?": "#888"}
            fig_lv = go.Figure(data=[go.Pie(
                labels=list(level_counts.keys()),
                values=list(level_counts.values()),
                marker=dict(colors=[lv_colors.get(k, "#888") for k in level_counts]),
                hole=0.4,
                textinfo="label+value",
            )])
            fig_lv.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="white", showlegend=False,
            )
            st.plotly_chart(fig_lv, use_container_width=True)

    # History table
    import pandas as pd
    rows = []
    for i, h in enumerate(reversed(history), 1):
        rows.append({
            "#":           len(history) - i + 1,
            "Time":        h.get("timestamp", "—"),
            "Type":        h.get("type", "—"),
            "Program":     h.get("program_name", "—"),
            "Level":       h.get("level", "—"),
            "Violations":  h.get("violations", 0),
            "Lines":       h.get("lines", 0),
            "Score/Effort": f"{h['score']}/100" if "score" in h else f"{h.get('effort', '—')}d" if "effort" in h else "—",
        })
    hist_display = pd.DataFrame(rows)
    st.dataframe(hist_display, use_container_width=True, hide_index=True)

    if st.button("🗑️ Clear History"):
        st.session_state.pop("cv_analysis_history", None)
        st.rerun()

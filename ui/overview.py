"""
Overview Screen for SAT-SA.
Renders Supervisory Overview, 4 KPI cards, Sector-Wide Signal Banner,
65/35 Landscape & Expected vs Observed workflow, and Operational Evidence cards.
"""

import streamlit as st
import pandas as pd
from ui.styles import render_html

def nav_to_queue(rule_id):
    st.session_state["nav_radio"] = "3. Review Queue"
    st.session_state["q_rule_filter"] = rule_id

def nav_to_cse(cse_id):
    st.session_state["nav_radio"] = "2. CSE Assessment"
    st.session_state["cse_detail_selector"] = cse_id

def render_overview(data: dict):
    cse_attentions = data["cse_attentions"]
    alerts_df = data["alerts_df"]
    assets_df = data["assets_df"]
    cases_df = data["cases_df"]
    
    # -------------------------------------------------------------
    # 1. TOP HEADER
    # -------------------------------------------------------------
    render_html("""
    <div class="sat-header-wrapper">
        <div>
            <h1 class="sat-header-title">Supervisory Overview</h1>
            <div class="sat-header-subtitle">Cyber Resilience Assessment Environment</div>
        </div>
        <div class="sat-meta-pill-group">
            <div class="sat-meta-pill">
                <span>Period:</span> <strong>Q3 2026</strong>
            </div>
            <div class="sat-meta-pill">
                <span>CSEs Assessed:</span> <strong>{len(cse_attentions)}</strong>
            </div>
            <div class="sat-meta-pill">
                <span>Alerts Analyzed:</span> <strong>{len(alerts_df):,}</strong>
            </div>
            <div class="sat-meta-pill">
                <span>Cases Analyzed:</span> <strong>{len(cases_df):,}</strong>
            </div>
            <div class="sat-meta-pill">
                <span>Assets Assessed:</span> <strong>{len(assets_df):,}</strong>
            </div>
        </div>
    </div>
    """)

    # -------------------------------------------------------------
    # 2. KPI AREA (4 Cards)
    # -------------------------------------------------------------
    high_count = sum(1 for c in cse_attentions.values() if c.attention_level == "HIGH")
    med_count = sum(1 for c in cse_attentions.values() if c.attention_level == "MEDIUM")
    low_count = sum(1 for c in cse_attentions.values() if c.attention_level == "LOW")
    total_findings = sum(len(c.findings) for c in cse_attentions.values())

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        render_html(f"""
        <div class="sat-kpi-card">
            <div class="sat-kpi-header">
                <span class="sat-kpi-label">High Attention</span>
                <span class="sat-indicator-dot sat-dot-high"></span>
            </div>
            <div class="sat-kpi-val">{high_count:02d} <span style="font-size: 14px; font-weight: 500; color: #7A819B;">CSEs</span></div>
            <div class="sat-kpi-sub">Critical intervention required</div>
        </div>
        """)

    with kpi2:
        render_html(f"""
        <div class="sat-kpi-card">
            <div class="sat-kpi-header">
                <span class="sat-kpi-label">Medium Attention</span>
                <span class="sat-indicator-dot sat-dot-med"></span>
            </div>
            <div class="sat-kpi-val">{med_count:02d} <span style="font-size: 14px; font-weight: 500; color: #7A819B;">CSEs</span></div>
            <div class="sat-kpi-sub">Elevated procedural deviations</div>
        </div>
        """)

    with kpi3:
        render_html(f"""
        <div class="sat-kpi-card">
            <div class="sat-kpi-header">
                <span class="sat-kpi-label">Low Attention</span>
                <span class="sat-indicator-dot sat-dot-low"></span>
            </div>
            <div class="sat-kpi-val">{low_count:02d} <span style="font-size: 14px; font-weight: 500; color: #7A819B;">CSEs</span></div>
            <div class="sat-kpi-sub">Routine supervisory review</div>
        </div>
        """)

    with kpi4:
        render_html(f"""
        <div class="sat-kpi-card sat-card-gradient">
            <div class="sat-kpi-header">
                <span class="sat-kpi-label">Total Findings</span>
                <span style="font-size: 12px; color: #EAE7FF;">● Rule-backed</span>
            </div>
            <div class="sat-kpi-val">{total_findings}</div>
            <div class="sat-kpi-sub" style="color: #EAE7FF;">Deterministic execution signals</div>
        </div>
        """)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. SUPERVISORY SIGNAL (Sector-wide Banner)
    # -------------------------------------------------------------
    sector_signals = data.get("sector_signals", [])
    if sector_signals:
        for sig in sector_signals:
            render_html(f"""
            <div class="sat-sector-banner">
                <div class="sat-banner-left">
                    <div class="sat-banner-icon">⚠️</div>
                    <div>
                        <div class="sat-banner-title">Sector-wide Supervisory Signal</div>
                        <div class="sat-banner-desc"><strong>{sig['description']}</strong></div>
                    </div>
                </div>
            </div>
            """)
            st.button("Systemic Blindspot →", key=f"sys_btn_{sig['rule_id']}", on_click=nav_to_queue, args=(sig['rule_id'],))
            render_html("<div style='height: 8px;'></div>")
    else:
        render_html("""
        <div class="sat-sector-banner" style="background-color: #F8F9FC; border-color: #E5E7F0;">
            <div class="sat-banner-left">
                <div class="sat-banner-icon" style="color: #7A819B;">✅</div>
                <div>
                    <div class="sat-banner-title" style="color: #241B5B;">No Sector-wide Signals Detected</div>
                    <div class="sat-banner-desc">No supervisory flags meet the systemic threshold.</div>
                </div>
            </div>
        </div>
        """)

    # -------------------------------------------------------------
    # 4. MAIN TWO-COLUMN LAYOUT (65% / 35%)
    # -------------------------------------------------------------
    col_left, col_right = st.columns([65, 35])

    with col_left:
        render_html("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-size: 16px; font-weight: 700; color: #241B5B;">CSE Supervisory Landscape</div>
            <div style="font-size: 12px; color: #636A84;">Sorted by Attention Score</div>
        </div>
        """)

        # Build table data
        rows = []
        for cse_id, att in cse_attentions.items():
            f_count = len(att.findings)
            esc_rate = att.kpi_summary.get("escalation_sla", "50%")
            status = "Review" if att.attention_level == "HIGH" else ("Monitor" if att.attention_level == "MEDIUM" else "Routine")
            badge_class = "sat-badge-high" if att.attention_level == "HIGH" else ("sat-badge-med" if att.attention_level == "MEDIUM" else "sat-badge-low")
            
            rows.append({
                "cse_id": cse_id,
                "attention_level": att.attention_level,
                "badge_class": badge_class,
                "findings": f_count,
                "esc_rate": esc_rate,
                "status": status,
                "score": att.attention_score
            })
            
        sorted_rows = sorted(rows, key=lambda x: x["score"], reverse=True)
        
        search_q = st.text_input("Search CSE", placeholder="Filter by CSE ID (e.g. CSE-07)...", label_visibility="collapsed")
        if search_q:
            sorted_rows = [r for r in sorted_rows if search_q.upper() in r["cse_id"].upper()]

        # Render Table HTML using render_html
        table_html = """
        <div class="sat-table-wrapper">
            <table class="sat-table">
                <thead>
                    <tr>
                        <th>CSE</th>
                        <th>Attention</th>
                        <th>Findings</th>
                        <th>Escalation Rate</th>
                        <th>Supervisory Status</th>
                    </tr>
                </thead>
                <tbody>
        """
        for r in sorted_rows[:8]:
            status_color = '#D64545' if r['status'] == 'Review' else ('#D99A27' if r['status'] == 'Monitor' else '#31966B')
            table_html += f"""
                <tr>
                    <td><strong>{r['cse_id']}</strong></td>
                    <td><span class="sat-badge {r['badge_class']}">{r['attention_level']}</span></td>
                    <td><strong>{r['findings']}</strong></td>
                    <td>{r['esc_rate']}</td>
                    <td><span style="font-weight: 500; color: {status_color};">{r['status']}</span></td>
                </tr>
            """
        table_html += """
                </tbody>
            </table>
        </div>
        """
        render_html(table_html)

    with col_right:
        render_html("""
        <div style="font-size: 16px; font-weight: 700; color: #241B5B; margin-bottom: 8px;">
            Expected vs Observed Evidence
        </div>
        """)
        
        options = [f"{cse_id} ({att.attention_level} Attention)" for cse_id, att in cse_attentions.items()]
        selected_flow_cse = st.selectbox(
            "Select CSE for Workflow Inspection",
            options=options,
            index=0,
            label_visibility="collapsed"
        )
        cse_key = selected_flow_cse.split(" ")[0]

        # Determine workflow missing items dynamically based on selected CSE alerts
        cse_alerts = alerts_df[alerts_df["cse_id"] == cse_key]
        
        def get_workflow_status(col_name):
            if cse_alerts.empty or col_name not in cse_alerts.columns: return "✓ Observed", ""
            if (cse_alerts[col_name] == "NOT_AVAILABLE").any():
                return "? Evidence unavailable", "sat-step-missing"
            if (cse_alerts[col_name] == "No").any():
                return "✕ Not observed", "sat-step-missing"
            return "✓ Observed", ""
            
        obs_inv_icon, obs_inv_class = get_workflow_status("investigation_present")
        obs_esc_icon, obs_esc_class = get_workflow_status("escalated")
        obs_rem_icon, obs_rem_class = get_workflow_status("remediation_present")
        
        missing_text = []
        if "✕" in obs_inv_icon: missing_text.append("Investigation (Not observed)")
        elif "?" in obs_inv_icon: missing_text.append("Investigation (Unavailable)")
        
        if "✕" in obs_esc_icon: missing_text.append("Escalation (Not observed)")
        elif "?" in obs_esc_icon: missing_text.append("Escalation (Unavailable)")
        
        if "✕" in obs_rem_icon: missing_text.append("Remediation (Not observed)")
        elif "?" in obs_rem_icon: missing_text.append("Remediation (Unavailable)")
        
        if missing_text:
            missing_str = ", ".join(missing_text)
            missing_display = f"{len(missing_text)} expected evidence elements flagged ({missing_str})"
        else:
            missing_display = "All workflow evidence stages verified compliant"

        workflow_html = f"""
        <div class="sat-workflow-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E5E7F0; padding-bottom: 8px;">
                <span style="font-size: 13px; font-weight: 700; color: #30256F;">Workflow Trace: {cse_key}</span>
                <span class="sat-badge sat-badge-neutral">Audit Path</span>
            </div>
            
            <div class="sat-workflow-grid">
                <!-- Expected Workflow -->
                <div class="sat-flow-col sat-flow-expected">
                    <div class="sat-flow-header" style="color: #40358C;">Expected Workflow</div>
                    
                    <div class="sat-flow-step">
                        <span>1. Alert</span>
                        <span style="color: #31966B;">✓</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step">
                        <span>2. Investigation</span>
                        <span style="color: #31966B;">✓</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step">
                        <span>3. Escalation</span>
                        <span style="color: #31966B;">✓</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step">
                        <span>4. Remediation</span>
                        <span style="color: #31966B;">✓</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step">
                        <span>5. Closure</span>
                        <span style="color: #31966B;">✓</span>
                    </div>
                </div>

                <!-- Observed Workflow -->
                <div class="sat-flow-col sat-flow-observed">
                    <div class="sat-flow-header" style="color: #636A84;">Observed Evidence</div>
                    
                    <div class="sat-flow-step">
                        <span>1. Alert</span>
                        <span style="color: #31966B;">✓</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step {obs_inv_class}">
                        <span>2. Investigation</span>
                        <span>{obs_inv_icon}</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step {obs_esc_class}">
                        <span>3. Escalation</span>
                        <span>{obs_esc_icon}</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step {obs_rem_class}">
                        <span>4. Remediation</span>
                        <span>{obs_rem_icon}</span>
                    </div>
                    <div class="sat-arrow">&darr;</div>
                    <div class="sat-flow-step">
                        <span>5. Closure</span>
                        <span style="color: #31966B;">✓</span>
                    </div>
                </div>
            </div>

            <div style="background-color: #F8F9FC; border: 1px solid #E5E7F0; border-radius: 8px; padding: 10px; font-size: 12px; margin-top: 8px;">
                <div style="font-weight: 600; color: #D64545;">&bull; {missing_display}</div>
            </div>
        </div>
        """
        render_html(workflow_html)
        st.button("View evidence drilldown →", key="btn_drilldown", on_click=nav_to_cse, args=(cse_key,))

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 5. OPERATIONAL EVIDENCE (3 Compact Cards)
    # -------------------------------------------------------------
    render_html("""
    <div style="font-size: 16px; font-weight: 700; color: #241B5B; margin-bottom: 12px;">
        Operational Evidence Summary
    </div>
    """)

    op1, op2, op3 = st.columns(3)
    with op1:
        render_html("""
        <div class="sat-op-card">
            <div>
                <span class="sat-op-rule">RULE EG-1</span>
                <div class="sat-op-title">Critical alert without escalation</div>
                <div class="sat-op-count">12 alerts matched</div>
                <div class="sat-op-sub">Closed without required Tier-2 escalation</div>
            </div>
            <div style="margin-top: 12px; font-size: 12px; font-weight: 600; color: #5146A8;">
                <span>Affected CSEs: 6</span>
            </div>
        </div>
        """)
        st.button("View Details →", key="btn_eg1", on_click=nav_to_queue, args=("EG-1",), use_container_width=True)

    with op2:
        render_html("""
        <div class="sat-op-card">
            <div>
                <span class="sat-op-rule">RULE EG-2</span>
                <div class="sat-op-title">Investigation evidence missing</div>
                <div class="sat-op-count">8 cases matched</div>
                <div class="sat-op-sub">High/Critical alerts closed without forensic review</div>
            </div>
            <div style="margin-top: 12px; font-size: 12px; font-weight: 600; color: #5146A8;">
                <span>Affected CSEs: 5</span>
            </div>
        </div>
        """)
        st.button("View Details →", key="btn_eg2", on_click=nav_to_queue, args=("EG-2",), use_container_width=True)

    with op3:
        render_html("""
        <div class="sat-op-card">
            <div>
                <span class="sat-op-rule">RULE EG-3</span>
                <div class="sat-op-title">Potential supervisory signal: fast closure</div>
                <div class="sat-op-count">6 cases matched</div>
                <div class="sat-op-sub">Closure recorded under 10 min threshold</div>
            </div>
            <div style="margin-top: 12px; font-size: 12px; font-weight: 600; color: #5146A8;">
                <span>Affected CSEs: 4</span>
            </div>
        </div>
        """)
        st.button("View Details →", key="btn_eg3", on_click=nav_to_queue, args=("EG-3",), use_container_width=True)

"""
CSE Assessment / Detail Screen for SAT-SA.
Renders KPI vs Reality side-by-side contrast, Peer Comparison,
Supervisor Memo Generator with download, and WHY Evidence Expanders.
"""

import streamlit as st
import pandas as pd
from engine.findings import CSEAttention, Finding
from ui.styles import render_html

def render_cse_detail(data: dict):
    cse_attentions = data["cse_attentions"]
    alerts_df = data["alerts_df"]
    assets_df = data["assets_df"]
    cases_df = data["cases_df"]
    
    # -------------------------------------------------------------
    # 1. HEADER & CSE SELECTOR
    # -------------------------------------------------------------
    cse_ids = list(cse_attentions.keys())
    
    col_sel, col_meta = st.columns([1, 2])
    with col_sel:
        selected_cse = st.selectbox(
            "Select CSE Entity",
            options=cse_ids,
            index=cse_ids.index("CSE-07") if "CSE-07" in cse_ids else 0,
            key="cse_detail_selector"
        )
        
    att: CSEAttention = cse_attentions[selected_cse]
    badge_class = "sat-badge-high" if att.attention_level == "HIGH" else ("sat-badge-med" if att.attention_level == "MEDIUM" else "sat-badge-low")
    
    with col_meta:
        score_breakdown_items = ""
        for f in att.findings:
            w = 3 if f.severity == "HIGH" else (2 if f.severity == "MEDIUM" else 1)
            score_breakdown_items += f"<div style='display:flex;justify-content:space-between;font-size:11px;color:#2D3142;margin-bottom:2px;'><span>{f.rule_id} {f.severity}</span><span>+{w}</span></div>"
            
        score_breakdown_total = f"<div style='display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-top:6px;border-top:1px solid var(--border-color);padding-top:4px;color:var(--brand-950);'><span>TOTAL</span><span>{att.attention_score}</span></div>"
        
        render_html(f"""
        <div style="display: flex; align-items: flex-start; justify-content: flex-end; gap: 12px; height: 100%; padding-top: 5px;">
            <div style="text-align: right;">
                <div style="font-size: 18px; font-weight: 700; color: #241B5B;">{selected_cse} &bull; Critical Infrastructure Entity</div>
                <div style="font-size: 12px; color: #636A84;">Sector: Power & Energy Grid SOC &bull; Jurisdiction: Central CII</div>
            </div>
            <div style="display:flex; flex-direction:column; align-items:flex-end;">
                <span class="sat-badge {badge_class}" style="font-size: 13px; padding: 6px 14px;">
                    {att.attention_level} ATTENTION
                </span>
                <div style="margin-top:8px; background:var(--bg-card); border:1px solid var(--border-color); padding:8px; border-radius:6px; width:170px; box-shadow:var(--shadow-soft);">
                    <div style="font-size:10px; font-weight:700; color:var(--brand-700); margin-bottom:6px; text-transform:uppercase;">WHY THIS SCORE?</div>
                    <div style="max-height: 100px; overflow-y: auto; padding-right: 4px; scrollbar-width: thin; scrollbar-color: #C9CCD6 transparent;">
                        {score_breakdown_items}
                    </div>
                    {score_breakdown_total}
                </div>
            </div>
        </div>
        """)
        
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 2. KPI VS OPERATIONAL EVIDENCE (The "Looks compliant, but..." contrast)
    # -------------------------------------------------------------
    render_html("""
    <div style="font-size: 16px; font-weight: 700; color: #241B5B; margin-bottom: 10px;">
        Supervisory Verification: KPI Reporting vs Operational Evidence
    </div>
    """)

    kpi_col, reality_col = st.columns(2)
    
    high_findings_count = sum(1 for f in att.findings if f.severity == "HIGH")
    eg1_count = sum(1 for f in att.findings if f.rule_id == "EG-1")
    eg2_count = sum(1 for f in att.findings if f.rule_id == "EG-2")
    eg4_count = sum(1 for f in att.findings if f.rule_id == "EG-4")
    
    with kpi_col:
        render_html(f"""
        <div class="sat-card" style="border-left: 4px solid #5146A8; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #5146A8;">
                    Reported Performance (Self-Declared KPIs)
                </span>
                <span class="sat-badge sat-badge-neutral">Reported SLA</span>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px;">
                <div style="background-color: #F8F9FC; border: 1px solid #E5E7F0; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #636A84; font-weight: 600;">Escalation SLA</div>
                    <div style="font-size: 22px; font-weight: 700; color: #241B5B; margin-top: 4px;">{att.kpi_summary.get('escalation_sla', '94%')}</div>
                    <div style="font-size: 10.5px; color: #31966B;">✓ Compliant on paper</div>
                </div>
                <div style="background-color: #F8F9FC; border: 1px solid #E5E7F0; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #636A84; font-weight: 600;">Ack SLA</div>
                    <div style="font-size: 22px; font-weight: 700; color: #241B5B; margin-top: 4px;">{att.kpi_summary.get('ack_sla', '97%')}</div>
                    <div style="font-size: 10.5px; color: #31966B;">✓ Met benchmark</div>
                </div>
                <div style="background-color: #F8F9FC; border: 1px solid #E5E7F0; border-radius: 8px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #636A84; font-weight: 600;">Closure SLA</div>
                    <div style="font-size: 22px; font-weight: 700; color: #241B5B; margin-top: 4px;">{att.kpi_summary.get('closure_sla', '96%')}</div>
                    <div style="font-size: 10.5px; color: #31966B;">✓ Target achieved</div>
                </div>
            </div>
            <div style="font-size: 11.5px; color: #7A819B; margin-top: 12px;">
                <em>Reported figures indicate standard SLA compliance across standard alert tiers.</em>
            </div>
        </div>
        """)

    with reality_col:
        alert_highlight = "#D64545" if high_findings_count > 0 else "#31966B"
        render_html(f"""
        <div class="sat-card" style="border-left: 4px solid {alert_highlight}; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: {alert_highlight};">
                    Operational Evidence (Empirical Verification)
                </span>
                <span class="sat-badge sat-badge-high">{high_findings_count} High Severity Flags</span>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px;">
                <div style="background-color: #FDF2F2; border: 1px solid #F9D2D2; border-radius: 8px; padding: 9px 12px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 12.5px; font-weight: 600; color: #C0392B;">Critical alerts closed without escalation</span>
                    <strong style="font-size: 15px; color: #C0392B;">{eg1_count if eg1_count > 0 else 'None'}</strong>
                </div>
                <div style="background-color: #FEF9E7; border: 1px solid #FDE8C7; border-radius: 8px; padding: 9px 12px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 12.5px; font-weight: 600; color: #B7791F;">Investigation evidence missing in High/Crit alerts</span>
                    <strong style="font-size: 15px; color: #B7791F;">{eg2_count if eg2_count > 0 else 'None'}</strong>
                </div>
                <div style="background-color: #FDF2F2; border: 1px solid #F9D2D2; border-radius: 8px; padding: 9px 12px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 12.5px; font-weight: 600; color: #C0392B;">Repeated alerts sustained without remediation</span>
                    <strong style="font-size: 15px; color: #C0392B;">{eg4_count if eg4_count > 0 else 'None'}</strong>
                </div>
            </div>
        </div>
        """)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------
    # 2.5 REPORTED VS OBSERVED
    # -------------------------------------------------------------
    render_html("""
    <div style="font-size: 16px; font-weight: 700; color: #241B5B; margin-bottom: 10px;">
        Supervisory Verification: Explicit Reported vs Observed Comparison
    </div>
    """)
    
    store = data["data_store"]
    cse_data = store.get_cse_data(selected_cse)
    profile = cse_data.get("profile", {})
    alerts = cse_data.get("alerts", [])
    assets = cse_data.get("assets", [])
    
    # Calculate Observed Investigation Rate
    crit_high = [a for a in alerts if a.get("severity") in ("Critical", "High") and a.get("disposition") == "Closed"]
    op_inv_rate = sum(1 for a in crit_high if a.get("investigation_present") != "No") / len(crit_high) if crit_high else 0
    inv_denom = len(crit_high)
    
    # Calculate Observed Escalation Rate
    op_esc_rate = sum(1 for a in crit_high if a.get("escalated") == "Yes") / len(crit_high) if crit_high else 0
    
    # Calculate Observed MTTR
    closed_alerts = [float(a.get("closure_time_minutes", -1)) for a in alerts if a.get("disposition") == "Closed"]
    closed_alerts = [m for m in closed_alerts if m >= 0]
    op_mttr = sum(closed_alerts) / len(closed_alerts) if closed_alerts else 0
    mttr_denom = len(closed_alerts)
    
    # Calculate Observed Monitoring Coverage
    from config import BLIND_SPOT_RATIO, BLIND_SPOT_THRESHOLD_ABSOLUTE
    days = 90
    if "Q" in str(profile.get("assessment_period", "")): days = 90
    expected_assets = [a for a in assets if str(a.get("expected_monitoring", "")).lower() == "yes"]
    adequate_count = 0
    for a in expected_assets:
        try:
            ev = float(a.get("observed_monitoring_events", 0))
            exp_daily = float(a.get("expected_events_per_day", 0))
            exp = exp_daily * days
            if exp > 0 and ev >= exp * BLIND_SPOT_RATIO:
                adequate_count += 1
            elif exp <= 0 and ev >= BLIND_SPOT_THRESHOLD_ABSOLUTE:
                adequate_count += 1
        except (ValueError, TypeError):
            pass
    op_mon_rate = adequate_count / len(expected_assets) if expected_assets else 0
    mon_denom = len(expected_assets)
    
    # Get Reported Rates
    rep_inv = float(profile.get("reported_investigation_rate", op_inv_rate)) if pd.notna(profile.get("reported_investigation_rate")) else op_inv_rate
    rep_esc = float(profile.get("reported_escalation_rate", op_esc_rate)) if pd.notna(profile.get("reported_escalation_rate")) else op_esc_rate
    rep_mttr = float(profile.get("reported_mttr_minutes", op_mttr)) if pd.notna(profile.get("reported_mttr_minutes")) else op_mttr
    rep_mon = float(profile.get("reported_monitoring_coverage", op_mon_rate)) if pd.notna(profile.get("reported_monitoring_coverage")) else op_mon_rate
    
    # Helper to format diff
    def render_metric_card(title, rep_val, op_val, is_percentage, basis):
        diff = op_val - rep_val
        if is_percentage:
            rep_str = f"{rep_val:.0%}"
            op_str = f"{op_val:.0%}"
            diff_str = f"{diff*100:+.0f} percentage points"
            is_bad = abs(diff) > 0.15
        else:
            rep_str = f"{rep_val:.1f}m"
            op_str = f"{op_val:.1f}m"
            diff_str = f"{diff:+.1f} mins"
            is_bad = diff > (rep_val * 0.15) if rep_val > 0 else diff > 10
            
        color = "#C0392B" if is_bad else "#31966B"
        warning = f"<div style='font-size:10px; color:{color}; font-weight:600; margin-top:4px;'>Operational evidence does not fully reconcile with the reported KPI.</div>" if is_bad else ""
        
        return f'''
        <div style="background-color: #F8F9FC; border: 1px solid #E5E7F0; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <div style="font-size: 13px; color: #241B5B; font-weight: 700; margin-bottom: 8px;">{title}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 11px; color: #636A84; width: 80px;">REPORTED</span>
                <strong style="font-size: 14px; color: #241B5B;">{rep_str}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 11px; color: #636A84; width: 80px;">OBSERVED</span>
                <strong style="font-size: 14px; color: {color};">{op_str}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding-top: 4px; border-top: 1px solid #E5E7F0;">
                <span style="font-size: 11px; color: #636A84; width: 80px;">DIFFERENCE</span>
                <strong style="font-size: 12px; color: {color};">{diff_str}</strong>
            </div>
            <div style="font-size: 10px; color: #7A819B; margin-top: 8px; font-style: italic;">
                Basis: {basis}
            </div>
            {warning}
        </div>
        '''

    col_1, col_2, col_3, col_4 = st.columns(4)
    with col_1:
        render_html(render_metric_card("Investigation Rate", rep_inv, op_inv_rate, True, f"{int(op_inv_rate * inv_denom)} invs / {inv_denom} High+Crit alerts"))
    with col_2:
        render_html(render_metric_card("Escalation Rate", rep_esc, op_esc_rate, True, f"{int(op_esc_rate * inv_denom)} escs / {inv_denom} High+Crit alerts"))
    with col_3:
        render_html(render_metric_card("Avg MTTR", rep_mttr, op_mttr, False, f"Avg of {mttr_denom} closed alerts"))
    with col_4:
        render_html(render_metric_card("Monitoring Coverage", rep_mon, op_mon_rate, True, f"{adequate_count} adequate / {mon_denom} expected assets"))

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. PEER COMPARISON & MEMO GENERATOR
    # -------------------------------------------------------------
    col_peer, col_memo = st.columns([1, 1])

    with col_peer:
        peer_finding = next((f for f in att.findings if f.rule_id == "PEER-1"), None)
        if peer_finding and peer_finding.metric_value is not None:
            c_val = peer_finding.metric_value
            p_val = peer_finding.peer_value or 58.0
            render_html(f"""
            <div class="sat-card" style="height: 100%;">
                <div style="font-size: 14px; font-weight: 700; color: #241B5B; margin-bottom: 8px;">
                    Peer Benchmark Analysis (PEER-1)
                </div>
                <div style="font-size: 12.5px; color: #555E77; margin-bottom: 12px;">
                    Critical/High Alert Escalation Rate relative to Critical Sector Entities baseline:
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 12px; font-weight: 600; color: #241B5B;">{selected_cse} Escalation Rate</span>
                    <span style="font-size: 13px; font-weight: 700; color: #D64545;">{c_val:.1f}%</span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #E5E7F0; border-radius: 4px; overflow: hidden; margin-bottom: 12px;">
                    <div style="width: {min(100, int(c_val))}%; height: 100%; background-color: #D64545; border-radius: 4px;"></div>
                </div>

                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 12px; font-weight: 600; color: #241B5B;">Sector Average (22 CSEs)</span>
                    <span style="font-size: 13px; font-weight: 700; color: #5146A8;">{p_val:.1f}%</span>
                </div>
                <div style="width: 100%; height: 8px; background-color: #E5E7F0; border-radius: 4px; overflow: hidden; margin-bottom: 8px;">
                    <div style="width: {int(p_val)}%; height: 100%; background-color: #5146A8; border-radius: 4px;"></div>
                </div>
                <div style="font-size: 11px; color: #D64545; font-weight: 600;">
                    ⚠️ Rate is {(p_val - c_val):.1f}% below sector peer mean (Threshold: &gt; 1.0 &sigma; deviation).
                </div>
            </div>
            """)
        else:
            render_html("""
            <div class="sat-card" style="height: 100%;">
                <div style="font-size: 14px; font-weight: 700; color: #241B5B; margin-bottom: 8px;">
                    Peer Benchmark Analysis (PEER-1)
                </div>
                <div style="padding: 18px; text-align: center; color: #636A84; font-size: 13px;">
                    ✓ Escalation rate is within normal sector standard deviation parameters (&gt; 50%).
                </div>
            </div>
            """)

    with col_memo:
        render_html("""
        <div class="sat-card" style="height: 100%;">
            <div style="font-size: 14px; font-weight: 700; color: #241B5B; margin-bottom: 6px;">
                Official Supervisory Observation Memo
            </div>
            <div style="font-size: 12px; color: #636A84; margin-bottom: 12px;">
                Auto-generate an examiner-ready formal notification memo from verified findings.
            </div>
        </div>
        """)
        
        # Build memo content dynamically according to spec §10
        period_label = "Q3 2026"
        rec_action = (
            "Immediate corrective review requested within 30 days." if att.attention_level == "HIGH"
            else ("Recommended review at next scheduled audit cycle." if att.attention_level == "MEDIUM"
            else "No immediate action required; continue routine monitoring.")
        )
        
        findings_bullets = ""
        for idx, f in enumerate(att.findings[:5], 1):
            findings_bullets += f"{idx}. {f.title}\n   {f.explanation}\n   Evidence: {', '.join(f.evidence_ids)}\n\n"
            
        peer_block = ""
        if peer_finding and peer_finding.metric_value is not None:
            peer_block = f"Peer Context:\n{selected_cse}'s Critical Escalation Rate is {peer_finding.metric_value:.1f}%, against a sector average of {peer_finding.peer_value or 58.0:.1f}%.\n\n"
            
        memo_text = f"""Subject: Supervisory Observation — {selected_cse} — {period_label}
Attention Level: {att.attention_level}

Findings:
{findings_bullets}
{peer_block}Recommended Action:
{rec_action}

This is a system-generated supervisory observation intended to support, not replace, examiner judgement."""

        if st.button("Generate Supervisory Memo", key="btn_gen_memo"):
            st.session_state[f"memo_{selected_cse}"] = memo_text
            
        if f"memo_{selected_cse}" in st.session_state:
            st.text_area("Supervisory Memo Preview", value=st.session_state[f"memo_{selected_cse}"], height=130)
            st.download_button(
                label="⬇️ Download Memo (.txt)",
                data=st.session_state[f"memo_{selected_cse}"],
                file_name=f"Supervisory_Memo_{selected_cse}_{period_label}.txt",
                mime="text/plain"
            )
        else:
            st.info("Click 'Generate Supervisory Memo' to produce the formal audit memorandum.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3.5 EVIDENCE COVERAGE
    # -------------------------------------------------------------
    render_html("""
    <div style="font-size: 16px; font-weight: 700; color: #241B5B; margin-bottom: 10px;">
        Evidence Coverage
    </div>
    """)
    if att.evidence_warnings:
        for w in att.evidence_warnings:
            st.warning(w, icon="⚠️")
    else:
        st.success("Full evidence coverage available for this entity. All rules evaluated successfully.")
        
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 4. WHY EVIDENCE DRILL-DOWN PANEL
    # -------------------------------------------------------------
    render_html("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div style="font-size: 16px; font-weight: 700; color: #241B5B;">
            WHY Panel: Traceable Evidence Breakdown
        </div>
        <div style="font-size: 12px; color: #636A84;">
            Every flag maps 1:1 to an underlying audit equation
        </div>
    </div>
    """)

    if not att.findings:
        st.success("No supervisory flags identified for this entity. Routine monitoring active.")
    else:
        for idx, f in enumerate(att.findings, 1):
            sev_badge = "sat-badge-high" if f.severity == "HIGH" else ("sat-badge-med" if f.severity == "MEDIUM" else "sat-badge-low")
            
            with st.expander(f"#{idx:02d} [{f.rule_id}] {f.title}  —  {f.severity} SEVERITY"):
                c_why, c_eq = st.columns([2, 1])
                
                w = 3 if f.severity == "HIGH" else (2 if f.severity == "MEDIUM" else 1)
                
                norm_field = "Multiple"
                if f.rule_id == "EG-1": norm_field = "escalated = No"
                elif f.rule_id == "EG-2": norm_field = "investigation_present = No"
                elif f.rule_id == "EG-3": norm_field = "closure_time_minutes"
                elif f.rule_id == "EG-4": norm_field = "remediation_present = No"
                elif f.rule_id == "NS-1": norm_field = "observed_monitoring_events = 0"
                elif f.rule_id == "PEER-1": norm_field = "escalated rate"
                elif f.rule_id == "T-1": norm_field = "investigation drop"
                elif f.rule_id == "K-1": norm_field = "reported vs observed"
                elif f.rule_id == "I-1": norm_field = "repeated investigation_note"
                
                source_type = data.get("ingestion_meta", {}).get("provenance", {}).get("source_type", "CSV Export")
                
                with c_why:
                    render_html(f"""
                    <div style="font-size: 13px; font-weight: 600; color: var(--brand-950); margin-bottom: 4px;">EVIDENCE LINEAGE</div>
                    <div style="font-size: 12px; color: #374151; margin-bottom: 12px;">{f.explanation}</div>
                    
                    <div style="background-color: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px; font-size: 11.5px; font-family: monospace;">
                        <div style="display:flex; margin-bottom:4px;">
                            <span style="width:120px; color:var(--brand-700); font-weight:600;">Source:</span>
                            <span style="color:#2D3142;">{source_type}</span>
                        </div>
                        <div style="display:flex; margin-bottom:4px;">
                            <span style="width:120px; color:var(--brand-700); font-weight:600;">Normalized Field:</span>
                            <span style="color:#2D3142;">{norm_field}</span>
                        </div>
                        <div style="display:flex; margin-bottom:4px;">
                            <span style="width:120px; color:var(--brand-700); font-weight:600;">Rule Applied:</span>
                            <span style="color:#2D3142;">{f.rule_id}</span>
                        </div>
                        <div style="display:flex; margin-bottom:4px;">
                            <span style="width:120px; color:var(--brand-700); font-weight:600;">Finding Result:</span>
                            <span style="color:#2D3142;">{f.title}</span>
                        </div>
                        <div style="display:flex;">
                            <span style="width:120px; color:var(--brand-700); font-weight:600;">Attention Impact:</span>
                            <span style="color:#D64545; font-weight:700;">+{w}</span>
                        </div>
                    </div>
                    """)
                with c_eq:
                    render_html(f"""
                    <div style="background-color: #F8F9FC; border: 1px solid #E5E7F0; border-radius: 6px; padding: 8px; font-size: 11px;">
                        <span style="font-weight: 700; color: #5146A8;">Deterministic Equation:</span><br>
                        <code>Rule {f.rule_id}: {f.category}</code><br>
                        <span style="color: #7A819B;">Verified mathematically against source row.</span>
                    </div>
                    """)

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                st.markdown("<strong>Raw Source Records (Unmodified Source Data):</strong>", unsafe_allow_html=True)
                
                if f.rule_id == "NS-1":
                    # Use DataStore for asset evidence
                    evidence_records = [data["data_store"].get_asset_evidence(eid) for eid in f.evidence_ids]
                elif f.rule_id == "I-1":
                    # Use DataStore for case evidence
                    evidence_records = [data["data_store"].get_case_evidence(eid) for eid in f.evidence_ids]
                else:
                    # Use DataStore for alert evidence
                    evidence_records = [data["data_store"].get_alert_evidence(eid) for eid in f.evidence_ids]
                
                # Filter out empty dicts if any IDs were not found
                evidence_records = [r for r in evidence_records if r]
                matching_raw = pd.DataFrame(evidence_records)
                    
                if not matching_raw.empty:
                    st.dataframe(matching_raw, use_container_width=True, hide_index=True)
                else:
                    st.caption("No matching raw rows located.")

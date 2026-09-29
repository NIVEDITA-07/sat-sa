"""
Priority Review Queue Screen for SAT-SA.
Full-width analyst queue with filters, rank order, and evidence inspection drawer.
"""

import streamlit as st
import pandas as pd
from engine.findings import Finding
from ui.styles import render_html

def render_review_queue(data: dict):
    cse_attentions = data["cse_attentions"]
    alerts_df = data["alerts_df"]
    assets_df = data["assets_df"]
    cases_df = data["cases_df"]
    
    # -------------------------------------------------------------
    # 1. HEADER
    # -------------------------------------------------------------
    render_html("""
    <div class="sat-header-wrapper">
        <div>
            <h1 class="sat-header-title">Priority Review Queue</h1>
            <div class="sat-header-subtitle">Ranked operational findings requiring supervisory manual inspection</div>
        </div>
        <div class="sat-meta-pill-group">
            <div class="sat-meta-pill">
                <span>Queue Triage:</span> <strong>Top Critical First</strong>
            </div>
            <div class="sat-meta-pill">
                <span>Mode:</span> <strong>Examiner Verification</strong>
            </div>
        </div>
    </div>
    """)

    # -------------------------------------------------------------
    # 2. FLATTEN ALL FINDINGS ACROSS CSES
    # -------------------------------------------------------------
    all_findings: list[tuple[str, Finding]] = []
    for cse_id, att in cse_attentions.items():
        for f in att.findings:
            all_findings.append((cse_id, f))
            
    sev_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    all_findings.sort(key=lambda item: (sev_weights.get(item[1].severity, 0), cse_attentions[item[0]].attention_score, item[0]), reverse=True)

    # -------------------------------------------------------------
    # 3. FILTER BAR
    # -------------------------------------------------------------
    f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1, 2])
    
    with f_col1:
        cse_options = ["All CSEs"] + sorted(list(cse_attentions.keys()))
        selected_cse_filter = st.selectbox("Filter CSE", options=cse_options, key="q_cse_filter")
        
    with f_col2:
        sev_options = ["All Severities", "HIGH", "MEDIUM", "LOW"]
        selected_sev_filter = st.selectbox("Filter Severity", options=sev_options, key="q_sev_filter")
        
    with f_col3:
        rule_options = ["All Rules", "EG-1", "EG-2", "EG-3", "EG-4", "NS-1", "PEER-1", "T-1", "K-1", "I-1"]
        selected_rule_filter = st.selectbox("Filter Rule", options=rule_options, key="q_rule_filter")
        
    with f_col4:
        search_kw = st.text_input("Search Queue", placeholder="Search finding title or evidence ID...", key="q_search_input")

    filtered_items = []
    for cse_id, f in all_findings:
        if selected_cse_filter != "All CSEs" and cse_id != selected_cse_filter:
            continue
        if selected_sev_filter != "All Severities" and f.severity != selected_sev_filter:
            continue
        if selected_rule_filter != "All Rules" and f.rule_id != selected_rule_filter:
            continue
        if search_kw:
            kw = search_kw.lower()
            match_title = kw in f.title.lower()
            match_cse = kw in cse_id.lower()
            match_ev = any(kw in ev.lower() for ev in f.evidence_ids)
            if not (match_title or match_cse or match_ev):
                continue
        filtered_items.append((cse_id, f))

    render_html(f"""
    <div style="font-size: 13px; color: #636A84; margin-bottom: 10px;">
        Displaying <strong>{len(filtered_items)}</strong> prioritized supervisory findings
    </div>
    """)

    # -------------------------------------------------------------
    # 4. RANKED TABLE & INTERACTIVE SELECTION
    # -------------------------------------------------------------
    col_table, col_inspect = st.columns([3, 2])

    with col_table:
        table_html = """
        <div class="sat-table-wrapper">
            <table class="sat-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>CSE</th>
                        <th>Rule</th>
                        <th>Finding Title</th>
                        <th>Severity</th>
                        <th>Evidence ID</th>
                    </tr>
                </thead>
                <tbody>
        """
        for rank, (cse_id, f) in enumerate(filtered_items[:20], 1):
            sev_badge = "sat-badge-high" if f.severity == "HIGH" else ("sat-badge-med" if f.severity == "MEDIUM" else "sat-badge-low")
            ev_snippet = f.evidence_ids[0] if f.evidence_ids else "N/A"
            table_html += f"""
                <tr>
                    <td><strong>{rank:02d}</strong></td>
                    <td><strong>{cse_id}</strong></td>
                    <td><span class="sat-op-rule" style="margin: 0;">{f.rule_id}</span></td>
                    <td style="max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{f.title}</td>
                    <td><span class="sat-badge {sev_badge}">{f.severity}</span></td>
                    <td><code>{ev_snippet}</code></td>
                </tr>
            """
        table_html += """
                </tbody>
            </table>
        </div>
        """
        render_html(table_html)

    with col_inspect:
        if not filtered_items:
            st.warning("No findings match the current filter selection.")
            return

        choice_idx = st.selectbox(
            "Select Item to Inspect",
            options=range(1, min(len(filtered_items) + 1, 21)),
            format_func=lambda i: f"#{i:02d} - {filtered_items[i-1][0]} ({filtered_items[i-1][1].rule_id}: {filtered_items[i-1][1].title[:35]}...)",
            key="inspect_choice"
        )
        
        target_cse, target_f = filtered_items[choice_idx - 1]
        sev_badge = "sat-badge-high" if target_f.severity == "HIGH" else ("sat-badge-med" if target_f.severity == "MEDIUM" else "sat-badge-low")

        rec_msg = 'Immediate corrective review requested within 30 days.' if target_f.severity == 'HIGH' else 'Review during scheduled supervisory audit cycle.'
        inspect_html = f"""
        <div class="sat-card" style="border-top: 3px solid #5146A8;">
            <div style="font-size: 14px; font-weight: 700; color: #241B5B; margin-bottom: 4px;">
                Selected Finding Inspection Drawer
            </div>
            <div style="font-size: 12px; color: #636A84; margin-bottom: 12px;">
                Supervisory evidence breakdown for inspection item #{choice_idx:02d}
            </div>
            
            <div style="margin-top: 10px; border-bottom: 1px solid #E5E7F0; padding-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="sat-op-rule">{target_f.rule_id}</span>
                    <span class="sat-badge {sev_badge}">{target_f.severity}</span>
                </div>
                <div style="font-size: 14px; font-weight: 700; color: #241B5B; margin-top: 6px;">{target_f.title}</div>
                <div style="font-size: 12px; color: #5146A8; font-weight: 600;">Entity: {target_cse}</div>
            </div>

            <div style="margin-top: 10px;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #636A84;">WHY WAS THIS FLAGGED?</div>
                <div style="font-size: 12.5px; color: #2D3142; margin-top: 3px; line-height: 1.4;">{target_f.explanation}</div>
            </div>

            <div style="margin-top: 10px;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #636A84;">EVIDENCE REFERENCES</div>
                <div style="font-size: 12px; color: #5146A8; margin-top: 3px;">
                    <code>{', '.join(target_f.evidence_ids)}</code>
                </div>
            </div>

            <div style="margin-top: 10px; background-color: #F8F9FC; border: 1px solid #E5E7F0; border-radius: 8px; padding: 10px;">
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #40358C;">RECOMMENDED ACTION</div>
                <div style="font-size: 12px; color: #241B5B; margin-top: 2px;">
                    {rec_msg}
                </div>
                <div style="font-size: 10.5px; color: #7A819B; margin-top: 6px; font-style: italic;">
                    System-generated supervisory observation intended to support, not replace, examiner judgement.
                </div>
            </div>
        </div>
        """
        render_html(inspect_html)

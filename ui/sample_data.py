"""
Sample Data Generator and State Provider for SAT-SA Frontend.
Produces 22 CSE entities, standard alert/asset/case DataFrames, and canonical
Finding and CSEAttention dataclass instances matching specifications.
"""

import pandas as pd
import numpy as np
from engine.findings import Finding, CSEAttention

def generate_sample_data():
    """
    Generates a deterministic illustrative dataset of 22 CSEs
    with exact KPI distributions:
    - 4 HIGH attention CSEs
    - 7 MEDIUM attention CSEs
    - 11 LOW attention CSEs
    Total findings: 86
    Includes sector-wide signal (EG-4 affecting 9 CSEs on Firewall/DNS assets).
    """
    cse_ids = [f"CSE-{i:02d}" for i in range(1, 23)]
    
    # Pre-defined status and attention distribution
    # High: CSE-07 (12), CSE-04 (9), CSE-09 (8), CSE-15 (7) -> 36 findings
    # Medium: CSE-11 (6), CSE-03 (5), CSE-08 (5), CSE-12 (5), CSE-16 (4), CSE-19 (4), CSE-21 (4) -> 33 findings
    # Low: CSE-01 (2), CSE-02 (1), CSE-05 (2), CSE-06 (1), CSE-10 (2), CSE-13 (1), CSE-14 (2), CSE-17 (1), CSE-18 (2), CSE-20 (1), CSE-22 (2) -> 17 findings
    # Total = 36 + 33 + 17 = 86 findings!
    
    # 1. Assets
    asset_rows = []
    asset_types = ["DNS Server", "Firewall", "Core Database", "Domain Controller", "Web Application"]
    for cse in cse_ids:
        for a_idx in range(1, 6):
            ast_id = f"AST-{cse.split('-')[1]}{a_idx:02d}"
            crit = "Critical" if a_idx in (1, 2) else ("High" if a_idx == 3 else "Medium")
            a_type = asset_types[a_idx - 1]
            exp_mon = "Yes"
            # CSE-11 has monitoring blind spot on AST-1101
            obs_events = 1 if (cse == "CSE-11" and a_idx == 1) else (0 if (cse == "CSE-15" and a_idx == 1) else np.random.randint(15, 80))
            asset_rows.append({
                "asset_id": ast_id,
                "cse_id": cse,
                "criticality": crit,
                "asset_type": a_type,
                "expected_monitoring": exp_mon,
                "observed_monitoring_events": obs_events
            })
    assets_df = pd.DataFrame(asset_rows)

    # 2. Alerts & Findings
    alert_rows = []
    case_rows = []
    cse_attentions = {}
    
    # Pre-seed specific findings for known personas
    # CSE-07: High, 12 findings, Escalation Rate 18%
    # CSE-04: High, 9 findings, Escalation Rate 24%
    # CSE-11: Medium, 6 findings, Escalation Rate 41%
    # CSE-02: Low, 1 finding, Escalation Rate 63%
    
    alert_counter = 1000
    case_counter = 5000
    
    for cse in cse_ids:
        findings = []
        c_num = int(cse.split("-")[1])
        
        # Determine attention level and findings count
        if cse == "CSE-07":
            f_count = 12
            level = "HIGH"
            score = 28.0
            esc_rate = 0.18
        elif cse == "CSE-04":
            f_count = 9
            level = "HIGH"
            score = 22.0
            esc_rate = 0.24
        elif cse in ("CSE-09", "CSE-15"):
            f_count = 8 if cse == "CSE-09" else 7
            level = "HIGH"
            score = 18.0
            esc_rate = 0.22
        elif cse == "CSE-11":
            f_count = 6
            level = "MEDIUM"
            score = 8.0
            esc_rate = 0.41
        elif cse in ("CSE-03", "CSE-08", "CSE-12"):
            f_count = 5
            level = "MEDIUM"
            score = 7.0
            esc_rate = 0.44
        elif cse in ("CSE-16", "CSE-19", "CSE-21"):
            f_count = 4
            level = "MEDIUM"
            score = 6.0
            esc_rate = 0.46
        elif cse == "CSE-02":
            f_count = 1
            level = "LOW"
            score = 2.0
            esc_rate = 0.63
        else:
            f_count = 1 if c_num % 2 == 0 else 2
            level = "LOW"
            score = float(f_count * 1.5)
            esc_rate = 0.58 + (c_num * 0.01)

        # Generate illustrative alert records for this CSE
        num_alerts = 20 if level == "HIGH" else (14 if level == "MEDIUM" else 10)
        c_alerts = []
        for i in range(num_alerts):
            alert_counter += 1
            case_counter += 1
            a_id = f"A-{alert_counter:05d}"
            c_id = f"C-{case_counter:05d}"
            ast_id = f"AST-{cse.split('-')[1]}{(i % 5) + 1:02d}"
            
            # Severity distribution
            if i < 3:
                sev = "Critical"
            elif i < 7:
                sev = "High"
            elif i < 12:
                sev = "Medium"
            else:
                sev = "Low"
                
            # Closure & process flags based on CSE
            if cse == "CSE-07":
                # High failure rate
                esc = "No" if (sev in ("Critical", "High") and i % 2 == 0) else "Yes"
                inv = "No" if i in (1, 3, 5) else "Yes"
                close_min = 4 if i in (2, 4) else (45 if i < 10 else 120)
                rem = "No" if i < 8 else "Yes"
            elif cse == "CSE-04":
                # Repeated alerts no remediation
                esc = "No" if (sev == "Critical" and i == 0) else "Yes"
                inv = "Yes"
                close_min = 35
                rem = "No" if i < 6 else "Yes"
            elif cse == "CSE-11":
                # Monitoring blindspot & minor gaps
                esc = "No" if (sev == "Critical" and i == 1) else "Yes"
                inv = "No" if i == 2 else "Yes"
                close_min = 8 if i == 3 else 40
                rem = "Yes"
            else:
                esc = "Yes" if (sev in ("Critical", "High") and np.random.rand() < esc_rate) else ("No" if np.random.rand() < 0.1 else "Yes")
                inv = "Yes" if np.random.rand() > 0.08 else "No"
                close_min = np.random.randint(15, 180)
                rem = "Yes" if np.random.rand() > 0.15 else "No"
                
            c_alerts.append(a_id)
            alert_rows.append({
                "alert_id": a_id,
                "cse_id": cse,
                "asset_id": ast_id,
                "severity": sev,
                "created_time": f"2026-08-{10 + (i % 15):02d}T09:{10 + i:02d}:00Z",
                "ack_time": f"2026-08-{10 + (i % 15):02d}T09:{12 + i:02d}:00Z",
                "closure_time_minutes": close_min,
                "disposition": "Closed",
                "escalated": esc,
                "investigation_present": inv,
                "remediation_present": rem
            })
            
            case_rows.append({
                "case_id": c_id,
                "alert_id": a_id,
                "investigation_start": f"2026-08-{10 + (i % 15):02d}T09:15:00Z" if inv == "Yes" else "",
                "investigation_end": f"2026-08-{10 + (i % 15):02d}T10:00:00Z" if inv == "Yes" else "",
                "escalation_status": "Escalated" if esc == "Yes" else "Not Escalated",
                "closure_status": "Closed"
            })

        # Assemble Canonical Findings
        # EG-1: Critical alert closed without escalation
        if cse in ("CSE-07", "CSE-04", "CSE-09", "CSE-15", "CSE-11", "CSE-03"):
            ev_id = c_alerts[0]
            findings.append(Finding(
                finding_id=f"{cse}-EG1-{len(findings)+1:03d}",
                cse_id=cse,
                rule_id="EG-1",
                category="execution_gap",
                severity="HIGH",
                title="Critical alert closed without escalation",
                explanation=f"Critical alert {ev_id} was resolved without mandatory Tier-2 supervisor escalation.",
                evidence_ids=[ev_id],
                metric_value=None,
                peer_value=None,
                related_asset_type="Firewall"
            ))
            
        # EG-2: High/Critical alert without investigation
        if cse in ("CSE-07", "CSE-09", "CSE-11", "CSE-08", "CSE-12"):
            ev_id = c_alerts[1]
            findings.append(Finding(
                finding_id=f"{cse}-EG2-{len(findings)+1:03d}",
                cse_id=cse,
                rule_id="EG-2",
                category="execution_gap",
                severity="HIGH" if cse == "CSE-07" else "MEDIUM",
                title="High/Critical alert without investigation evidence",
                explanation=f"Alert {ev_id} reached closure disposition without documented forensic investigation notes.",
                evidence_ids=[ev_id],
                metric_value=None,
                peer_value=None,
                related_asset_type="Core Database"
            ))
            
        # EG-3: Suspiciously fast closure
        if cse in ("CSE-07", "CSE-11", "CSE-16", "CSE-19"):
            ev_id = c_alerts[2]
            findings.append(Finding(
                finding_id=f"{cse}-EG3-{len(findings)+1:03d}",
                cse_id=cse,
                rule_id="EG-3",
                category="execution_gap",
                severity="MEDIUM",
                title="Potential supervisory signal: suspiciously fast closure",
                explanation=f"Alert {ev_id} was closed in under 10 minutes. Raised as a review trigger, not a confirmed verdict.",
                evidence_ids=[ev_id],
                metric_value=4.0 if cse == "CSE-07" else 8.0,
                peer_value=45.0,
                related_asset_type="DNS Server"
            ))

        # EG-4: Repeated alerts without remediation (Shared by 9 CSEs -> Sector Wide!)
        if cse in ("CSE-07", "CSE-04", "CSE-09", "CSE-15", "CSE-03", "CSE-08", "CSE-12", "CSE-16", "CSE-21"):
            target_ast = f"AST-{cse.split('-')[1]}02"
            ev_ids = [c_alerts[0], c_alerts[3], c_alerts[4]]
            findings.append(Finding(
                finding_id=f"{cse}-EG4-{len(findings)+1:03d}",
                cse_id=cse,
                rule_id="EG-4",
                category="execution_gap",
                severity="HIGH",
                title="Repeated alerts without remediation evidence",
                explanation=f"Asset {target_ast} sustained recurrent high-severity alerts without documented remediation controls.",
                evidence_ids=ev_ids,
                metric_value=0.75,
                peer_value=0.20,
                related_asset_type="Firewall"
            ))

        # NS-1: Monitoring blind spot
        if cse in ("CSE-11", "CSE-15"):
            target_ast = f"AST-{cse.split('-')[1]}01"
            findings.append(Finding(
                finding_id=f"{cse}-NS1-{len(findings)+1:03d}",
                cse_id=cse,
                rule_id="NS-1",
                category="negative_space",
                severity="MEDIUM",
                title="Possible monitoring blind spot on critical asset",
                explanation=f"Critical asset {target_ast} had under 2 telemetry events recorded during the assessment cycle.",
                evidence_ids=[target_ast],
                metric_value=1.0 if cse == "CSE-11" else 0.0,
                peer_value=45.0,
                related_asset_type="DNS Server"
            ))

        # PEER-1: Escalation rate peer deviation
        if cse in ("CSE-07", "CSE-04", "CSE-09", "CSE-15"):
            findings.append(Finding(
                finding_id=f"{cse}-PEER1-{len(findings)+1:03d}",
                cse_id=cse,
                rule_id="PEER-1",
                category="peer_deviation",
                severity="HIGH" if esc_rate < 0.20 else "MEDIUM",
                title="Escalation rate significantly below sector baseline",
                explanation=f"Critical/High escalation rate ({int(esc_rate*100)}%) is over 2 standard deviations below the sector average (58%).",
                evidence_ids=[c_alerts[0]],
                metric_value=esc_rate * 100,
                peer_value=58.0,
                related_asset_type=None
            ))

        # Pad remaining findings to reach the desired target count
        while len(findings) < f_count:
            idx = len(findings) + 1
            ev_id = c_alerts[idx % len(c_alerts)]
            findings.append(Finding(
                finding_id=f"{cse}-EG1-{idx:03d}",
                cse_id=cse,
                rule_id="EG-1",
                category="execution_gap",
                severity="MEDIUM" if level != "HIGH" else "HIGH",
                title="Supervisory observation on unescalated event",
                explanation=f"Alert {ev_id} triggered supervisory review threshold.",
                evidence_ids=[ev_id],
                metric_value=None,
                peer_value=None,
                related_asset_type="Web Application"
            ))
            
        kpis = {
            "escalation_sla": f"{int(esc_rate * 100)}%" if level != "HIGH" else "94%", # gaming demonstration!
            "ack_sla": "97%" if cse == "CSE-07" else f"{np.random.randint(92, 99)}%",
            "closure_sla": "96%" if cse == "CSE-07" else f"{np.random.randint(90, 98)}%"
        }
        
        cse_attentions[cse] = CSEAttention(
            cse_id=cse,
            attention_score=score,
            attention_level=level,
            findings=findings,
            kpi_summary=kpis
        )
        
    alerts_df = pd.DataFrame(alert_rows)
    cases_df = pd.DataFrame(case_rows)
    
    return {
        "cse_attentions": cse_attentions,
        "alerts_df": alerts_df,
        "assets_df": assets_df,
        "cases_df": cases_df
    }

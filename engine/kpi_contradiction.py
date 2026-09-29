import pandas as pd
from engine.findings import Finding
from engine.data_store import DataStore
from config import KPI_CONTRADICTION_THRESHOLD

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_kpi_contradiction(store: DataStore) -> list[Finding]:
    """
    KPI_CONTRADICTION (K-1): Compare reported metrics against operational computed ones.
    """
    findings = []
    
    for cse_id, profile in store._profiles_idx.items():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        if not alerts: continue
        
        # Operational Escalation Rate
        crit_high = [a for a in alerts if a.get("severity") in ("Critical", "High") and a.get("disposition") == "Closed"]
        if crit_high:
            esc = sum(1 for a in crit_high if a.get("escalated") == "Yes")
            op_esc_rate = esc / len(crit_high)
        else:
            op_esc_rate = None
            
        # Operational Investigation Rate
        if crit_high:
            inv = sum(1 for a in crit_high if a.get("investigation_present") != "No")
            op_inv_rate = inv / len(crit_high)
        else:
            op_inv_rate = None
            
        # Operational MTTR
        closed_alerts = []
        for a in alerts:
            if a.get("disposition") == "Closed":
                try:
                    mins = float(a.get("closure_time_minutes", -1))
                    if mins >= 0:
                        closed_alerts.append(mins)
                except (ValueError, TypeError):
                    pass
        op_mttr = sum(closed_alerts) / len(closed_alerts) if closed_alerts else None
        
        # Checking Escalation Contradiction
        if op_esc_rate is not None and "reported_escalation_rate" in profile:
            try:
                rep_esc = float(profile["reported_escalation_rate"])
                if pd.notna(rep_esc):
                    diff = rep_esc - op_esc_rate
                    if diff > KPI_CONTRADICTION_THRESHOLD:
                        sev = "HIGH" if diff >= 0.40 else "MEDIUM"
                        findings.append(Finding(
                            finding_id=generate_finding_id(cse_id, "K-1", 1),
                            cse_id=cse_id,
                            rule_id="K-1",
                            category="kpi_contradiction",
                            severity=sev,
                            title="Reported vs observed operational discrepancy requiring examiner review",
                            explanation=f"Reported escalation rate ({rep_esc:.0%}) contradicts observed operational rate ({op_esc_rate:.0%}). Difference: {diff:.0%}.",
                            evidence_ids=[a["alert_id"] for a in crit_high],
                            metric_value=op_esc_rate,
                            peer_value=rep_esc,
                            related_asset_type="Escalation SLA"
                        ))
            except (ValueError, TypeError):
                pass
                
        # Checking Investigation Contradiction
        if op_inv_rate is not None and "reported_investigation_rate" in profile:
            try:
                rep_inv = float(profile["reported_investigation_rate"])
                if pd.notna(rep_inv):
                    diff = rep_inv - op_inv_rate
                    if diff > KPI_CONTRADICTION_THRESHOLD:
                        sev = "HIGH" if diff >= 0.40 else "MEDIUM"
                        findings.append(Finding(
                            finding_id=generate_finding_id(cse_id, "K-1", 2),
                            cse_id=cse_id,
                            rule_id="K-1",
                            category="kpi_contradiction",
                            severity=sev,
                            title="Reported vs observed operational discrepancy requiring examiner review",
                            explanation=f"Reported investigation rate ({rep_inv:.0%}) contradicts observed operational rate ({op_inv_rate:.0%}). Difference: {diff:.0%}.",
                            evidence_ids=[a["alert_id"] for a in crit_high],
                            metric_value=op_inv_rate,
                            peer_value=rep_inv,
                            related_asset_type="Investigation SLA"
                        ))
            except (ValueError, TypeError):
                pass

    return findings

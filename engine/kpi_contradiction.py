import pandas as pd
from engine.findings import Finding
from engine.data_store import DataStore
from engine.metrics import compute_operational_escalation_rate, compute_operational_investigation_rate
from config import KPI_CONTRADICTION_THRESHOLD

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def _normalize_percentage(val):
    if pd.isna(val): return None
    try:
        val_str = str(val).strip().replace('%', '')
        num = float(val_str)
        if num > 1.0: return num / 100.0
        return num
    except ValueError:
        return None

def check_kpi_contradiction(store: DataStore) -> list[Finding]:
    """
    KPI_CONTRADICTION (K-1): Compare reported metrics against operational computed ones.
    """
    findings = []
    
    for cse_id, profile in store._profiles_idx.items():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        if not alerts: 
            continue
            
        op_esc_rate, esc_vol = compute_operational_escalation_rate(alerts)
        op_inv_rate, inv_vol = compute_operational_investigation_rate(alerts, store)
        
        finding_idx = 1
        
        # Checking Escalation Contradiction
        if op_esc_rate is not None and "reported_escalation_rate" in profile:
            rep_esc = _normalize_percentage(profile["reported_escalation_rate"])
            if rep_esc is not None:
                diff = abs(rep_esc - op_esc_rate)
                if diff >= KPI_CONTRADICTION_THRESHOLD:
                    sev = "HIGH" if diff >= 0.40 else "MEDIUM"
                    direction = "higher" if rep_esc > op_esc_rate else "lower"
                    findings.append(Finding(
                        finding_id=generate_finding_id(cse_id, "K-1", finding_idx),
                        cse_id=cse_id,
                        rule_id="K-1",
                        category="kpi_contradiction",
                        severity=sev,
                        title="Reported escalation KPI contradicts operational evidence",
                        explanation=f"Reported escalation rate ({rep_esc:.0%}) is {direction} than the observed operational rate ({op_esc_rate:.0%}, n={esc_vol}). Difference: {diff:.0%}.",
                        evidence_ids=[],
                        metric_value=op_esc_rate,
                        peer_value=rep_esc,
                        related_asset_type="Escalation SLA"
                    ))
                    finding_idx += 1
                    
        # Checking Investigation Contradiction
        if op_inv_rate is not None and "reported_investigation_rate" in profile:
            rep_inv = _normalize_percentage(profile["reported_investigation_rate"])
            if rep_inv is not None:
                diff = abs(rep_inv - op_inv_rate)
                if diff >= KPI_CONTRADICTION_THRESHOLD:
                    sev = "HIGH" if diff >= 0.40 else "MEDIUM"
                    direction = "higher" if rep_inv > op_inv_rate else "lower"
                    findings.append(Finding(
                        finding_id=generate_finding_id(cse_id, "K-1", finding_idx),
                        cse_id=cse_id,
                        rule_id="K-1",
                        category="kpi_contradiction",
                        severity=sev,
                        title="Reported investigation KPI contradicts operational evidence",
                        explanation=f"Reported investigation rate ({rep_inv:.0%}) is {direction} than the observed operational rate ({op_inv_rate:.0%}, n={inv_vol}). Difference: {diff:.0%}.",
                        evidence_ids=[],
                        metric_value=op_inv_rate,
                        peer_value=rep_inv,
                        related_asset_type="Investigation SLA"
                    ))
                    finding_idx += 1

    return findings

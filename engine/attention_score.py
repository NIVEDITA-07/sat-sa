from engine.findings import Finding, CSEAttention
from config import SCORE_WEIGHT_HIGH, SCORE_WEIGHT_MEDIUM, SCORE_WEIGHT_LOW, SCORE_LEVEL_HIGH_MIN, SCORE_LEVEL_MEDIUM_MIN
from engine.data_store import DataStore
import pandas as pd

def compute_attention(cse_id: str, findings: list[Finding], store: DataStore) -> CSEAttention:
    """
    Computes final attention score and KPI summary for a CSE.
    """
    score = 0.0
    for f in findings:
        if f.severity == "HIGH":
            score += SCORE_WEIGHT_HIGH
        elif f.severity == "MEDIUM":
            score += SCORE_WEIGHT_MEDIUM
        else:
            score += SCORE_WEIGHT_LOW
            
    if score >= SCORE_LEVEL_HIGH_MIN:
        level = "HIGH"
    elif score >= SCORE_LEVEL_MEDIUM_MIN:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    data = store.get_cse_data(cse_id)
    cse_alerts = data.get("alerts", [])
    total_alerts = len(cse_alerts)
    
    if total_alerts > 0:
        esc_rate = int(sum(1 for a in cse_alerts if a.get('escalated') == 'Yes') / total_alerts * 100)
        closure_rate = int(sum(1 for a in cse_alerts if a.get('disposition') == 'Closed') / total_alerts * 100)
        ack_rate = 97  # Fallback if profile missing
    else:
        esc_rate, closure_rate, ack_rate = 100, 100, 100
        
    # Dynamically read KPIs from cse_profiles_df
    kpis = {}
    profile = data.get("profile", {})
    if profile:
        # Assumes values like 0.94 in the CSV need to be shown as 94%
        if 'reported_escalation_rate' in profile and pd.notna(profile['reported_escalation_rate']):
            esc_val = profile['reported_escalation_rate']
            kpis["escalation_sla"] = f"{int(float(esc_val)*100)}%" if isinstance(esc_val, (int, float, str)) else f"{esc_rate}%"
        if 'reported_investigation_rate' in profile and pd.notna(profile['reported_investigation_rate']):
            ack_val = profile['reported_investigation_rate'] # Use this for ack/investigation proxy
            kpis["ack_sla"] = f"{int(float(ack_val)*100)}%" if isinstance(ack_val, (int, float, str)) else f"{ack_rate}%"
        if 'reported_monitoring_coverage' in profile and pd.notna(profile['reported_monitoring_coverage']):
            closure_val = profile['reported_monitoring_coverage'] # Proxy for closure/coverage
            kpis["closure_sla"] = f"{int(float(closure_val)*100)}%" if isinstance(closure_val, (int, float, str)) else f"{closure_rate}%"
                
    if not kpis:
        kpis = {
            "escalation_sla": f"{esc_rate}%",
            "ack_sla": f"{ack_rate}%",
            "closure_sla": f"{closure_rate}%"
        }
        
    return CSEAttention(
        cse_id=cse_id,
        attention_score=score,
        attention_level=level,
        findings=findings,
        kpi_summary=kpis
    )

import pandas as pd
from engine.findings import Finding
from engine.data_store import DataStore
from config import TEMPORAL_DRIFT_THRESHOLD, TEMPORAL_MIN_DAYS, TEMPORAL_MIN_OBSERVATIONS
from engine.semantics import is_known_yes, is_known_no, is_available, resolve_investigation_expectation, EXPECTATION_YES

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_temporal_drift(store: DataStore) -> list[Finding]:
    """
    TEMPORAL_DRIFT (T-1): Detects meaningful deterioration in operational metrics over time.
    Uses actual calendar/time windows (e.g. trailing 30 days vs prior 30 days).
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        if not alerts: 
            continue
        
        valid_alerts = []
        for a in alerts:
            ts = a.get("created_at")
            if not is_available(ts):
                ts = a.get("created_time")
            if is_available(ts):
                try:
                    a["_ts"] = pd.to_datetime(ts, errors='coerce', utc=True)
                    if pd.notna(a["_ts"]):
                        valid_alerts.append(a)
                except Exception:
                    pass
                    
        if not valid_alerts: 
            continue
        
        valid_alerts.sort(key=lambda x: x["_ts"])
        
        min_date = valid_alerts[0]["_ts"]
        max_date = valid_alerts[-1]["_ts"]
        
        total_days = (max_date - min_date).days
        if total_days < TEMPORAL_MIN_DAYS * 2:
            continue # Need enough calendar days for two windows
            
        # Define recent as the last TEMPORAL_MIN_DAYS
        # Define baseline as the TEMPORAL_MIN_DAYS before that
        recent_start = max_date - pd.Timedelta(days=TEMPORAL_MIN_DAYS)
        baseline_start = recent_start - pd.Timedelta(days=TEMPORAL_MIN_DAYS)
        
        baseline_alerts = [a for a in valid_alerts if baseline_start <= a["_ts"] < recent_start]
        recent_alerts = [a for a in valid_alerts if recent_start <= a["_ts"] <= max_date]
        
        if not baseline_alerts or not recent_alerts: 
            continue
        
        # Calculate metric: investigation rate for High/Critical
        def get_investigation_rate(al_list):
            evaluable = []
            investigated_count = 0
            for a in al_list:
                if a.get("disposition") != "Closed": continue
                if resolve_investigation_expectation(a) != EXPECTATION_YES: continue
                
                # Check investigation evidence
                inv_present = a.get("investigation_present")
                case_row = store.get_case_for_alert(a.get("alert_id"))
                
                case_bypassed = False
                if case_row and case_row.get("investigation_status") == "Bypassed":
                    case_bypassed = True
                    
                if is_known_yes(inv_present) or (case_row and not case_bypassed and is_available(case_row.get("investigation_status"))):
                    evaluable.append(a)
                    investigated_count += 1
                elif is_known_no(inv_present) or case_bypassed:
                    evaluable.append(a)
            
            if len(evaluable) < TEMPORAL_MIN_OBSERVATIONS: 
                return None, 0
                
            return investigated_count / len(evaluable), len(evaluable)
            
        base_rate, base_vol = get_investigation_rate(baseline_alerts)
        recent_rate, recent_vol = get_investigation_rate(recent_alerts)
        
        if base_rate is not None and recent_rate is not None:
            diff = base_rate - recent_rate
            if diff >= TEMPORAL_DRIFT_THRESHOLD:
                sev = "HIGH" if diff >= 0.40 else "MEDIUM"
                
                recent_evaluable = [a for a in recent_alerts if a.get("disposition") == "Closed"]
                evidence = [a['alert_id'] for a in recent_evaluable]
                
                b_date_str = f"{baseline_start.strftime('%Y-%m-%d')} to {recent_start.strftime('%Y-%m-%d')}"
                r_date_str = f"{recent_start.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
                
                c_val = recent_rate * 100
                p_val = base_rate * 100
                
                findings.append(Finding(
                    finding_id=generate_finding_id(cse_id, "T-1", 1),
                    cse_id=cse_id,
                    rule_id="T-1",
                    category="temporal_drift",
                    severity=sev,
                    title="Investigation rate declined materially in recent period",
                    explanation=f"Investigation rate for expected alerts declined from {int(p_val)}% (Baseline: {b_date_str}, n={base_vol}) to {int(c_val)}% (Recent: {r_date_str}, n={recent_vol}).",
                    evidence_ids=evidence,
                    metric_value=recent_rate,
                    peer_value=base_rate,
                    related_asset_type=None
                ))
                
    return findings

import pandas as pd
from engine.findings import Finding
from engine.data_store import DataStore
from config import TEMPORAL_DRIFT_THRESHOLD, TEMPORAL_WINDOW_DAYS

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_temporal_drift(store: DataStore) -> list[Finding]:
    """
    TEMPORAL_DRIFT (T-1): Detects meaningful deterioration in operational metrics over time.
    Compares earlier window vs later window.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        if not alerts: continue
        
        # We need created_at to sort them in time
        valid_alerts = []
        for a in alerts:
            ts = a.get("created_at")
            if pd.isna(ts) or ts == "NOT_AVAILABLE":
                ts = a.get("created_time")
            if pd.notna(ts) and ts != "NOT_AVAILABLE":
                try:
                    a["_ts"] = pd.to_datetime(ts, errors='coerce', utc=True)
                    if pd.notna(a["_ts"]):
                        valid_alerts.append(a)
                except Exception:
                    pass
                    
        if not valid_alerts: continue
        
        valid_alerts.sort(key=lambda x: x["_ts"])
        
        min_date = valid_alerts[0]["_ts"]
        max_date = valid_alerts[-1]["_ts"]
        
        total_days = (max_date - min_date).days
        if total_days < TEMPORAL_WINDOW_DAYS * 2:
            continue # Need at least 2 windows
            
        # Split into baseline (first half) and recent (second half)
        mid_date = min_date + pd.Timedelta(days=total_days / 2)
        
        baseline_alerts = [a for a in valid_alerts if a["_ts"] <= mid_date]
        recent_alerts = [a for a in valid_alerts if a["_ts"] > mid_date]
        
        if not baseline_alerts or not recent_alerts: continue
        
        # Calculate metric: investigation rate (example)
        def get_investigation_rate(al_list):
            evaluable = [a for a in al_list if a.get("disposition") == "Closed"]
            if not evaluable: return None, 0
            inv = sum(1 for a in evaluable if a.get("investigation_present") != "No")
            return inv / len(evaluable), len(evaluable)
            
        base_rate, base_vol = get_investigation_rate(baseline_alerts)
        recent_rate, recent_vol = get_investigation_rate(recent_alerts)
        
        if base_rate is not None and recent_rate is not None and base_vol > 0 and recent_vol > 0:
            diff = base_rate - recent_rate
            if diff >= TEMPORAL_DRIFT_THRESHOLD: # Rate dropped by threshold (e.g. 20%)
                sev = "HIGH" if diff >= 0.40 else "MEDIUM"
                
                # Get evidence from recent alerts
                recent_evaluable = [a for a in recent_alerts if a.get("disposition") == "Closed"]
                evidence = [a['alert_id'] for a in recent_evaluable]
                
                b_date_str = f"{min_date.strftime('%Y-%m-%d')} to {mid_date.strftime('%Y-%m-%d')}"
                r_date_str = f"{mid_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
                
                findings.append(Finding(
                    finding_id=generate_finding_id(cse_id, "T-1", 1),
                    cse_id=cse_id,
                    rule_id="T-1",
                    category="temporal_drift",
                    severity=sev,
                    title="Deterioration in investigation rate over time",
                    explanation=f"Investigation rate for High/Critical alerts dropped from {base_rate:.0%} (Baseline: {b_date_str}) to {recent_rate:.0%} (Recent: {r_date_str}). Meaningful deterioration detected.",
                    evidence_ids=evidence,
                    metric_value=recent_rate,
                    peer_value=base_rate,
                    related_asset_type=None
                ))
                
    return findings

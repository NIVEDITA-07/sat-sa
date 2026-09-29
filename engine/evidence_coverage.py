import pandas as pd
from engine.data_store import DataStore

def check_evidence_coverage(store: DataStore) -> dict:
    """
    Calculates the coverage of supervisory evidence PER CSE.
    Missing evidence is tracked as NOT_AVAILABLE.
    Generates evidence coverage summaries and warnings.
    """
    cse_coverage_info = {}
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        assets = data.get("assets", [])
        cases = data.get("cases", [])
        
        alerts_df = pd.DataFrame(alerts)
        assets_df = pd.DataFrame(assets)
        cases_df = pd.DataFrame(cases)
        
        def eval_col(df, col):
            if df.empty or col not in df.columns: return "NOT_AVAILABLE"
            # Count valid
            valid = df[(df[col] != "NOT_AVAILABLE") & (df[col].notna())]
            if len(df) == 0: return "Available"
            ratio = len(valid) / len(df)
            if ratio == 1.0: return "Available"
            if ratio > 0: return "Partial"
            return "NOT_AVAILABLE"

        coverage = {
            "Alerts": "Available" if not alerts_df.empty else "NOT_AVAILABLE",
            "Assets": "Available" if not assets_df.empty else "NOT_AVAILABLE",
            "Cases": "Available" if not cases_df.empty else "NOT_AVAILABLE",
            "Investigation": eval_col(alerts_df, "investigation_present"),
            "Escalation": eval_col(alerts_df, "escalated"),
            "Remediation": eval_col(alerts_df, "remediation_present"),
            "Monitoring": eval_col(assets_df, "observed_monitoring_events"),
            "Investigation Notes": eval_col(cases_df, "investigation_note"),
            "Closure Time": eval_col(alerts_df, "closure_time_minutes")
        }
        
        warnings = []
        rule_avail = {}
        
        # Determine rule readiness based on evidence and generate warnings
        if coverage["Escalation"] == "NOT_AVAILABLE":
            warnings.append("EG-1 could not be fully evaluated because escalation evidence is unavailable.")
            rule_avail["EG-1"] = "INSUFFICIENT EVIDENCE"
        else:
            rule_avail["EG-1"] = "READY"
            
        if coverage["Investigation"] == "NOT_AVAILABLE":
            warnings.append("EG-2 could not be fully evaluated because investigation evidence is unavailable.")
            rule_avail["EG-2"] = "INSUFFICIENT EVIDENCE"
        else:
            rule_avail["EG-2"] = "READY"
            
        if coverage["Closure Time"] == "NOT_AVAILABLE":
            warnings.append("EG-3 could not be fully evaluated because closure timestamps are unavailable.")
            rule_avail["EG-3"] = "INSUFFICIENT EVIDENCE"
        else:
            rule_avail["EG-3"] = "READY"
            
        if coverage["Remediation"] == "NOT_AVAILABLE":
            warnings.append("EG-4 could not be fully evaluated because remediation evidence is unavailable.")
            rule_avail["EG-4"] = "INSUFFICIENT EVIDENCE"
        else:
            rule_avail["EG-4"] = "READY"
            
        if coverage["Monitoring"] == "NOT_AVAILABLE":
            warnings.append("NS-1 could not be fully evaluated because monitoring telemetry is unavailable.")
            rule_avail["NS-1"] = "INSUFFICIENT EVIDENCE"
        else:
            rule_avail["NS-1"] = "READY"
            
        if coverage["Escalation"] == "NOT_AVAILABLE":
            warnings.append("PEER-1 could not be fully evaluated because escalation evidence is unavailable.")
            rule_avail["PEER-1"] = "INSUFFICIENT EVIDENCE"
        else:
            rule_avail["PEER-1"] = "READY"
            
        if coverage["Investigation Notes"] == "NOT_AVAILABLE":
            warnings.append("I-1 could not be fully evaluated because investigation notes are unavailable.")
            rule_avail["I-1"] = "INSUFFICIENT EVIDENCE"
        else:
            rule_avail["I-1"] = "READY"

        cse_coverage_info[cse_id] = {
            "coverage_summary": coverage,
            "rule_availability": rule_avail,
            "warnings": warnings
        }
        
    return cse_coverage_info

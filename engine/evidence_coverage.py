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
        def evaluate_rule_status(required_columns, coverage_map):
            missing_count = sum(1 for col in required_columns if coverage_map.get(col) == "NOT_AVAILABLE")
            partial_count = sum(1 for col in required_columns if coverage_map.get(col) == "Partial")
            
            if missing_count > 0:
                return "INSUFFICIENT EVIDENCE"
            elif partial_count > 0:
                return "PARTIALLY EVALUABLE"
            return "READY"
            
        rule_avail["EG-1"] = evaluate_rule_status(["Escalation", "Alerts"], coverage)
        rule_avail["EG-2"] = evaluate_rule_status(["Investigation", "Alerts"], coverage)
        rule_avail["EG-3"] = evaluate_rule_status(["Closure Time", "Alerts"], coverage)
        rule_avail["EG-4"] = evaluate_rule_status(["Remediation", "Alerts"], coverage)
        rule_avail["NS-1"] = evaluate_rule_status(["Monitoring", "Assets"], coverage)
        rule_avail["PEER-1"] = evaluate_rule_status(["Escalation", "Alerts"], coverage)
        rule_avail["T-1"] = evaluate_rule_status(["Investigation", "Alerts"], coverage)
        rule_avail["K-1"] = evaluate_rule_status(["Escalation", "Investigation", "Alerts"], coverage)
        rule_avail["I-1"] = evaluate_rule_status(["Investigation Notes", "Cases"], coverage)
        
        for rule, status in rule_avail.items():
            if status == "INSUFFICIENT EVIDENCE":
                warnings.append(f"{rule} could not be fully evaluated because critical evidence is unavailable.")
            elif status == "PARTIALLY EVALUABLE":
                warnings.append(f"{rule} is evaluated on partial evidence; findings may be incomplete.")

        cse_coverage_info[cse_id] = {
            "coverage_summary": coverage,
            "rule_availability": rule_avail,
            "warnings": warnings
        }
        
    return cse_coverage_info

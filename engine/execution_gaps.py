import pandas as pd
from engine.findings import Finding
from config import FAST_CLOSURE_MINUTES, REPEAT_ALERT_THRESHOLD, REPEAT_NO_REMEDIATION_RATIO
from engine.data_store import DataStore
from collections import Counter

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def _get_top_asset_type(alerts: list, store: DataStore) -> str:
    asset_types = []
    for a in alerts:
        asset_id = a.get('asset_id')
        if asset_id:
            asset = store.get_asset_evidence(asset_id)
            if asset and 'asset_type' in asset:
                asset_types.append(asset['asset_type'])
    if not asset_types: return "Unknown"
    return Counter(asset_types).most_common(1)[0][0]

def check_eg1_critical_no_escalation(store: DataStore) -> list[Finding]:
    """
    EG-1: Critical/High alert closed without escalation.
    Aggregates at the CSE level: one finding per CSE summarizing the violation rate.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        # Filter for evaluable alerts: Critical/High and closed_at is present
        evaluable = [a for a in alerts if a.get("severity") in ("Critical", "High") and pd.notna(a.get("closed_at")) and a.get("closed_at") != "NOT_AVAILABLE"]
        
        if not evaluable:
            continue
            
        total_critical_closed = len(evaluable)
        not_escalated = [a for a in evaluable if a.get("escalated") == "No"]
        violation_count = len(not_escalated)
        
        if violation_count == 0:
            continue
            
        violation_rate = violation_count / total_critical_closed
        
        # The prompt says: "Generate: rule_id = EG-1, category = execution_gap, severity = HIGH"
        sev = "HIGH"
            
        top_asset_type = _get_top_asset_type(not_escalated, store)
        evidence = [a['alert_id'] for a in not_escalated]
        
        findings.append(Finding(
            finding_id=generate_finding_id(cse_id, "EG-1", 1),
            cse_id=cse_id,
            rule_id="EG-1",
            category="execution_gap",
            severity=sev,
            title="Critical alerts closed without escalation",
            explanation=f"{violation_count} of {total_critical_closed} critical alerts ({violation_rate:.0%}) were closed without mandatory Tier-2 supervisor escalation.",
            evidence_ids=evidence,
            metric_value=violation_rate,
            related_asset_type=top_asset_type
        ))
    return findings

def check_eg2_missing_investigation(store: DataStore) -> list[Finding]:
    """
    EG-2: High/Critical alert without investigation evidence.
    Aggregated at the CSE level.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        # We need cases for this CSE to check for 'Bypassed'
        cases_df = store.cases_df
        cse_cases = cases_df[cases_df['cse_id'] == cse_id] if not cases_df.empty and 'cse_id' in cases_df.columns else pd.DataFrame()
        bypassed_alert_ids = set()
        if not cse_cases.empty and 'investigation_status' in cse_cases.columns:
            bypassed_alert_ids = set(cse_cases[cse_cases['investigation_status'] == 'Bypassed']['primary_alert_id'].dropna())
        
        evaluable = [a for a in alerts if a.get("severity") in ("Critical", "High") and a.get("disposition") == "Closed"]
        
        if not evaluable:
            continue
            
        total = len(evaluable)
        # explicitly indicates NO
        no_investigation = [
            a for a in evaluable 
            if a.get("investigation_present") == "No" or a.get("alert_id") in bypassed_alert_ids
        ]
        
        violation_count = len(no_investigation)
        
        if violation_count == 0:
            continue
            
        violation_rate = violation_count / total
        
        has_critical = any(a.get("severity") == "Critical" for a in no_investigation)
        if has_critical:
            sev = "HIGH"
        else:
            sev = "MEDIUM"
            
        top_asset_type = _get_top_asset_type(no_investigation, store)
        evidence = [a['alert_id'] for a in no_investigation]
        
        findings.append(Finding(
            finding_id=generate_finding_id(cse_id, "EG-2", 1),
            cse_id=cse_id,
            rule_id="EG-2",
            category="execution_gap",
            severity=sev,
            title="Alerts without investigation evidence",
            explanation=f"{violation_count} of {total} critical/high alerts ({violation_rate:.0%}) explicitly lacked investigation prior to closure.",
            evidence_ids=evidence,
            metric_value=violation_rate,
            related_asset_type=top_asset_type
        ))
    return findings

def check_eg3_fast_closure(store: DataStore) -> list[Finding]:
    """
    EG-3: Suspiciously fast closure.
    Aggregated at the CSE level.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        evaluable = []
        for a in alerts:
            if a.get("disposition") != "Closed": continue
            try:
                mins = float(a.get("closure_time_minutes", -1))
                if mins >= 0:
                    a["_mins"] = mins
                    evaluable.append(a)
            except (ValueError, TypeError):
                continue
                
        if not evaluable:
            continue
            
        total_closed = len(evaluable)
        fast_closed = [a for a in evaluable if a["_mins"] < FAST_CLOSURE_MINUTES]
        violation_count = len(fast_closed)
        
        if violation_count == 0:
            continue
            
        violation_rate = violation_count / total_closed
        avg_fast_time = sum(a["_mins"] for a in fast_closed) / violation_count
        
        if violation_rate >= 0.15:
            sev = "HIGH"
        elif violation_rate >= 0.05:
            sev = "MEDIUM"
        else:
            sev = "LOW"
            
        top_asset_type = _get_top_asset_type(fast_closed, store)
        evidence = [a['alert_id'] for a in fast_closed]
        
        findings.append(Finding(
            finding_id=generate_finding_id(cse_id, "EG-3", 1),
            cse_id=cse_id,
            rule_id="EG-3",
            category="execution_gap",
            severity=sev,
            title="Potential fast-closure supervisory signal",
            explanation=f"{violation_count} of {total_closed} closed High/Critical alerts ({violation_rate:.0%}) were resolved in under {FAST_CLOSURE_MINUTES} minutes (avg {avg_fast_time:.1f} min).",
            evidence_ids=evidence,
            metric_value=violation_rate,
            peer_value=None,
            related_asset_type=top_asset_type
        ))
    return findings

def check_eg4_repeated_no_remediation(store: DataStore) -> list[Finding]:
    """
    EG-4: Repeated alerts without remediation on the same asset.
    Generates one HIGH finding per violating asset.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        # Group by asset
        asset_stats = {}
        for a in alerts:
            ast_id = a.get("asset_id")
            if not ast_id: continue
            
            if ast_id not in asset_stats:
                asset_stats[ast_id] = {"total": 0, "unremediated": 0, "evidence": []}
                
            asset_stats[ast_id]["total"] += 1
            if a.get("remediation_present") == "No":
                asset_stats[ast_id]["unremediated"] += 1
            asset_stats[ast_id]["evidence"].append(a["alert_id"])
            
        # Evaluate violators
        finding_idx = 1
        for ast_id, stats in asset_stats.items():
            if stats["total"] >= REPEAT_ALERT_THRESHOLD:
                ratio = stats["unremediated"] / stats["total"]
                if ratio >= REPEAT_NO_REMEDIATION_RATIO:
                    ast_rec = store.get_asset_evidence(ast_id)
                    top_asset_type = ast_rec.get("asset_type", "Unknown") if ast_rec else "Unknown"
                    
                    findings.append(Finding(
                        finding_id=generate_finding_id(cse_id, "EG-4", finding_idx),
                        cse_id=cse_id,
                        rule_id="EG-4",
                        category="execution_gap",
                        severity="HIGH",
                        title=f"Repeated alerts without remediation on asset {ast_id}",
                        explanation=f"Asset {ast_id} sustained {stats['total']} repeated alerts with {stats['unremediated']} ({ratio:.0%}) lacking remediation evidence.",
                        evidence_ids=[ast_id] + stats["evidence"],
                        metric_value=ratio,
                        peer_value=None,
                        related_asset_type=top_asset_type
                    ))
                    finding_idx += 1
                    
    return findings

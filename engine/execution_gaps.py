import pandas as pd
from engine.findings import Finding
from config import FAST_CLOSURE_MINUTES, REPEAT_ALERT_MIN_COUNT, REPEAT_UNREMEDIATED_RATIO
from engine.data_store import DataStore
from engine.semantics import (
    resolve_escalation_expectation,
    resolve_investigation_expectation,
    resolve_remediation_expectation,
    is_known_no,
    is_known_yes,
    is_available,
    EXPECTATION_YES,
    EVIDENCE_NO,
    EVIDENCE_NOT_AVAILABLE,
    EVIDENCE_YES
)
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
    EG-1: Critical/High alerts were observed to close without recorded escalation where escalation was expected.
    Aggregated at the CSE level.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        evaluable = []
        violation_alerts = []
        
        for alert in alerts:
            # Must be closed
            if alert.get("disposition") != "Closed":
                continue
                
            case_row = store.get_case_for_alert(alert.get("alert_id"))
            
            # Resolve expectation
            expected = resolve_escalation_expectation(alert, case_row=case_row)
            if expected != EXPECTATION_YES:
                continue
                
            # If expected=YES, check observation
            obs = alert.get("escalated")
            if not is_available(obs):
                # Coverage gap, not an execution gap
                continue
                
            evaluable.append(alert)
            if is_known_no(obs):
                violation_alerts.append(alert)
                
        if not evaluable or not violation_alerts:
            continue
            
        violation_count = len(violation_alerts)
        total_evaluable = len(evaluable)
        violation_rate = violation_count / total_evaluable
        
        top_asset_type = _get_top_asset_type(violation_alerts, store)
        evidence = [a['alert_id'] for a in violation_alerts]
        
        findings.append(Finding(
            finding_id=generate_finding_id(cse_id, "EG-1", 1),
            cse_id=cse_id,
            rule_id="EG-1",
            category="execution_gap",
            severity="HIGH",
            title="Expected escalation not observed",
            explanation=f"Critical/High alerts were observed to close without recorded escalation where escalation was expected. {violation_count} of {total_evaluable} evaluable alerts ({violation_rate:.0%}) lack escalation evidence.",
            evidence_ids=evidence,
            metric_value=violation_rate,
            related_asset_type=top_asset_type
        ))
        
    return findings

def check_eg2_missing_investigation(store: DataStore) -> list[Finding]:
    """
    EG-2: Alerts closed without investigation evidence where expected.
    Aggregated at the CSE level.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        evaluable = []
        violation_alerts = []
        
        for alert in alerts:
            if alert.get("disposition") != "Closed":
                continue
                
            expected = resolve_investigation_expectation(alert)
            if expected != EXPECTATION_YES:
                continue
                
            # Check observation
            inv_present = alert.get("investigation_present")
            case_row = store.get_case_for_alert(alert.get("alert_id"))
            
            # Reconcile evidence. If either says yes, it's a yes. 
            # If both say NO (or bypassed), it's a NO.
            # If missing/unavailable, it's unavailable.
            case_bypassed = False
            if case_row and case_row.get("investigation_status") == "Bypassed":
                case_bypassed = True
                
            if is_known_yes(inv_present) or (case_row and not case_bypassed and is_available(case_row.get("investigation_status"))):
                # Investigation occurred
                evaluable.append(alert)
            elif is_known_no(inv_present) or case_bypassed:
                # Confirmed NO investigation
                evaluable.append(alert)
                violation_alerts.append(alert)
            else:
                # Insufficient evidence (NOT_AVAILABLE)
                continue
                
        if not evaluable or not violation_alerts:
            continue
            
        violation_count = len(violation_alerts)
        total_evaluable = len(evaluable)
        violation_rate = violation_count / total_evaluable
        
        has_critical = any(a.get("severity") == "Critical" for a in violation_alerts)
        sev = "HIGH" if has_critical else "MEDIUM"
        
        top_asset_type = _get_top_asset_type(violation_alerts, store)
        evidence = [a['alert_id'] for a in violation_alerts]
        
        findings.append(Finding(
            finding_id=generate_finding_id(cse_id, "EG-2", 1),
            cse_id=cse_id,
            rule_id="EG-2",
            category="execution_gap",
            severity=sev,
            title="Alerts closed without investigation",
            explanation=f"Alerts required investigation, but available evidence indicates investigation did not occur. {violation_count} of {total_evaluable} evaluable alerts ({violation_rate:.0%}) lacked investigation prior to closure.",
            evidence_ids=evidence,
            metric_value=violation_rate,
            related_asset_type=top_asset_type
        ))
        
    return findings

def check_eg3_fast_closure(store: DataStore) -> list[Finding]:
    """
    EG-3: Fast closure of alerts within configured threshold.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        evaluable = []
        fast_closed = []
        
        for alert in alerts:
            if alert.get("disposition") != "Closed": 
                continue
            if alert.get("severity") not in ("Critical", "High"):
                continue
                
            try:
                mins = float(alert.get("closure_time_minutes", -1))
                # Exclude invalid negative durations (handled by DQ) or missing
                if mins >= 0 and is_available(alert.get("closure_time_minutes")):
                    alert["_mins"] = mins
                    evaluable.append(alert)
                    if mins < FAST_CLOSURE_MINUTES:
                        fast_closed.append(alert)
            except (ValueError, TypeError):
                continue
                
        if not evaluable or not fast_closed:
            continue
            
        violation_count = len(fast_closed)
        total_evaluable = len(evaluable)
        violation_rate = violation_count / total_evaluable
        
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
            title="Fast-closure supervisory signal",
            explanation=f"Alert closure occurred within the configured fast-closure threshold; examiner review may be appropriate. {violation_count} of {total_evaluable} eligible closed alerts ({violation_rate:.0%}) were resolved in under {FAST_CLOSURE_MINUTES} minutes (avg {avg_fast_time:.1f} min).",
            evidence_ids=evidence,
            metric_value=violation_rate,
            related_asset_type=top_asset_type
        ))
        
    return findings

def check_eg4_repeated_no_remediation(store: DataStore) -> list[Finding]:
    """
    EG-4: Repeated alerts without remediation progress on the same asset.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        asset_stats = {}
        for a in alerts:
            ast_id = a.get("asset_id")
            if not ast_id or not is_available(ast_id): 
                continue
                
            if ast_id not in asset_stats:
                asset_stats[ast_id] = {"total_evaluable": 0, "unremediated": 0, "evidence": []}
                
            expected = resolve_remediation_expectation(a)
            obs = a.get("remediation_present")
            
            if expected == EXPECTATION_YES and is_available(obs):
                asset_stats[ast_id]["total_evaluable"] += 1
                asset_stats[ast_id]["evidence"].append(a["alert_id"])
                if is_known_no(obs):
                    asset_stats[ast_id]["unremediated"] += 1
            
        # Evaluate violators
        finding_idx = 1
        for ast_id, stats in asset_stats.items():
            if stats["total_evaluable"] >= REPEAT_ALERT_MIN_COUNT:
                ratio = stats["unremediated"] / stats["total_evaluable"]
                if ratio >= REPEAT_UNREMEDIATED_RATIO:
                    ast_rec = store.get_asset_evidence(ast_id)
                    top_asset_type = ast_rec.get("asset_type", "Unknown") if ast_rec else "Unknown"
                    
                    findings.append(Finding(
                        finding_id=generate_finding_id(cse_id, "EG-4", finding_idx),
                        cse_id=cse_id,
                        rule_id="EG-4",
                        category="execution_gap",
                        severity="HIGH",
                        title="Repeated alerts without remediation progress",
                        explanation=f"Repeated alerts for asset {ast_id} show limited recorded remediation progress. {stats['unremediated']} of {stats['total_evaluable']} ({ratio:.0%}) evaluable alerts lacked remediation evidence.",
                        evidence_ids=[ast_id] + stats["evidence"],
                        metric_value=ratio,
                        related_asset_type=top_asset_type
                    ))
                    finding_idx += 1
                    
    return findings

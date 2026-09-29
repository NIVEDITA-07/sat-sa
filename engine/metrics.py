import pandas as pd
from engine.semantics import is_known_yes, is_available, resolve_investigation_expectation, EXPECTATION_YES

def compute_operational_escalation_rate(alerts):
    """
    Computes Escalation Rate.
    Numerator: Critical/High closed alerts with escalated = YES
    Denominator: Critical/High closed alerts with known escalation status
    """
    eligible = [
        a for a in alerts 
        if a.get("severity") in ("Critical", "High") 
        and a.get("disposition") == "Closed"
        and is_available(a.get("escalated"))
    ]
    
    if not eligible:
        return None, 0
        
    escalated = sum(1 for a in eligible if is_known_yes(a.get("escalated")))
    return escalated / len(eligible), len(eligible)

def compute_operational_investigation_rate(alerts, store):
    """
    Computes Investigation Rate.
    Numerator: Critical/High closed alerts where investigation is EXPECTED and observed to be YES.
    Denominator: Critical/High closed alerts where investigation is EXPECTED and evidence is available.
    """
    eligible = []
    investigated = 0
    
    for a in alerts:
        if a.get("disposition") != "Closed": continue
        if resolve_investigation_expectation(a) != EXPECTATION_YES: continue
        
        inv_present = a.get("investigation_present")
        case_row = store.get_case_for_alert(a.get("alert_id"))
        
        case_bypassed = case_row and case_row.get("investigation_status") == "Bypassed"
        
        # If it's explicitly YES
        if is_known_yes(inv_present) or (case_row and not case_bypassed and is_available(case_row.get("investigation_status"))):
            eligible.append(a)
            investigated += 1
        # If it's explicitly NO
        elif is_known_yes(a.get("investigation_present") == "NO") or case_bypassed:
            eligible.append(a)
            
    if not eligible:
        return None, 0
        
    return investigated / len(eligible), len(eligible)

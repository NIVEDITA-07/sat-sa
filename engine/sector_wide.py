from engine.findings import Finding
from config import CROSS_CSE_PROPORTION_THRESHOLD, CROSS_CSE_MIN_AFFECTED_CSES

def compute_sector_wide_signals(all_findings: list[Finding], cse_coverage_info: dict) -> list[dict]:
    """
    Aggregates findings to see if any specific rule affects >= CROSS_CSE_PROPORTION_THRESHOLD 
    of ELIGIBLE CSEs (excluding those with insufficient evidence for the rule).
    """
    signals = []
    
    rule_counts = {}
    rule_affected_cses = {}
    
    for f in all_findings:
        if f.rule_id not in rule_counts:
            rule_counts[f.rule_id] = 0
            rule_affected_cses[f.rule_id] = set()
            
        rule_counts[f.rule_id] += 1
        rule_affected_cses[f.rule_id].add(f.cse_id)
        
    for rule_id, affected_set in rule_affected_cses.items():
        # Calculate eligible CSEs for this rule
        eligible_count = 0
        for cse_id, cov in cse_coverage_info.items():
            rule_status = cov.get("rule_availability", {}).get(rule_id, "READY")
            if rule_status != "INSUFFICIENT EVIDENCE":
                eligible_count += 1
                
        if eligible_count == 0:
            continue
            
        affected_count = len(affected_set)
        proportion = affected_count / eligible_count
        
        if proportion >= CROSS_CSE_PROPORTION_THRESHOLD and affected_count >= CROSS_CSE_MIN_AFFECTED_CSES:
            signals.append({
                "rule_id": rule_id,
                "affected_count": affected_count,
                "eligible_count": eligible_count,
                "proportion": proportion,
                "description": f"{affected_count} of {eligible_count} evaluable CSEs ({proportion*100:.1f}%) show the same supervisory signal ({rule_id})."
            })
            
    return signals

from engine.findings import Finding
from config import SECTOR_WIDE_PROPORTION_THRESHOLD

def compute_sector_wide_signals(all_findings: list[Finding], total_cses: int) -> list[dict]:
    """
    Aggregates findings to see if any specific rule/asset combo affects >= SECTOR_WIDE_PROPORTION_THRESHOLD of CSEs.
    """
    signals = []
    
    # Group findings by rule_id
    rule_counts = {}
    rule_affected_cses = {}
    
    for f in all_findings:
        if f.rule_id not in rule_counts:
            rule_counts[f.rule_id] = 0
            rule_affected_cses[f.rule_id] = set()
            
        rule_counts[f.rule_id] += 1
        rule_affected_cses[f.rule_id].add(f.cse_id)
        
    for rule_id, cse_set in rule_affected_cses.items():
        proportion = len(cse_set) / total_cses
        if proportion >= SECTOR_WIDE_PROPORTION_THRESHOLD:
            signals.append({
                "rule_id": rule_id,
                "affected_count": len(cse_set),
                "proportion": proportion,
                "description": f"{(proportion*100):.1f}% of assessed CSEs show the same supervisory signal ({rule_id})."
            })
            
    return signals

import pandas as pd
import numpy as np
from engine.findings import Finding
from config import PEER_DEVIATION_STD_MULTIPLIER, PEER_DEVIATION_RATIO_FLOOR
from engine.data_store import DataStore

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_peer1_deviation(store: DataStore) -> list[Finding]:
    """
    PEER-1: Escalation rate deviation from peer sector baseline.
    Groups by sector, calculates operational escalation rate.
    HIGH if < 0.25 * mean, MEDIUM if < mean - k*std OR < 0.5 * mean.
    """
    findings = []
    
    # Group CSEs by sector
    sectors = {}
    
    for cse_id, profile in store._profiles_idx.items():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        crit_high = [a for a in alerts if a.get("severity") in ("Critical", "High")]
        if not crit_high:
            continue
            
        total = len(crit_high)
        escalated = sum(1 for a in crit_high if a.get("escalated") == "Yes")
        rate = escalated / total
        
        sector = profile.get("sector", "Unknown")
        if sector not in sectors:
            sectors[sector] = []
            
        sectors[sector].append({
            "cse_id": cse_id,
            "total": total,
            "rate": rate,
            "evidence": [a["alert_id"] for a in crit_high if a.get("escalated") == "No"]
        })
        
    for sector, cse_stats in sectors.items():
        if len(cse_stats) < 2:
            continue
            
        rates = [s["rate"] for s in cse_stats]
        sector_mean = sum(rates) / len(rates)
        
        # Calculate standard deviation
        if len(rates) > 1:
            variance = sum((r - sector_mean) ** 2 for r in rates) / (len(rates) - 1)
            sector_std = variance ** 0.5
        else:
            sector_std = 0
            
        threshold_std = sector_mean - (PEER_DEVIATION_STD_MULTIPLIER * sector_std)
        threshold_half = 0.5 * sector_mean
        threshold = max(threshold_std, threshold_half)
        
        for stat in cse_stats:
            if stat["rate"] < threshold and stat["total"] > 0:
                c_val = stat["rate"] * 100
                p_val = sector_mean * 100
                sev = "HIGH" if stat["rate"] < (0.25 * sector_mean) else "MEDIUM"
                
                findings.append(Finding(
                    finding_id=generate_finding_id(stat["cse_id"], "PEER-1", 1),
                    cse_id=stat["cse_id"],
                    rule_id="PEER-1",
                    category="peer_deviation",
                    severity=sev,
                    title="Potential peer deviation signal",
                    explanation=f"Critical/High escalation rate ({int(c_val)}%) is significantly below the peer baseline for sector '{sector}' ({int(p_val)}%). This is a comparative deviation signal requiring context review.",
                    evidence_ids=[stat["evidence"]],
                    metric_value=stat["rate"],
                    peer_value=sector_mean,
                    related_asset_type=None
                ))
            
    return findings

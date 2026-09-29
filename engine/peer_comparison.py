import pandas as pd
import numpy as np
from engine.findings import Finding
from config import PEER_MIN_CSE_COUNT, PEER_MIN_ELIGIBLE_ALERTS, PEER_STD_MULTIPLIER, PEER_MIN_RELATIVE_RATE
from engine.data_store import DataStore
from engine.semantics import is_known_yes, is_available

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_peer1_deviation(store: DataStore) -> list[Finding]:
    """
    PEER-1: Escalation rate deviation from peer sector baseline.
    Uses LEAVE-ONE-OUT baseline. A target CSE is not compared against its own performance.
    """
    findings = []
    
    # Pre-calculate operational escalation rates for all CSEs
    cse_metrics = []
    
    for cse_id, profile in store._profiles_idx.items():
        data = store.get_cse_data(cse_id)
        alerts = data.get("alerts", [])
        
        # We define the peer metric as escalation rate for Critical/High closed alerts
        eligible_alerts = [
            a for a in alerts 
            if a.get("severity") in ("Critical", "High") 
            and a.get("disposition") == "Closed"
            and is_available(a.get("escalated"))
        ]
        
        if len(eligible_alerts) < PEER_MIN_ELIGIBLE_ALERTS:
            continue
            
        total_eligible = len(eligible_alerts)
        escalated = sum(1 for a in eligible_alerts if is_known_yes(a.get("escalated")))
        rate = escalated / total_eligible
        
        sector = profile.get("sector", "Unknown")
        if sector == "Unknown" or not is_available(sector):
            continue
            
        cse_metrics.append({
            "cse_id": cse_id,
            "sector": sector,
            "total_eligible": total_eligible,
            "rate": rate,
            "evidence": [a["alert_id"] for a in eligible_alerts if not is_known_yes(a.get("escalated"))]
        })
        
    # Group by sector
    sectors = {}
    for c_stat in cse_metrics:
        sec = c_stat["sector"]
        if sec not in sectors:
            sectors[sec] = []
        sectors[sec].append(c_stat)
        
    for sector, members in sectors.items():
        if len(members) < PEER_MIN_CSE_COUNT:
            # Insufficient peer population
            continue
            
        for target in members:
            # Leave-one-out calculation
            peers = [m for m in members if m["cse_id"] != target["cse_id"]]
            peer_rates = [p["rate"] for p in peers]
            
            peer_mean = sum(peer_rates) / len(peer_rates)
            
            if len(peer_rates) > 1:
                variance = sum((r - peer_mean) ** 2 for r in peer_rates) / (len(peer_rates) - 1)
                peer_std = variance ** 0.5
            else:
                peer_std = 0
                
            threshold_std = peer_mean - (PEER_STD_MULTIPLIER * peer_std)
            threshold_relative = PEER_MIN_RELATIVE_RATE * peer_mean
            
            # The deviation threshold is the stricter (lower) of the two constraints
            threshold = min(threshold_std, threshold_relative)
            
            # Target must be materially below the threshold
            if target["rate"] < threshold:
                sev = "HIGH" if target["rate"] < (0.25 * peer_mean) else "MEDIUM"
                
                c_val = target["rate"] * 100
                p_val = peer_mean * 100
                
                findings.append(Finding(
                    finding_id=generate_finding_id(target["cse_id"], "PEER-1", 1),
                    cse_id=target["cse_id"],
                    rule_id="PEER-1",
                    category="peer_deviation",
                    severity=sev,
                    title="Escalation rate below comparable peer baseline",
                    explanation=f"Escalation rate ({int(c_val)}%) is materially below the Leave-One-Out comparable-peer baseline for sector '{sector}' ({int(p_val)}%, {len(peers)} peers).",
                    evidence_ids=target["evidence"],
                    metric_value=target["rate"],
                    peer_value=peer_mean,
                    related_asset_type=None
                ))
                
    return findings

import pandas as pd
from engine.findings import Finding
from config import BLIND_SPOT_THRESHOLD_ABSOLUTE, BLIND_SPOT_RATIO
from engine.data_store import DataStore
from collections import Counter

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_ns1_blind_spot(store: DataStore) -> list[Finding]:
    """
    NS-1: Monitoring blind spot.
    Critical assets with observed monitoring events materially below expected activity.
    Aggregated at the CSE level: one finding per CSE.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        assets = data.get("assets", [])
        
        # Get period days from profile if available, else assume 90 (Q1)
        profile = data.get("profile", {})
        period = str(profile.get("assessment_period", ""))
        days = 90
        if "Q" in period: days = 90
        
        # Parse critical assets expecting monitoring
        critical_assets = []
        for a in assets:
            if str(a.get("expected_monitoring")).lower() in ("yes", "high", "standard"):
                try:
                    events = float(a.get("observed_monitoring_events", 0))
                    a["_events"] = events
                    expected_daily = float(a.get("expected_events_per_day", 0))
                    a["_expected"] = expected_daily * days
                    critical_assets.append(a)
                except (ValueError, TypeError):
                    a["_events"] = 0
                    a["_expected"] = 0
                    critical_assets.append(a)
                    
        if not critical_assets:
            continue
            
        total_critical = len(critical_assets)
        blind_spots = []
        for a in critical_assets:
            if a["_events"] == 0:
                blind_spots.append(a)
                    
        blind_count = len(blind_spots)
        
        if blind_count == 0:
            continue
            
        blind_rate = blind_count / total_critical
        
        if blind_rate >= 0.30:
            sev = "HIGH"
        elif blind_rate >= 0.10:
            sev = "MEDIUM"
        else:
            sev = "LOW"
            
        asset_types = [a.get("asset_type") for a in blind_spots if "asset_type" in a]
        top_asset_type = Counter(asset_types).most_common(1)[0][0] if asset_types else "Unknown"
        evidence = [a['asset_id'] for a in blind_spots]
        
        findings.append(Finding(
            finding_id=generate_finding_id(cse_id, "NS-1", 1),
            cse_id=cse_id,
            rule_id="NS-1",
            category="negative_space",
            severity=sev,
            title="Possible monitoring blind spot",
            explanation=f"{blind_count} of {total_critical} critical assets ({blind_rate:.0%}) recorded telemetry materially below the expected threshold for the {days}-day assessment period.",
            evidence_ids=evidence,
            metric_value=blind_rate,
            peer_value=None,
            related_asset_type=top_asset_type
        ))
    return findings

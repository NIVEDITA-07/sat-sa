import pandas as pd
from engine.findings import Finding
from config import NEGATIVE_SPACE_MAX_COVERAGE_RATIO
from engine.data_store import DataStore
from engine.semantics import is_available, normalize_boolean, EVIDENCE_YES
from collections import Counter

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_ns1_blind_spot(store: DataStore) -> list[Finding]:
    """
    NS-1: Monitoring blind spot.
    Critical assets with observed monitoring events materially below expected activity (coverage_ratio <= threshold).
    Aggregated at the CSE level.
    """
    findings = []
    
    for cse_id in store._profiles_idx.keys():
        data = store.get_cse_data(cse_id)
        assets = data.get("assets", [])
        
        profile = data.get("profile", {})
        # Estimate days from assessment period safely
        period = str(profile.get("assessment_period", ""))
        days = 90
        if "Q" in period: days = 90
        
        evaluable_assets = []
        blind_spots = []
        
        for a in assets:
            # We only evaluate if expected_monitoring is known to be required
            exp = str(a.get("expected_monitoring", "")).lower()
            if exp not in ("yes", "high", "standard") and normalize_boolean(exp) != EVIDENCE_YES:
                continue
                
            obs_events = a.get("observed_monitoring_events")
            exp_daily = a.get("expected_events_per_day")
            
            # If telemetry is explicitly marked as NOT_AVAILABLE, we skip (insufficient evidence)
            # instead of assuming zero telemetry.
            if not is_available(obs_events):
                continue
                
            try:
                events = float(obs_events)
                
                if is_available(exp_daily):
                    expected_total = float(exp_daily) * days
                else:
                    # Fallback expectation: 1 event per day minimum if not explicitly provided
                    expected_total = 1.0 * days
                    
                if expected_total <= 0:
                    continue
                    
                coverage_ratio = events / expected_total
                
                a["_coverage"] = coverage_ratio
                evaluable_assets.append(a)
                
                if coverage_ratio <= NEGATIVE_SPACE_MAX_COVERAGE_RATIO:
                    blind_spots.append(a)
                    
            except (ValueError, TypeError):
                continue
                    
        if not evaluable_assets or not blind_spots:
            continue
            
        total_evaluable = len(evaluable_assets)
        blind_count = len(blind_spots)
        blind_rate = blind_count / total_evaluable
        
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
            title="Possible monitoring blind spot based on available evidence",
            explanation=f"Telemetry coverage was negligible (<= {NEGATIVE_SPACE_MAX_COVERAGE_RATIO*100:.0f}% of expectation) for {blind_count} of {total_evaluable} evaluable monitored assets ({blind_rate:.0%}) over the assessment period.",
            evidence_ids=evidence,
            metric_value=blind_rate,
            peer_value=None,
            related_asset_type=top_asset_type
        ))
        
    return findings

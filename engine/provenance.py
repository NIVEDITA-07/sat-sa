import hashlib
import json
from datetime import datetime, timezone
from engine.findings import Finding, FindingProvenance, EvidenceLineage
from engine.data_store import DataStore
import config

# Provide a mapping of rules to the fields they care about
RULE_EVIDENCE_FIELDS = {
    "EG-1": ["severity", "disposition", "escalated"],
    "EG-2": ["severity", "disposition", "investigation_present", "investigation_status"],
    "EG-3": ["severity", "disposition", "closure_time_minutes"],
    "EG-4": ["remediation_present"],
    "NS-1": ["expected_monitoring", "observed_monitoring_events", "expected_events_per_day"],
    "PEER-1": ["severity", "disposition", "escalated"],
    "T-1": ["severity", "disposition", "investigation_present", "investigation_status", "created_at"],
    "K-1": ["reported_escalation_rate", "reported_investigation_rate"],
    "I-1": ["investigation_note", "investigator_id"],
    "DQ-1": ["alert_id"],
    "DQ-2": ["severity"],
    "DQ-3": ["closure_time_minutes"],
    "DQ-4": ["alert_id"],
    "DQ-5": ["case_id"],
}

# Provide rule versions
RULE_VERSIONS = {
    "EG-1": "v1.0",
    "EG-2": "v1.0",
    "EG-3": "v1.0",
    "EG-4": "v1.0",
    "NS-1": "v1.0",
    "PEER-1": "v1.0",
    "T-1": "v1.0",
    "K-1": "v1.0",
    "I-1": "v1.0",
    "DQ-1": "v1.0",
    "DQ-2": "v1.0",
    "DQ-3": "v1.0",
    "DQ-4": "v1.0",
    "DQ-5": "v1.0",
}

def get_config_hash() -> str:
    """Generate a deterministic hash of the current analytical configuration."""
    conf = {
        k: getattr(config, k) for k in dir(config)
        if not k.startswith("__") and isinstance(getattr(config, k), (int, float, str, dict))
    }
    return hashlib.md5(json.dumps(conf, sort_keys=True).encode("utf-8")).hexdigest()[:8]

def build_evidence_lineage(store: DataStore, evidence_ids: list[str], rule_id: str, ingestion_meta: dict) -> list[EvidenceLineage]:
    """Resolves evidence IDs back to source records and extracts relevant fields."""
    lineage = []
    relevant_keys = RULE_EVIDENCE_FIELDS.get(rule_id, [])
    
    # We don't want to add thousands of evidence items to a single finding for performance.
    # Cap detailed lineage to the first 50 items.
    capped_evidence = evidence_ids[:50]
    
    source_name = ingestion_meta.get("provenance", {}).get("source_name", "Unknown Source")
    source_type = ingestion_meta.get("provenance", {}).get("type", "Unknown Type")
    
    for eid in capped_evidence:
        record_type = None
        record = None
        
        # Determine the type by checking DataStore indexes
        if eid in store._alerts_idx:
            record_type = "alert"
            record = store.get_alert_evidence(eid)
        elif eid in store._cases_idx:
            record_type = "case"
            record = store.get_case_evidence(eid)
        elif eid in store._assets_idx:
            record_type = "asset"
            record = store.get_asset_evidence(eid)
        elif eid in store._profiles_idx:
            record_type = "profile"
            record = store.get_cse_data(eid).get("profile", {})
            
        if not record:
            continue
            
        # Extract only the fields relevant to the rule that fired
        relevant = {k: record.get(k) for k in relevant_keys if k in record}
        
        # Include primary keys for context
        for pk in ["alert_id", "case_id", "asset_id", "cse_id"]:
            if pk in record and pk not in relevant:
                relevant[pk] = record[pk]
                
        lineage.append(EvidenceLineage(
            source_name=source_name,
            source_type=source_type,
            source_record_id=eid,  # using canonical id as source representation since they map 1:1
            normalized_record_id=f"{record_type}:{eid}",
            record_type=record_type,
            relevant_fields=relevant
        ))
        
    return lineage

def attach_provenance(findings: list[Finding], store: DataStore, ingestion_meta: dict) -> list[Finding]:
    """Attaches formal lineage and provenance to a list of findings."""
    analysis_time = datetime.now(timezone.utc).isoformat()
    config_version = f"cfg-{get_config_hash()}"
    assessment_id = ingestion_meta.get("provenance", {}).get("ingestion_timestamp", analysis_time)
    
    for f in findings:
        r_id = f.rule_id
        # Build aggregate context for aggregate rules
        aggregate_context = {}
        if r_id == "PEER-1":
            aggregate_context = {
                "metric_type": "escalation_rate",
                "cse_metric": f.metric_value,
                "peer_mean": f.peer_value,
                "threshold_used": getattr(config, "PEER_MIN_RELATIVE_RATE", 0.5)
            }
        elif r_id == "T-1":
            aggregate_context = {
                "metric_type": "investigation_rate",
                "drift": f.metric_value,
                "threshold_used": getattr(config, "TEMPORAL_DRIFT_THRESHOLD", 0.20)
            }
        elif r_id == "K-1":
            aggregate_context = {
                "metric_type": "kpi_contradiction",
                "difference": f.metric_value,
                "threshold_used": getattr(config, "KPI_CONTRADICTION_THRESHOLD", 0.15)
            }
        
        f.provenance = FindingProvenance(
            rule_version=f"{r_id}:{RULE_VERSIONS.get(r_id, 'v1.0')}",
            assessment_id=f"run-{hashlib.md5(assessment_id.encode()).hexdigest()[:8]}",
            analysis_timestamp=analysis_time,
            configuration_version=config_version,
            evidence_lineage=build_evidence_lineage(store, f.evidence_ids, r_id, ingestion_meta),
            aggregate_context=aggregate_context
        )
        
    return findings

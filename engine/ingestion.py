import pandas as pd
import numpy as np

CANONICAL_ALERTS = ['alert_id', 'cse_id', 'asset_id', 'severity', 'created_at', 'created_time', 'ack_time', 'closure_time_minutes', 'closed_at', 'disposition', 'escalated', 'investigation_present', 'remediation_present', 'reopened']
CANONICAL_ASSETS = ['asset_id', 'cse_id', 'criticality', 'asset_type', 'expected_monitoring', 'observed_monitoring_events', 'expected_events_per_day']
CANONICAL_CASES = ['case_id', 'cse_id', 'alert_id', 'investigation_start', 'investigation_end', 'escalation_status', 'closure_status', 'investigation_note', 'investigator_id']

def get_source_profiles():
    # Base canonical maps that map the new CSV files to the engine
    # IMPORTANT: Raw CSV has `status` (Closed/Open) and `disposition` (True Positive/False Positive)
    # The engine rules check `disposition == 'Closed'` meaning "was this alert closed"
    # So we map `status` → `disposition` for the engine
    new_alerts_map = {
        "alert_id": "alert_id",
        "cse_id": "cse_id",
        "asset_id": "asset_id",
        "severity": "severity",
        "created_at": "created_at",
        "acknowledged_at": "ack_time",
        "closed_at": "closed_at",
        "status": "disposition",
        "escalated": "escalated",
        "investigation_present": "investigation_present",
        "reopened": "reopened",
        # closure_time_minutes and remediation_present are computed dynamically below
    }
    new_cases_map = {
        "case_id": "case_id",
        "cse_id": "cse_id",
        "primary_alert_id": "alert_id",
        "investigation_started_at": "investigation_start",
        "investigation_completed_at": "investigation_end",
        "escalation_level": "escalation_status",
        "closure_reason": "closure_status",
        "investigation_note": "investigation_note",
        "investigator_id": "investigator_id"
    }
    
    return {
        "CONTROLLED_DEMO": {
            "name": "SAT-SA Controlled Demonstration Dataset",
            "type": "Synthetic / Controlled",
            "alerts_map": new_alerts_map,
            "assets_map": {k: k for k in CANONICAL_ASSETS},
            "cases_map": new_cases_map
        },
        "PUBLIC_SOC": {
            "name": "SecAlertBench (Public SOC Sample)",
            "type": "Public Cybersecurity Dataset",
            "alerts_map": {
                "event_id": "alert_id",
                "org_id": "cse_id",
                "hostname": "asset_id",
                "priority": "severity",
                "event_time": "created_time",
                "ticket_status": "disposition",
            },
            "assets_map": {
                "hostname": "asset_id",
                "org_id": "cse_id",
                "importance": "criticality",
                "device_class": "asset_type",
                "log_count": "observed_monitoring_events"
            },
            "cases_map": {}
        },
        "CSE_SUBMISSION": {
            "name": "Uploaded SOC Export",
            "type": "CSE Submission",
            "alerts_map": new_alerts_map,
            "assets_map": {k: k for k in CANONICAL_ASSETS},
            "cases_map": new_cases_map
        }
    }

def normalize_dataset(raw_df: pd.DataFrame, mapping: dict, canonical_columns: list) -> tuple[pd.DataFrame, list[dict]]:
    df = pd.DataFrame()
    mapping_status = []
    
    if raw_df is None or raw_df.empty:
        df = pd.DataFrame(columns=canonical_columns)
        for can_col in canonical_columns:
            mapping_status.append({"source_field": "—", "sat_sa_field": can_col, "status": "⚠ Not Available"})
        return df, mapping_status

    for raw_col, can_col in mapping.items():
        if raw_col in raw_df.columns:
            df[can_col] = raw_df[raw_col]
            mapping_status.append({"source_field": raw_col, "sat_sa_field": can_col, "status": "✓ Mapped"})
        else:
            mapping_status.append({"source_field": raw_col, "sat_sa_field": can_col, "status": "✕ Missing from source"})
            
    for col in raw_df.columns:
        if col not in mapping:
            mapping_status.append({"source_field": col, "sat_sa_field": "—", "status": "Not Used"})
            
    for can_col in canonical_columns:
        if can_col not in df.columns:
            df[can_col] = "NOT_AVAILABLE"
            mapping_status.append({"source_field": "—", "sat_sa_field": can_col, "status": "⚠ Not Available"})
            
    # Handle NaN values for canonical columns to NOT_AVAILABLE
    df = df.fillna("NOT_AVAILABLE")
    return df, mapping_status

def ingest_data(alerts_df: pd.DataFrame, assets_df: pd.DataFrame, cases_df: pd.DataFrame, profile_key: str, cse_profiles_df: pd.DataFrame = None) -> dict:
    """
    Ingests heterogeneous SOC data, applies the source profile mapping,
    and returns a canonical internal SAT-SA model dataset.
    """
    profiles = get_source_profiles()
    profile = profiles.get(profile_key, profiles["CONTROLLED_DEMO"])
    
    # Pre-normalization transformations
    if alerts_df is not None and not alerts_df.empty:
        # Compute closure_time_minutes if we have timestamps
        if 'created_at' in alerts_df.columns and 'closed_at' in alerts_df.columns:
            created = pd.to_datetime(alerts_df['created_at'], errors='coerce')
            closed = pd.to_datetime(alerts_df['closed_at'], errors='coerce')
            alerts_df['closure_time_minutes'] = (closed - created).dt.total_seconds() / 60.0
            profile["alerts_map"]["closure_time_minutes"] = "closure_time_minutes"
            
        # Map remediation_status to remediation_present
        # Raw values: 'Closed' = remediation done, 'Open' = remediation NOT done
        if 'remediation_status' in alerts_df.columns:
            def map_rem(val):
                if pd.isna(val) or str(val).strip() == "": return "NOT_AVAILABLE"
                val_str = str(val).strip()
                if val_str == "Closed": return "Yes"
                if val_str == "Open": return "No"
                return "NOT_AVAILABLE"
            alerts_df['remediation_present'] = alerts_df['remediation_status'].apply(map_rem)
            profile["alerts_map"]["remediation_present"] = "remediation_present"

    norm_alerts, map_alerts = normalize_dataset(alerts_df, profile["alerts_map"], CANONICAL_ALERTS)
    norm_assets, map_assets = normalize_dataset(assets_df, profile["assets_map"], CANONICAL_ASSETS)
    norm_cases, map_cases = normalize_dataset(cases_df, profile["cases_map"], CANONICAL_CASES)
    
    from datetime import datetime
    
    return {
        "alerts_df": norm_alerts,
        "assets_df": norm_assets,
        "cases_df": norm_cases,
        "cse_profiles_df": cse_profiles_df,
        "mapping_status": map_alerts + map_assets + map_cases,
        "provenance": {
            "source_type": profile_key,
            "source_name": profile["name"],
            "type": profile["type"],
            "records": len(norm_alerts) + len(norm_assets) + len(norm_cases),
            "ingestion_timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }

import pandas as pd
import numpy as np

def validate_schema(alerts_df: pd.DataFrame, assets_df: pd.DataFrame, cases_df: pd.DataFrame) -> bool:
    """
    Validates required columns, datatypes, and referential integrity of the data.
    """
    # 1. Required Columns
    req_alerts = {'alert_id', 'cse_id', 'asset_id', 'severity', 'closure_time_minutes', 'disposition', 'escalated', 'investigation_present', 'remediation_present'}
    req_assets = {'asset_id', 'cse_id', 'criticality', 'asset_type', 'expected_monitoring', 'observed_monitoring_events'}
    req_cases = {'case_id', 'alert_id', 'escalation_status', 'closure_status'}
    
    if not req_alerts.issubset(alerts_df.columns):
        raise ValueError(f"Alerts DataFrame is missing columns. Expected {req_alerts}")
    if not req_assets.issubset(assets_df.columns):
        raise ValueError(f"Assets DataFrame is missing columns. Expected {req_assets}")
    if not req_cases.issubset(cases_df.columns):
        raise ValueError(f"Cases DataFrame is missing columns. Expected {req_cases}")
        
    # 2. Enum validations
    valid_severities = {'Critical', 'High', 'Medium', 'Low', 'NOT_AVAILABLE'}
    invalid_sev = set(alerts_df['severity'].unique()) - valid_severities
    if invalid_sev:
        raise ValueError(f"Invalid severities found in alerts: {invalid_sev}")
        
    valid_crit = {'Critical', 'High', 'Medium', 'Low', 'NOT_AVAILABLE'}
    invalid_crit = set(assets_df['criticality'].unique()) - valid_crit
    if invalid_crit:
        raise ValueError(f"Invalid criticalities found in assets: {invalid_crit}")

    # 3. Referential Integrity
    # In a real-world MVP, raw SOC data is often dirty. We should log warnings rather than crashing.
    missing_assets = set(alerts_df['asset_id']) - set(assets_df['asset_id'])
    if missing_assets and list(missing_assets) != ['NOT_AVAILABLE']:
        print(f"Warning: {len(missing_assets)} asset_ids in alerts are missing from assets.")
        
    missing_alerts = set(cases_df['alert_id']) - set(alerts_df['alert_id'])
    if missing_alerts and list(missing_alerts) != ['NOT_AVAILABLE']:
        print(f"Warning: {len(missing_alerts)} alert_ids in cases are missing from alerts.")

    return True

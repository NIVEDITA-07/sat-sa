from engine.data_store import DataStore
from engine.findings import Finding
import pandas as pd

def check_data_quality(store: DataStore) -> list[Finding]:
    """
    Detects data quality issues in the alerts such as:
    - DQ-1: Duplicate alerts
    - DQ-2: Missing severity
    - DQ-3: Impossible lifecycle (negative closure time)
    """
    findings = []
    
    # Check for Duplicate Alerts
    # We can group by alert_id to find duplicates
    alerts_df = store.alerts_df
    
    if not alerts_df.empty:
        # DQ-1: Duplicate alerts
        dup_alerts = alerts_df[alerts_df.duplicated(subset=['alert_id'], keep=False)]
        dup_ids = dup_alerts['alert_id'].unique()
        for aid in dup_ids:
            # Create finding for the CSE of the first occurrence
            cse_id = dup_alerts[dup_alerts['alert_id'] == aid]['cse_id'].iloc[0]
            findings.append(Finding(
                finding_id=f"DQ1-{aid}",
                cse_id=cse_id,
                rule_id="DQ-1",
                category="data_quality",
                severity="LOW",
                title="Duplicate alert record",
                explanation=f"Alert {aid} appears multiple times in the dataset.",
                evidence_ids=[str(aid)]
            ))
            
        # DQ-2: Missing severity
        # If severity is null or "NOT_AVAILABLE"
        missing_sev = alerts_df[alerts_df['severity'].isna() | (alerts_df['severity'] == "NOT_AVAILABLE") | (alerts_df['severity'] == "")]
        for _, row in missing_sev.iterrows():
            aid = row.get("alert_id")
            cse_id = row.get("cse_id")
            findings.append(Finding(
                finding_id=f"DQ2-{aid}",
                cse_id=cse_id,
                rule_id="DQ-2",
                category="data_quality",
                severity="LOW",
                title="Missing severity",
                explanation=f"Alert {aid} does not have a valid severity assigned.",
                evidence_ids=[str(aid)]
            ))
            
        # DQ-3: Impossible lifecycle
        # If closure time < 0
        if "closure_time_minutes" in alerts_df.columns:
            # Filter valid numerics
            valid_time = alerts_df[pd.to_numeric(alerts_df["closure_time_minutes"], errors="coerce").notna()]
            negative_time = valid_time[valid_time["closure_time_minutes"].astype(float) < 0]
            for _, row in negative_time.iterrows():
                aid = row.get("alert_id")
                cse_id = row.get("cse_id")
                findings.append(Finding(
                    finding_id=f"DQ3-{aid}",
                    cse_id=cse_id,
                    rule_id="DQ-3",
                    category="data_quality",
                    severity="MEDIUM",
                    title="Impossible lifecycle sequence",
                    explanation=f"Alert {aid} has a negative closure time.",
                    evidence_ids=[str(aid)]
                ))
                
    return findings

from engine.data_store import DataStore
from engine.findings import Finding
import pandas as pd

def generate_finding_id(cse_id: str, rule_id: str, index: int) -> str:
    return f"{cse_id}-{rule_id.replace('-', '')}-{index:03d}"

def check_data_quality(store: DataStore) -> list[Finding]:
    """
    Detects data quality issues (DQ-1 to DQ-8).
    Findings are aggregated by CSE + Rule to prevent cardinality explosion.
    """
    findings = []
    alerts_df = store.alerts_df
    cases_df = store.cases_df
    
    if alerts_df.empty: return findings
    
    for cse_id in store._profiles_idx.keys():
        cse_alerts = alerts_df[alerts_df['cse_id'] == cse_id] if 'cse_id' in alerts_df.columns else pd.DataFrame()
        cse_cases = cases_df[cases_df['cse_id'] == cse_id] if not cases_df.empty and 'cse_id' in cases_df.columns else pd.DataFrame()
        
        if cse_alerts.empty: continue
        
        # DQ-1 & DQ-6: Duplicate and Conflicting alerts
        dup_alerts = cse_alerts[cse_alerts.duplicated(subset=['alert_id'], keep=False)]
        if not dup_alerts.empty:
            dup_ids = list(dup_alerts['alert_id'].unique())
            findings.append(Finding(
                finding_id=generate_finding_id(cse_id, "DQ-1", 1),
                cse_id=cse_id,
                rule_id="DQ-1",
                category="data_quality",
                severity="LOW",
                title="Duplicate alert records",
                explanation=f"{len(dup_ids)} distinct alert IDs appear multiple times in the dataset.",
                evidence_ids=dup_ids[:20] # Cap evidence IDs
            ))
            
        # DQ-2: Missing severity
        missing_sev = cse_alerts[cse_alerts['severity'].isna() | (cse_alerts['severity'] == "NOT_AVAILABLE") | (cse_alerts['severity'] == "")]
        if not missing_sev.empty:
            missing_ids = list(missing_sev['alert_id'].unique())
            findings.append(Finding(
                finding_id=generate_finding_id(cse_id, "DQ-2", 1),
                cse_id=cse_id,
                rule_id="DQ-2",
                category="data_quality",
                severity="LOW",
                title="Missing alert severity",
                explanation=f"{len(missing_ids)} alerts do not have a valid severity assigned.",
                evidence_ids=missing_ids[:20]
            ))
            
        # DQ-3 & DQ-8: Impossible lifecycle / Invalid timestamps
        if "closure_time_minutes" in cse_alerts.columns:
            valid_time = cse_alerts[pd.to_numeric(cse_alerts["closure_time_minutes"], errors="coerce").notna()]
            negative_time = valid_time[valid_time["closure_time_minutes"].astype(float) < 0]
            if not negative_time.empty:
                neg_ids = list(negative_time['alert_id'].unique())
                findings.append(Finding(
                    finding_id=generate_finding_id(cse_id, "DQ-3", 1),
                    cse_id=cse_id,
                    rule_id="DQ-3",
                    category="data_quality",
                    severity="MEDIUM",
                    title="Impossible lifecycle sequence",
                    explanation=f"{len(neg_ids)} alerts have negative closure time (closed before creation).",
                    evidence_ids=neg_ids[:20]
                ))
                
        # DQ-4: Orphan references (Cases pointing to missing alerts)
        if not cse_cases.empty and 'alert_id' in cse_cases.columns:
            orphan_cases = cse_cases[~cse_cases['alert_id'].isin(cse_alerts['alert_id'])]
            if not orphan_cases.empty:
                orphan_ids = list(orphan_cases['case_id'].unique())
                findings.append(Finding(
                    finding_id=generate_finding_id(cse_id, "DQ-4", 1),
                    cse_id=cse_id,
                    rule_id="DQ-4",
                    category="data_quality",
                    severity="MEDIUM",
                    title="Orphan case references",
                    explanation=f"{len(orphan_ids)} cases reference an alert_id that does not exist in the dataset.",
                    evidence_ids=orphan_ids[:20]
                ))
                
        # DQ-5: Duplicate case IDs
        if not cse_cases.empty and 'case_id' in cse_cases.columns:
            dup_cases = cse_cases[cse_cases.duplicated(subset=['case_id'], keep=False)]
            if not dup_cases.empty:
                dup_case_ids = list(dup_cases['case_id'].unique())
                findings.append(Finding(
                    finding_id=generate_finding_id(cse_id, "DQ-5", 1),
                    cse_id=cse_id,
                    rule_id="DQ-5",
                    category="data_quality",
                    severity="LOW",
                    title="Duplicate case records",
                    explanation=f"{len(dup_case_ids)} distinct case IDs appear multiple times in the dataset.",
                    evidence_ids=dup_case_ids[:20]
                ))
                
    return findings

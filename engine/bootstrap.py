import os
import pandas as pd
from engine.pipeline import run_analytical_engine
from engine.ingestion import ingest_data

def generate_scenario(scenario_name: str):
    alerts = pd.DataFrame([{
        "alert_id": "ALT-1", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": "Critical",
        "created_time": "2026-09-01T10:00:00Z", "ack_time": "2026-09-01T10:05:00Z",
        "closure_time_minutes": 120, "disposition": "Closed",
        "escalated": "Yes", "investigation_present": "Yes", "remediation_present": "Yes"
    }])
    assets = pd.DataFrame([{
        "asset_id": "AST-1", "cse_id": "CSE-1", "criticality": "Critical",
        "asset_type": "Server", "expected_monitoring": "Yes", "observed_monitoring_events": 100
    }])
    cases = pd.DataFrame([{
        "case_id": "CAS-1", "alert_id": "ALT-1", "investigation_start": "2026-09-01T10:05:00Z",
        "investigation_end": "2026-09-01T11:00:00Z", "escalation_status": "Tier-2", "closure_status": "Resolved"
    }])
    
    if scenario_name == "Critical Alert / No Escalation":
        alerts.loc[0, "escalated"] = "No"
    elif scenario_name == "Missing Investigation":
        alerts.loc[0, "investigation_present"] = "No"
    elif scenario_name == "Fast Closure":
        alerts.loc[0, "closure_time_minutes"] = 5
    elif scenario_name == "Repeated Alerts / No Remediation":
        alerts = pd.concat([alerts, alerts.copy(), alerts.copy()]).reset_index(drop=True)
        alerts.loc[:, "alert_id"] = ["ALT-1", "ALT-2", "ALT-3"]
        alerts.loc[:, "remediation_present"] = "No"
    elif scenario_name == "Monitoring Blind Spot":
        assets.loc[0, "observed_monitoring_events"] = 0
    elif scenario_name == "Peer Deviation":
        alerts.loc[0, "escalated"] = "No"
    elif scenario_name == "Multi-CSE Systemic Signal":
        alerts.loc[0, "remediation_present"] = "No"
        
    return alerts, assets, cases

def load_and_run_pipeline(profile_key: str = "CONTROLLED_DEMO", alerts_df=None, assets_df=None, cases_df=None, cse_profiles_df=None, scenario: str = None) -> dict:
    """
    Bootstraps the application by running the ingestion layer and analytical engine.
    If DataFrames are None, loads default CSVs from disk for the demo.
    """
    if alerts_df is None or assets_df is None or cases_df is None or cse_profiles_df is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        
        # Load profiles
        try:
            cse_profiles_df = pd.read_csv(os.path.join(data_dir, "cse_profiles.csv"))
        except FileNotFoundError:
            cse_profiles_df = pd.DataFrame()
            
        if scenario and scenario != "None" and scenario != "Healthy SOC":
            alerts_df, assets_df, cases_df = generate_scenario(scenario)
            files_map = {}
        else:
            # Load the base static dataset (the controlled demo data generated in Phase 2)
            alerts_path = os.path.join(data_dir, "alerts.csv")
            assets_path = os.path.join(data_dir, "assets.csv")
            cases_path = os.path.join(data_dir, "cases.csv")
            cse_profiles_path = os.path.join(data_dir, "cse_profiles.csv")
            
            alerts_df = pd.read_csv(alerts_path)
            assets_df = pd.read_csv(assets_path)
            cases_df = pd.read_csv(cases_path)
            
            files_map = {
                "alerts.csv": alerts_path,
                "assets.csv": assets_path,
                "cases.csv": cases_path,
                "cse_profiles.csv": cse_profiles_path
            }

            if profile_key == "PUBLIC_SOC":
                # For the public demo, let's simulate missing columns by dropping some from the loaded dataset
                # and renaming some to match the "PUBLIC_SOC" mapping expectations.
                alerts_df = alerts_df.rename(columns={"alert_id": "event_id", "cse_id": "org_id", "asset_id": "hostname", "severity": "priority", "created_time": "event_time", "disposition": "ticket_status"})
                alerts_df = alerts_df.drop(columns=["escalated", "investigation_present", "remediation_present"], errors="ignore")
                
                assets_df = assets_df.rename(columns={"asset_id": "hostname", "cse_id": "org_id", "criticality": "importance", "asset_type": "device_class", "observed_monitoring_events": "log_count"})
                # drop cases entirely for public SOC
                cases_df = pd.DataFrame()
            
    # 1. Ingest & Normalize
    ingestion_payload = ingest_data(alerts_df, assets_df, cases_df, profile_key, cse_profiles_df=cse_profiles_df)
    
    # 2. Build the Data Relationship Layer (DataStore)
    from engine.data_store import DataStore
    store = DataStore()
    store.load_cse_profiles(ingestion_payload["cse_profiles_df"])
    store.load_assets(ingestion_payload["assets_df"])
    store.load_alerts(ingestion_payload["alerts_df"])
    store.load_cases(ingestion_payload["cases_df"])
    
    # 3. Execute the deterministic mathematical rules via DataStore
    results = run_analytical_engine(
        store,
        ingestion_meta={
            "mapping_status": ingestion_payload["mapping_status"],
            "provenance": ingestion_payload["provenance"]
        }
    )
    results["data_store"] = store
    
    # 3. Independent Validation
    from engine.validation import load_ground_truth, validate_findings
    gt_df = load_ground_truth()
    # 4. Integrity Capture & Verification
    assessment_id = "SATSA-2026-001" # Fixed assessment ID for demo MVP
    ingestion_payload["provenance"]["assessment_id"] = assessment_id
    
    integrity_result = None
    if "files_map" in locals() and files_map:
        from engine.integrity import capture_assessment_integrity, verify_assessment_integrity, get_manifest_path
        import os
        
        manifest_path = get_manifest_path(assessment_id)
        if not os.path.exists(manifest_path):
            capture_assessment_integrity(assessment_id, files_map)
            
        integrity_result = verify_assessment_integrity(assessment_id, files_map)
        
    results["integrity"] = integrity_result
    
    return results

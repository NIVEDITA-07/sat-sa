import unittest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.execution_gaps import (
    check_eg1_critical_no_escalation,
    check_eg2_missing_investigation,
    check_eg3_fast_closure,
    check_eg4_repeated_no_remediation
)
from engine.negative_space import check_ns1_blind_spot
from engine.peer_comparison import check_peer1_deviation

class TestAnalyticalEngine(unittest.TestCase):

    def setUp(self):
        # Base DataFrames for testing
        self.assets_df = pd.DataFrame([
            {"asset_id": "AST-01", "cse_id": "CSE-A", "criticality": "Critical", "asset_type": "Firewall", "expected_monitoring": "Yes", "observed_monitoring_events": 50},
            {"asset_id": "AST-02", "cse_id": "CSE-A", "criticality": "Critical", "asset_type": "DNS", "expected_monitoring": "Yes", "observed_monitoring_events": 1}, # Blind spot!
            {"asset_id": "AST-03", "cse_id": "CSE-B", "criticality": "High", "asset_type": "Web", "expected_monitoring": "Yes", "observed_monitoring_events": 20}
        ])

    def test_eg1_critical_no_escalation(self):
        alerts_df = pd.DataFrame([
            {"alert_id": "A-01", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "Critical", "disposition": "Closed", "escalated": "No", "closure_time_minutes": 60, "investigation_present": "Yes", "remediation_present": "Yes"}, # Violator
            {"alert_id": "A-02", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "Critical", "disposition": "Closed", "escalated": "Yes", "closure_time_minutes": 60, "investigation_present": "Yes", "remediation_present": "Yes"}, # Good
            {"alert_id": "A-03", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "Low", "disposition": "Closed", "escalated": "No", "closure_time_minutes": 60, "investigation_present": "Yes", "remediation_present": "Yes"} # Good (Not critical)
        ])
        
        from engine.data_store import DataStore
        store = DataStore()
        store.load_cse_profiles(pd.DataFrame([{"cse_id": "CSE-A"}]))
        store.load_assets(self.assets_df)
        store.load_alerts(alerts_df)
        
        findings = check_eg1_critical_no_escalation(store)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].evidence_ids[0], "A-01")

    def test_eg2_missing_investigation(self):
        alerts_df = pd.DataFrame([
            {"alert_id": "A-01", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "High", "disposition": "Closed", "escalated": "Yes", "investigation_present": "No", "closure_time_minutes": 60, "remediation_present": "Yes"}, # Violator
            {"alert_id": "A-02", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "High", "disposition": "Closed", "escalated": "Yes", "investigation_present": "Yes", "closure_time_minutes": 60, "remediation_present": "Yes"} # Good
        ])
        
        from engine.data_store import DataStore
        store = DataStore()
        store.load_cse_profiles(pd.DataFrame([{"cse_id": "CSE-A"}]))
        store.load_assets(self.assets_df)
        store.load_alerts(alerts_df)
        
        findings = check_eg2_missing_investigation(store)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].evidence_ids[0], "A-01")

    def test_eg3_fast_closure(self):
        alerts_df = pd.DataFrame([
            {"alert_id": "A-01", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "Medium", "disposition": "Closed", "closure_time_minutes": 4, "escalated": "Yes", "investigation_present": "Yes", "remediation_present": "Yes"}, # Violator (< 10 min)
            {"alert_id": "A-02", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "Medium", "disposition": "Closed", "closure_time_minutes": 45, "escalated": "Yes", "investigation_present": "Yes", "remediation_present": "Yes"} # Good
        ])
        
        from engine.data_store import DataStore
        store = DataStore()
        store.load_cse_profiles(pd.DataFrame([{"cse_id": "CSE-A"}]))
        store.load_assets(self.assets_df)
        store.load_alerts(alerts_df)
        
        findings = check_eg3_fast_closure(store)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].evidence_ids[0], "A-01")

    def test_eg4_repeated_no_remediation(self):
        alerts_df = pd.DataFrame([
            # 3 alerts on AST-01, 2 un-remediated (ratio > 0.5) -> Violator
            {"alert_id": "A-01", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "High", "remediation_present": "No"},
            {"alert_id": "A-02", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "High", "remediation_present": "No"},
            {"alert_id": "A-03", "cse_id": "CSE-A", "asset_id": "AST-01", "severity": "High", "remediation_present": "Yes"},
            # 3 alerts on AST-03, 1 un-remediated (ratio < 0.5) -> Good
            {"alert_id": "B-01", "cse_id": "CSE-B", "asset_id": "AST-03", "severity": "High", "remediation_present": "No"},
            {"alert_id": "B-02", "cse_id": "CSE-B", "asset_id": "AST-03", "severity": "High", "remediation_present": "Yes"},
            {"alert_id": "B-03", "cse_id": "CSE-B", "asset_id": "AST-03", "severity": "High", "remediation_present": "Yes"},
        ])
        
        from engine.data_store import DataStore
        store = DataStore()
        store.load_cse_profiles(pd.DataFrame([{"cse_id": "CSE-A"}, {"cse_id": "CSE-B"}]))
        store.load_assets(self.assets_df)
        store.load_alerts(alerts_df)
        
        findings = check_eg4_repeated_no_remediation(store)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].cse_id, "CSE-A")
        self.assertEqual(findings[0].metric_value, 2/3)

    def test_ns1_blind_spot(self):
        from engine.data_store import DataStore
        store = DataStore()
        store.load_cse_profiles(pd.DataFrame([{"cse_id": "CSE-A"}, {"cse_id": "CSE-B"}]))
        store.load_assets(self.assets_df)
        
        findings = check_ns1_blind_spot(store)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].evidence_ids[0], "AST-02") # The one with 1 event

    def test_peer1_deviation(self):
        alerts_df = pd.DataFrame([
            # CSE-A: 4 critical alerts, 4 escalated (100%)
            {"alert_id": "A-01", "cse_id": "CSE-A", "severity": "Critical", "escalated": "Yes"},
            {"alert_id": "A-02", "cse_id": "CSE-A", "severity": "Critical", "escalated": "Yes"},
            {"alert_id": "A-03", "cse_id": "CSE-A", "severity": "High", "escalated": "Yes"},
            {"alert_id": "A-04", "cse_id": "CSE-A", "severity": "High", "escalated": "Yes"},
            # CSE-B: 4 critical alerts, 0 escalated (0%) -> Violator!
            {"alert_id": "B-01", "cse_id": "CSE-B", "severity": "Critical", "escalated": "No"},
            {"alert_id": "B-02", "cse_id": "CSE-B", "severity": "Critical", "escalated": "No"},
            {"alert_id": "B-03", "cse_id": "CSE-B", "severity": "High", "escalated": "No"},
            {"alert_id": "B-04", "cse_id": "CSE-B", "severity": "High", "escalated": "No"},
            # CSE-C: 4 critical alerts, 4 escalated (100%)
            {"alert_id": "C-01", "cse_id": "CSE-C", "severity": "Critical", "escalated": "Yes"},
            {"alert_id": "C-02", "cse_id": "CSE-C", "severity": "Critical", "escalated": "Yes"},
            {"alert_id": "C-03", "cse_id": "CSE-C", "severity": "High", "escalated": "Yes"},
            {"alert_id": "C-04", "cse_id": "CSE-C", "severity": "High", "escalated": "Yes"},
        ])
        
        from engine.data_store import DataStore
        store = DataStore()
        store.load_cse_profiles(pd.DataFrame([{"cse_id": "CSE-A"}, {"cse_id": "CSE-B"}, {"cse_id": "CSE-C"}]))
        store.load_alerts(alerts_df)
        
        findings = check_peer1_deviation(store)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].cse_id, "CSE-B")

from engine.ingestion import ingest_data, get_source_profiles, normalize_dataset, CANONICAL_ALERTS
from engine.evidence_coverage import compute_evidence_coverage
from engine.bootstrap import load_and_run_pipeline

class TestIngestionAndNormalization(unittest.TestCase):
    def setUp(self):
        self.raw_alerts = pd.DataFrame([
            {"event_id": "EV-1", "org_id": "ORG-1", "hostname": "HOST-1", "priority": "High"}
        ])
        self.raw_assets = pd.DataFrame([
            {"hostname": "HOST-1", "org_id": "ORG-1", "importance": "Critical", "device_class": "Server", "log_count": 50}
        ])
        
    def test_missing_fields_become_not_available(self):
        profile = get_source_profiles()["PUBLIC_SOC"]
        norm, status = normalize_dataset(self.raw_alerts, profile["alerts_map"], CANONICAL_ALERTS)
        self.assertEqual(norm["investigation_present"].iloc[0], "NOT_AVAILABLE")
        self.assertEqual(norm["escalated"].iloc[0], "NOT_AVAILABLE")
        
    def test_valid_invalid_field_mapping(self):
        profile = get_source_profiles()["PUBLIC_SOC"]
        norm, status = normalize_dataset(self.raw_alerts, profile["alerts_map"], CANONICAL_ALERTS)
        mapped = [s for s in status if "Mapped" in s["status"]]
        self.assertTrue(len(mapped) > 0)
        
        bad_map = {"fake_field": "alert_id"}
        _, bad_status = normalize_dataset(self.raw_alerts, bad_map, CANONICAL_ALERTS)
        self.assertTrue(any("Missing" in s["status"] for s in bad_status))

    def test_incomplete_evidence_coverage(self):
        payload = ingest_data(self.raw_alerts, self.raw_assets, pd.DataFrame(), "PUBLIC_SOC")
        cov, avail = compute_evidence_coverage(payload["alerts_df"], payload["assets_df"], payload["cases_df"])
        
        self.assertEqual(cov["Investigation"], 0)
        self.assertEqual(avail["EG-1"], "INSUFFICIENT EVIDENCE")
        self.assertEqual(avail["EG-2"], "INSUFFICIENT EVIDENCE")
        self.assertEqual(avail["NS-1"], "READY") 
        
    def test_provenance_metadata(self):
        payload = ingest_data(self.raw_alerts, self.raw_assets, pd.DataFrame(), "PUBLIC_SOC")
        prov = payload["provenance"]
        self.assertEqual(prov["source_type"], "PUBLIC_SOC")
        self.assertEqual(prov["type"], "Public Cybersecurity Dataset")
        self.assertTrue(prov["records"] > 0)
        
    def test_scenario_replay(self):
        data = load_and_run_pipeline("CONTROLLED_DEMO")
        self.assertTrue(len(data["alerts_df"]) > 0)
        self.assertIn("ingestion_meta", data)

if __name__ == '__main__':
    unittest.main()

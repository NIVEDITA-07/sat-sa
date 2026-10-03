import unittest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.pipeline import run_analytical_engine
from engine.data_store import DataStore
from engine.ingestion import ingest_data

class TestSATSAProvenance(unittest.TestCase):

    def setUp(self):
        self.raw_alerts = pd.DataFrame([
            {"alert_id": "ALT-1", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": "Critical", "created_at": "2026-09-01T10:00:00Z", "closed_at": "2026-09-01T11:00:00Z", "status": "Closed", "escalated": "No", "investigation_present": "No", "remediation_status": "Closed"},
            {"alert_id": "ALT-2", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": "Critical", "created_at": "2026-09-01T10:00:00Z", "closed_at": "2026-09-01T11:00:00Z", "status": "Closed", "escalated": pd.NA, "investigation_present": pd.NA, "remediation_status": pd.NA}
        ])
        
        self.raw_assets = pd.DataFrame([
            {"asset_id": "AST-1", "cse_id": "CSE-1", "criticality": "Critical", "asset_type": "Server", "expected_monitoring": "Yes", "observed_monitoring_events": 1000},
        ])
        
        self.raw_cases = pd.DataFrame([
            {"case_id": "CAS-1", "cse_id": "CSE-1", "primary_alert_id": "ALT-1", "investigation_started_at": "2026-09-01T10:05:00Z", "investigation_note": "Normal alert handled.", "investigator_id": "INV-1"},
        ])
        
        self.raw_profiles = pd.DataFrame([
            {"cse_id": "CSE-1", "sector": "Finance", "assessment_period": "Q1 2026", "reported_escalation_rate": "100%", "reported_investigation_rate": "100%"},
        ])
        
        payload = ingest_data(self.raw_alerts, self.raw_assets, self.raw_cases, "CONTROLLED_DEMO", self.raw_profiles)
        
        self.store = DataStore()
        self.store.load_cse_profiles(payload["cse_profiles_df"])
        self.store.load_assets(payload["assets_df"])
        self.store.load_alerts(payload["alerts_df"])
        self.store.load_cases(payload["cases_df"])
        
        self.results = run_analytical_engine(self.store, ingestion_meta=payload)
        self.att = self.results["cse_attentions"]["CSE-1"]

    def test_provenance_exists_and_resolves(self):
        # Find EG-1
        finding = next((f for f in self.att.findings if f.rule_id == "EG-1"), None)
        self.assertIsNotNone(finding)
        self.assertIsNotNone(finding.provenance)
        
        # Test 1, 5, 6, 7
        self.assertTrue(finding.provenance.rule_version.startswith("EG-1:"))
        self.assertTrue(finding.provenance.assessment_id.startswith("run-"))
        self.assertTrue(finding.provenance.configuration_version.startswith("cfg-"))
        
        # Test 2, 3: Evidence ID resolves
        self.assertTrue(len(finding.provenance.evidence_lineage) > 0)
        lineage = finding.provenance.evidence_lineage[0]
        self.assertEqual(lineage.source_record_id, "ALT-1")
        
        alert_record = self.store.get_alert_evidence("ALT-1")
        self.assertIsNotNone(alert_record)
        
        # Test 4: Raw record remains unchanged
        self.assertEqual(alert_record["escalated"], "No") # Normalized state is unchanged in store
        
    def test_aggregate_provenance(self):
        finding = next((f for f in self.att.findings if f.rule_id == "K-1"), None)
        if finding:
            self.assertIsNotNone(finding.provenance.aggregate_context)
            self.assertEqual(finding.provenance.aggregate_context.get("metric_type"), "kpi_contradiction")
            
    def test_not_available_behavior(self):
        # ALT-2 should NOT trigger EG-1 because escalated is NOT_AVAILABLE
        finding = next((f for f in self.att.findings if f.rule_id == "EG-1"), None)
        self.assertNotIn("ALT-2", finding.evidence_ids)
        self.assertNotIn("ALT-2", [l.source_record_id for l in finding.provenance.evidence_lineage])
        
    def test_attention_lineage(self):
        self.assertTrue(len(self.att.contributions) > 0)
        for contrib in self.att.contributions:
            self.assertTrue(contrib.finding_id)
            self.assertTrue(contrib.rule_id)
            self.assertTrue(contrib.contribution_weight > 0)

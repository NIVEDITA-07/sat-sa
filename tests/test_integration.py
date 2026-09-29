import unittest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.pipeline import run_analytical_engine
from engine.data_store import DataStore
from engine.ingestion import ingest_data

class TestSATSAInvariants(unittest.TestCase):

    def setUp(self):
        # Build synthetic raw data to test all 10 invariants
        
        self.raw_alerts = pd.DataFrame([
            # 1. Duplicated Alert (DQ-1)
            {"alert_id": "ALT-1", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": "Critical", "created_at": "2026-09-01T10:00:00Z", "closed_at": "2026-09-01T11:00:00Z", "status": "Closed", "escalated": "Yes", "investigation_present": "Yes", "remediation_status": "Closed"},
            {"alert_id": "ALT-1", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": "Critical", "created_at": "2026-09-01T10:00:00Z", "closed_at": "2026-09-01T11:00:00Z", "status": "Closed", "escalated": "Yes", "investigation_present": "Yes", "remediation_status": "Closed"},
            
            # 2. Missing Severity (DQ-2) & Fast Closure (EG-3)
            {"alert_id": "ALT-2", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": pd.NA, "created_at": "2026-09-01T10:00:00Z", "closed_at": "2026-09-01T10:05:00Z", "status": "Closed", "escalated": "Yes", "investigation_present": "Yes", "remediation_status": "Closed"},
            
            # 3. Impossible Lifecycle (DQ-3)
            {"alert_id": "ALT-3", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": "High", "created_at": "2026-09-01T12:00:00Z", "closed_at": "2026-09-01T11:00:00Z", "status": "Closed", "escalated": "Yes", "investigation_present": "Yes", "remediation_status": "Closed"},
            
            # 4. EG-1 Violator (No Escalation)
            {"alert_id": "ALT-4", "cse_id": "CSE-1", "asset_id": "AST-1", "severity": "Critical", "created_at": "2026-09-01T10:00:00Z", "closed_at": "2026-09-01T11:00:00Z", "status": "Closed", "escalated": "No", "investigation_present": "Yes", "remediation_status": "Closed"},
            
            # 5. Missing Data / INSUFFICIENT EVIDENCE (EG-1 should NOT fire)
            {"alert_id": "ALT-5", "cse_id": "CSE-2", "asset_id": "AST-2", "severity": "Critical", "created_at": "2026-09-01T10:00:00Z", "closed_at": "2026-09-01T11:00:00Z", "status": "Closed", "escalated": pd.NA, "investigation_present": pd.NA, "remediation_status": pd.NA}
        ])
        
        self.raw_assets = pd.DataFrame([
            {"asset_id": "AST-1", "cse_id": "CSE-1", "criticality": "Critical", "asset_type": "Server", "expected_monitoring": "Yes", "observed_monitoring_events": 1000},
            {"asset_id": "AST-2", "cse_id": "CSE-2", "criticality": "Critical", "asset_type": "Server", "expected_monitoring": "Yes", "observed_monitoring_events": 0} # NS-1 Violator
        ])
        
        self.raw_cases = pd.DataFrame([
            {"case_id": "CAS-1", "cse_id": "CSE-1", "primary_alert_id": "ALT-1", "investigation_started_at": "2026-09-01T10:05:00Z", "investigation_note": "Normal alert handled.", "investigator_id": "INV-1"},
            {"case_id": "CAS-2", "cse_id": "CSE-1", "primary_alert_id": "ALT-4", "investigation_started_at": "2026-09-01T10:05:00Z", "investigation_note": "Normal alert handled.", "investigator_id": "INV-1"}, # I-1 pattern reuse
            {"case_id": "CAS-3", "cse_id": "CSE-1", "primary_alert_id": "ALT-2", "investigation_started_at": "2026-09-01T10:05:00Z", "investigation_note": "Normal alert handled.", "investigator_id": "INV-1"},
            {"case_id": "CAS-4", "cse_id": "CSE-1", "primary_alert_id": "ALT-3", "investigation_started_at": "2026-09-01T10:05:00Z", "investigation_note": "Normal alert handled.", "investigator_id": "INV-1"}
        ])
        
        self.raw_profiles = pd.DataFrame([
            {"cse_id": "CSE-1", "sector": "Finance", "assessment_period": "Q1 2026", "reported_escalation_rate": "100%", "reported_investigation_rate": "100%"},
            {"cse_id": "CSE-2", "sector": "Finance", "assessment_period": "Q1 2026", "reported_escalation_rate": "100%", "reported_investigation_rate": "100%"}
        ])

    def test_invariants(self):
        # 1. Ingestion handles NOT_AVAILABLE cleanly
        payload = ingest_data(self.raw_alerts, self.raw_assets, self.raw_cases, "CONTROLLED_DEMO", self.raw_profiles)
        
        store = DataStore()
        store.load_cse_profiles(payload["cse_profiles_df"])
        store.load_assets(payload["assets_df"])
        store.load_alerts(payload["alerts_df"])
        store.load_cases(payload["cases_df"])
        
        results = run_analytical_engine(store)
        cse1_att = results["cse_attentions"]["CSE-1"]
        cse2_att = results["cse_attentions"]["CSE-2"]
        
        # Grab finding rules triggered for CSE-1
        cse1_rules = [f.rule_id for f in cse1_att.findings]
        cse2_rules = [f.rule_id for f in cse2_att.findings]
        
        # Assert INVARIANT: Data Quality isolated (DQ-1, DQ-2, DQ-3 triggered for CSE-1)
        self.assertIn("DQ-1", cse1_rules, "Duplicate alert should trigger DQ-1")
        self.assertIn("DQ-2", cse1_rules, "Missing severity should trigger DQ-2")
        self.assertIn("DQ-3", cse1_rules, "Negative closure time should trigger DQ-3")
        
        # Assert INVARIANT: Tri-state Semantics (EG-1 triggers for CSE-1 due to explicit 'No', but NOT for CSE-2 due to 'NOT_AVAILABLE')
        self.assertIn("EG-1", cse1_rules, "EG-1 should trigger when explicit NO is observed")
        self.assertNotIn("EG-1", cse2_rules, "EG-1 must NOT trigger for missing data")
        
        # Assert INVARIANT: Investigation reuse (I-1 triggers for INV-1)
        self.assertIn("I-1", cse1_rules, "I-1 should detect reused investigation notes")
        
        # Assert INVARIANT: Monitoring blind spot (NS-1 triggers for CSE-2)
        self.assertIn("NS-1", cse2_rules, "NS-1 should trigger for 0 telemetry")
        
        # Assert INVARIANT: Missing data leads to INSUFFICIENT EVIDENCE rather than findings
        self.assertEqual(results["coverage"]["CSE-2"]["rule_availability"]["EG-1"], "INSUFFICIENT EVIDENCE")
        
        # Assert INVARIANT: KPI Contradiction works correctly (Reported 100%, observed < 100%)
        self.assertIn("K-1", cse1_rules, "K-1 should trigger when operational rate contradicts reported 100%")

if __name__ == '__main__':
    unittest.main()

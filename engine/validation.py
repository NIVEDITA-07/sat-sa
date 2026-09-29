import pandas as pd
import os

SCENARIO_TO_RULE = {
    'CRITICAL_NO_ESCALATION': 'EG-1',
    'MISSING_INVESTIGATION': 'EG-2',
    'FAST_CLOSURE': 'EG-3',
    'REPEATED_NO_REMEDIATION': 'EG-4',
    'NEGATIVE_SPACE': 'NS-1',
    'PEER_DEVIATION': 'PEER-1',
    'TEMPORAL_DRIFT': 'T-1',
    'KPI_CONTRADICTION': 'K-1',
    'INVESTIGATION_REUSE': 'I-1'
}

def load_ground_truth(file_path: str = None) -> pd.DataFrame:
    if not file_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "validation_ground_truth.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

def validate_findings(cse_attentions: dict, ground_truth_df: pd.DataFrame) -> dict:
    if ground_truth_df.empty:
        return {"status": "No Ground Truth Found"}
        
    all_findings = []
    for att in cse_attentions.values():
        all_findings.extend(att.findings)
        
    generated_map = {}
    for f in all_findings:
        if (f.cse_id, f.rule_id) not in generated_map:
            generated_map[(f.cse_id, f.rule_id)] = []
        generated_map[(f.cse_id, f.rule_id)].append(f)

    results = []
    detected_count = 0
    not_detected_count = 0
    
    # We will track which findings matched expected scenarios.
    matched_findings = set()
    
    for _, row in ground_truth_df.iterrows():
        scenario = row.get("scenario_type")
            
        cse = row.get("cse_id")
        rule_ids = []
        if scenario == 'DATA_QUALITY':
            rule_ids = ['DQ-1', 'DQ-2', 'DQ-3']
        else:
            r = SCENARIO_TO_RULE.get(scenario)
            if r:
                rule_ids = [r]
                
        if not rule_ids:
            continue
            
        entity_id = row.get("entity_id")
        entity_type = row.get("entity_type")
        
        matches = []
        for r_id in rule_ids:
            matches.extend(generated_map.get((cse, r_id), []))
        
        detected = False
        for m in matches:
            if entity_type == "Asset" and pd.notna(entity_id):
                if entity_id in m.evidence_ids or entity_id in m.title:
                    detected = True
                    matched_findings.add(m.finding_id)
            elif entity_type == "Alert" and pd.notna(entity_id):
                if entity_id in m.evidence_ids:
                    detected = True
                    matched_findings.add(m.finding_id)
            elif entity_type == "Investigator" and pd.notna(entity_id):
                if entity_id in m.title or entity_id in m.explanation:
                    detected = True
                    matched_findings.add(m.finding_id)
            elif pd.notna(entity_id):
                if entity_id in m.evidence_ids or entity_id in m.title or entity_id in m.explanation:
                    detected = True
                    matched_findings.add(m.finding_id)
            else:
                detected = True
                matched_findings.add(m.finding_id)
                
        if detected:
            detected_count += 1
            status = "PASS"
        else:
            not_detected_count += 1
            status = "FAIL"
            
        results.append({
            "Scenario": scenario,
            "CSE": cse,
            "Entity": entity_id if pd.notna(entity_id) else "N/A",
            "Expected": "Yes",
            "Detected": "Yes" if detected else "No",
            "Status": status
        })
        
    unexpected = len([f for f in all_findings if f.finding_id not in matched_findings])
        
    return {
        "results": results,
        "summary": {
            "expected_total": detected_count + not_detected_count,
            "detected": detected_count,
            "not_detected": not_detected_count,
            "unexpected_detections": unexpected
        }
    }

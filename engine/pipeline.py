import pandas as pd
from engine.schema import validate_schema
from engine.execution_gaps import (
    check_eg1_critical_no_escalation,
    check_eg2_missing_investigation,
    check_eg3_fast_closure,
    check_eg4_repeated_no_remediation
)
from engine.negative_space import check_ns1_blind_spot
from engine.peer_comparison import check_peer1_deviation
from engine.attention_score import compute_attention
from engine.sector_wide import compute_sector_wide_signals

from engine.temporal_drift import check_temporal_drift
from engine.kpi_contradiction import check_kpi_contradiction
from engine.investigation_reuse import check_investigation_reuse
from engine.data_store import DataStore

def run_analytical_engine(store: DataStore, ingestion_meta: dict = None) -> dict:
    """
    Core pipeline that executes all rules and generates canonical findings.
    """
    alerts_df = store.alerts_df
    assets_df = store.assets_df
    cases_df = store.cases_df
    cse_profiles_df = store.cse_profiles_df
    
    # 1. Validate Schema
    validate_schema(alerts_df, assets_df, cases_df)
    
    # 2. Evidence Coverage
    from engine.evidence_coverage import check_evidence_coverage
    coverage_info = check_evidence_coverage(store)
    
    # 3. Execute Rules (Generates Flat List of Findings, observing availability)
    all_findings = []
    
    from engine.data_quality import check_data_quality
    all_findings.extend(check_data_quality(store))
    all_findings.extend(check_eg1_critical_no_escalation(store))
    all_findings.extend(check_eg2_missing_investigation(store))
    all_findings.extend(check_eg3_fast_closure(store))
    all_findings.extend(check_eg4_repeated_no_remediation(store))
    all_findings.extend(check_ns1_blind_spot(store))
    all_findings.extend(check_peer1_deviation(store))
    all_findings.extend(check_temporal_drift(store))
    all_findings.extend(check_kpi_contradiction(store))
    all_findings.extend(check_investigation_reuse(store))
    
    # Filter out findings for CSEs that didn't have evidence for that rule.
    # Phase 1: use EvaluabilityResult.evaluable when available; fall back to
    # the string vocabulary for backward compatibility.
    filtered_findings = []
    for f in all_findings:
        cse  = f.cse_id
        rule = f.rule_id
        cse_cov = coverage_info.get(cse, {})

        # Prefer the typed EvaluabilityResult (Phase 1 gate)
        gate = cse_cov.get("evaluability", {}).get(rule)
        if gate is not None:
            if gate.evaluable:
                filtered_findings.append(f)
        else:
            # Legacy fallback: string check
            status = cse_cov.get("rule_availability", {}).get(rule, "READY")
            if status in ("READY", "PARTIALLY EVALUABLE"):
                filtered_findings.append(f)

    all_findings = filtered_findings

    # Phase 2: Attach Provenance Lineage
    from engine.provenance import attach_provenance
    all_findings = attach_provenance(all_findings, store, ingestion_meta or {})
    
    # 4. Group Findings by CSE
    cse_ids = sorted(list(store._profiles_idx.keys()))
    
    cse_findings_map = {cse_id: [] for cse_id in cse_ids}
    for f in all_findings:
        if f.cse_id in cse_findings_map:
            cse_findings_map[f.cse_id].append(f)
            
    # 5. Compute Attention Scores & KPIs
    cse_attentions = {}
    for cse_id, findings in cse_findings_map.items():
        att = compute_attention(cse_id, findings, store)
        att.evidence_coverage = coverage_info.get(cse_id, {}).get("coverage_summary", {})
        att.evidence_warnings = coverage_info.get(cse_id, {}).get("warnings", [])
        cse_attentions[cse_id] = att
        
    # 6. Compute Sector-Wide Signals
    sector_signals = compute_sector_wide_signals(all_findings, coverage_info)
        
    # 7. Ground Truth Validation
    # validation is now disabled from inside the pipeline to strictly keep ground truth separate.
    # It will run in bootstrap.py after the engine returns.
    validation_metrics = {}
        
    return {
        "cse_attentions": cse_attentions,
        "alerts_df": alerts_df,
        "assets_df": assets_df,
        "cases_df": cases_df,
        "sector_signals": sector_signals,
        "coverage": coverage_info,
        "validation_metrics": validation_metrics,
        "ingestion_meta": ingestion_meta or {}
    }

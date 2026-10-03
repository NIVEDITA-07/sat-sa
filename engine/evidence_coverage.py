"""
engine/evidence_coverage.py

Calculates the coverage of supervisory evidence per CSE and determines
which analytical rules have sufficient evidence to run.

Phase 1 changes:
  - Uses the formal evaluability_gate() from semantics.py.
  - eval_col now correctly returns "NOT_AVAILABLE" when column is absent OR
    when ALL values in the column are "NOT_AVAILABLE" (not just when the
    column is missing from the DataFrame).
  - rule_availability now stores EvaluabilityResult objects, serialised to
    the existing string vocabulary for backward-compatibility with pipeline.py.
"""

import pandas as pd
from engine.data_store import DataStore
from engine.semantics import evaluability_gate, EVIDENCE_NOT_AVAILABLE


# Map each rule → the coverage dimensions it requires
RULE_REQUIRED_DIMENSIONS: dict[str, list[str]] = {
    "EG-1":   ["Escalation", "Alerts"],
    "EG-2":   ["Investigation", "Alerts"],
    "EG-3":   ["Closure Time", "Alerts"],
    "EG-4":   ["Remediation", "Alerts"],
    "NS-1":   ["Monitoring", "Assets"],
    "PEER-1": ["Escalation", "Alerts"],
    "T-1":    ["Investigation", "Alerts"],
    "K-1":    ["Escalation", "Investigation", "Alerts"],
    "I-1":    ["Investigation Notes", "Cases"],
}


def _eval_col(df: pd.DataFrame, col: str) -> str:
    """
    Determine the coverage state for a single column.

    Returns
    -------
    "Available"      – column exists and every row has a non-NOT_AVAILABLE value.
    "Partial"        – column exists and at least one row is populated, but not all.
    "NOT_AVAILABLE"  – column is absent OR every single value is NOT_AVAILABLE.

    PHASE 1 GUARANTEE
    ─────────────────
    A column full of "NOT_AVAILABLE" strings is indistinguishable from a missing
    column from the engine's perspective — both yield "NOT_AVAILABLE".
    """
    if df.empty or col not in df.columns:
        return "NOT_AVAILABLE"

    total = len(df)
    if total == 0:
        return "NOT_AVAILABLE"

    populated = df[
        (df[col] != EVIDENCE_NOT_AVAILABLE) & df[col].notna()
    ]
    filled = len(populated)

    if filled == 0:
        return "NOT_AVAILABLE"
    if filled == total:
        return "Available"
    return "Partial"


def check_evidence_coverage(store: DataStore) -> dict:
    """
    Calculates per-CSE evidence coverage and rule evaluability.

    Returns
    -------
    dict  keyed by cse_id, each value being:
    {
        "coverage_summary":  dict[str, str],        # dimension → coverage state
        "rule_availability": dict[str, str],         # rule_id  → "READY" | "INSUFFICIENT EVIDENCE" | "PARTIALLY EVALUABLE"
        "evaluability":      dict[str, EvaluabilityResult],  # rule_id → EvaluabilityResult
        "warnings":          list[str],
    }

    Backward compatibility
    ───────────────────────
    rule_availability still stores the plain string vocabulary that pipeline.py
    expects.  The new "evaluability" sub-dict provides the typed EvaluabilityResult
    for any caller that wants richer information.
    """
    cse_coverage_info = {}

    for cse_id in store._profiles_idx.keys():
        data   = store.get_cse_data(cse_id)
        alerts_df = pd.DataFrame(data.get("alerts", []))
        assets_df = pd.DataFrame(data.get("assets", []))
        cases_df  = pd.DataFrame(data.get("cases", []))

        # ── Coverage dimensions ─────────────────────────────────────────
        coverage: dict[str, str] = {
            "Alerts":               "Available" if not alerts_df.empty else "NOT_AVAILABLE",
            "Assets":               "Available" if not assets_df.empty else "NOT_AVAILABLE",
            "Cases":                "Available" if not cases_df.empty  else "NOT_AVAILABLE",
            "Investigation":        _eval_col(alerts_df, "investigation_present"),
            "Escalation":           _eval_col(alerts_df, "escalated"),
            "Remediation":          _eval_col(alerts_df, "remediation_present"),
            "Monitoring":           _eval_col(assets_df, "observed_monitoring_events"),
            "Investigation Notes":  _eval_col(cases_df,  "investigation_note"),
            "Closure Time":         _eval_col(alerts_df, "closure_time_minutes"),
        }

        # ── Rule evaluability via formal gate ───────────────────────────
        warnings:       list[str]  = []
        rule_avail:     dict[str, str]               = {}
        evaluability:   dict[str, object]            = {}  # EvaluabilityResult

        for rule_id, dims in RULE_REQUIRED_DIMENSIONS.items():
            required = {d: coverage.get(d, "NOT_AVAILABLE") for d in dims}
            gate     = evaluability_gate(required)
            evaluability[rule_id] = gate

            # Serialise to the string vocabulary pipeline.py already uses
            rule_avail[rule_id] = gate.state.replace("_", " ")  # maps to the existing keys

            if gate.state == "INSUFFICIENT_EVIDENCE":
                missing_str = ", ".join(gate.missing_fields)
                warnings.append(
                    f"{rule_id} cannot be evaluated — required evidence is absent: {missing_str}."
                )
            elif gate.state == "PARTIALLY_EVALUABLE":
                partial_str = ", ".join(gate.partial_fields)
                warnings.append(
                    f"{rule_id} is evaluated on partial evidence ({partial_str}); "
                    f"findings may be incomplete."
                )

        cse_coverage_info[cse_id] = {
            "coverage_summary":  coverage,
            "rule_availability": rule_avail,
            "evaluability":      evaluability,
            "warnings":          warnings,
        }

    return cse_coverage_info

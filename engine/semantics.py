"""
engine/semantics.py

Centralized evidence state interpretation and expectation resolution layer.
Implements explicit tri-state semantics (YES, NO, NOT_AVAILABLE).

Phase 1 additions:
  - EvaluabilityResult dataclass: formal typed result of a gate check
  - evaluability_gate(): central gate function called by any rule before evaluating
  - All constants kept backward-compatible
"""

import pandas as pd
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Evidence Tri-States (string representation for JSON serialisability)
# ---------------------------------------------------------------------------
EVIDENCE_YES           = "YES"
EVIDENCE_NO            = "NO"
EVIDENCE_NOT_AVAILABLE = "NOT_AVAILABLE"

# Expectation States (same vocabulary, kept separate for conceptual clarity)
EXPECTATION_YES           = "YES"
EXPECTATION_NO            = "NO"
EXPECTATION_NOT_AVAILABLE = "NOT_AVAILABLE"

# ---------------------------------------------------------------------------
# Evaluability Gate result  (Phase 1 addition)
# ---------------------------------------------------------------------------

@dataclass
class EvaluabilityResult:
    """
    Formal result returned by evaluability_gate().

    Attributes
    ----------
    evaluable : bool
        True → the rule has sufficient evidence to produce a finding or
                a confident non-finding.
        False → the rule MUST NOT fire; evidence is absent or ambiguous.
    state : str
        One of: "READY" | "INSUFFICIENT_EVIDENCE" | "PARTIALLY_EVALUABLE"
    missing_fields : list[str]
        Which required field names were NOT_AVAILABLE.  Empty when evaluable=True
        and state="READY".
    partial_fields : list[str]
        Which required field names were only partially populated.
    """
    evaluable:      bool
    state:          str
    missing_fields: list = field(default_factory=list)
    partial_fields: list = field(default_factory=list)

    def __bool__(self):
        return self.evaluable


def evaluability_gate(required_fields: dict[str, str]) -> EvaluabilityResult:
    """
    Central evaluability gate.  Call this at the top of every rule before
    evaluating any condition.

    Parameters
    ----------
    required_fields : dict[str, str]
        Mapping of  {field_label: coverage_status}  where coverage_status is
        one of "Available" | "Partial" | "NOT_AVAILABLE".
        The caller obtains coverage_status values from check_evidence_coverage().

    Returns
    -------
    EvaluabilityResult
        If evaluable=False the calling rule MUST skip and produce no finding.

    Examples
    --------
    >>> gate = evaluability_gate({"Escalation": "NOT_AVAILABLE", "Alerts": "Available"})
    >>> if not gate:
    ...     return []   # rule cannot run; log gate.state and gate.missing_fields
    """
    missing  = [f for f, s in required_fields.items() if s == "NOT_AVAILABLE"]
    partial  = [f for f, s in required_fields.items() if s == "Partial"]

    if missing:
        return EvaluabilityResult(
            evaluable=False,
            state="INSUFFICIENT_EVIDENCE",
            missing_fields=missing,
            partial_fields=partial,
        )
    if partial:
        return EvaluabilityResult(
            evaluable=True,
            state="PARTIALLY_EVALUABLE",
            missing_fields=[],
            partial_fields=partial,
        )
    return EvaluabilityResult(evaluable=True, state="READY")


# ---------------------------------------------------------------------------
# Core tri-state normalisation
# ---------------------------------------------------------------------------

def normalize_boolean(value) -> str:
    """
    Normalises various boolean-like strings into the canonical tri-state.

    CRITICAL CONTRACT
    ─────────────────
    Any value that cannot be conclusively mapped to YES or NO MUST return
    EVIDENCE_NOT_AVAILABLE.  It must NEVER silently become EVIDENCE_NO.
    """
    if pd.isna(value) or value is None:
        return EVIDENCE_NOT_AVAILABLE

    val_str = str(value).strip().upper()

    if val_str in ("YES", "Y", "TRUE", "T", "1", "CLOSED", "COMPLETED"):
        return EVIDENCE_YES
    if val_str in ("NO", "N", "FALSE", "F", "0", "OPEN", "NOT_COMPLETED"):
        return EVIDENCE_NO
    if val_str in ("NOT_AVAILABLE", "NA", "N/A", "NONE", "NULL", "MISSING", ""):
        return EVIDENCE_NOT_AVAILABLE

    # Anything else is genuinely ambiguous → NOT_AVAILABLE, never NO.
    return EVIDENCE_NOT_AVAILABLE


def is_known_yes(value) -> bool:
    return normalize_boolean(value) == EVIDENCE_YES


def is_known_no(value) -> bool:
    return normalize_boolean(value) == EVIDENCE_NO


def is_available(value) -> bool:
    """True when the value is definitively YES or NO (not missing)."""
    return normalize_boolean(value) != EVIDENCE_NOT_AVAILABLE


# ---------------------------------------------------------------------------
# Expectation resolvers
# ---------------------------------------------------------------------------

def resolve_escalation_expectation(alert_row, profile_row=None, case_row=None) -> str:
    """
    Determine whether escalation is *expected* for this alert.

    Priority
    1. Explicit case-record field (escalation_required) — highest authority.
    2. Severity-based policy fallback.
    """
    if case_row is not None and "escalation_required" in case_row:
        exp = normalize_boolean(case_row["escalation_required"])
        if exp != EXPECTATION_NOT_AVAILABLE:
            return exp

    severity = str(alert_row.get("severity", "")).upper()
    if severity in ("CRITICAL", "HIGH"):
        return EXPECTATION_YES
    if severity in ("MEDIUM", "LOW"):
        return EXPECTATION_NO
    return EXPECTATION_NOT_AVAILABLE


def resolve_investigation_expectation(alert_row, profile_row=None) -> str:
    """Determine whether investigation is expected for this alert."""
    severity = str(alert_row.get("severity", "")).upper()
    if severity in ("CRITICAL", "HIGH"):
        return EXPECTATION_YES
    if severity in ("MEDIUM", "LOW"):
        return EXPECTATION_NO
    return EXPECTATION_NOT_AVAILABLE


def resolve_remediation_expectation(alert_row) -> str:
    """Any valid alert implies remediation is expected."""
    return EXPECTATION_YES


# ---------------------------------------------------------------------------
# Gap determination
# ---------------------------------------------------------------------------

def determine_execution_gap(expected: str, observed: str) -> bool:
    """
    Returns True *only* when expected=YES AND observed=NO.

    CRITICAL: If either side is NOT_AVAILABLE → returns False.
    NOT_AVAILABLE must NEVER silently become a gap.
    """
    return expected == EXPECTATION_YES and observed == EVIDENCE_NO

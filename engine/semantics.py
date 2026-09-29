"""
engine/semantics.py

Centralized evidence state interpretation and expectation resolution layer.
Implements explicit tri-state semantics (YES, NO, NOT_AVAILABLE).
"""

import pandas as pd

# Evidence Tri-States
EVIDENCE_YES = "YES"
EVIDENCE_NO = "NO"
EVIDENCE_NOT_AVAILABLE = "NOT_AVAILABLE"

# Expectation States
EXPECTATION_YES = "YES"
EXPECTATION_NO = "NO"
EXPECTATION_NOT_AVAILABLE = "NOT_AVAILABLE"

def normalize_boolean(value) -> str:
    """Normalizes various boolean-like strings into tri-state strings."""
    if pd.isna(value) or value is None:
        return EVIDENCE_NOT_AVAILABLE
    
    val_str = str(value).strip().upper()
    if val_str in ("YES", "Y", "TRUE", "T", "1", "CLOSED", "COMPLETED"):
        return EVIDENCE_YES
    elif val_str in ("NO", "N", "FALSE", "F", "0", "OPEN", "NOT_COMPLETED"):
        return EVIDENCE_NO
    elif val_str == "NOT_AVAILABLE":
        return EVIDENCE_NOT_AVAILABLE
    
    return EVIDENCE_NOT_AVAILABLE

def is_known_yes(value) -> bool:
    return normalize_boolean(value) == EVIDENCE_YES

def is_known_no(value) -> bool:
    return normalize_boolean(value) == EVIDENCE_NO

def is_available(value) -> bool:
    return normalize_boolean(value) != EVIDENCE_NOT_AVAILABLE

def resolve_escalation_expectation(alert_row, profile_row=None, case_row=None) -> str:
    """
    Priority:
    1. Explicit source evidence (e.g., case_row.escalation_required)
    2. Fallback policy rule (Critical/High)
    """
    # If the case record explicitly states escalation expectation
    if case_row is not None and "escalation_required" in case_row:
        exp = normalize_boolean(case_row["escalation_required"])
        if exp != EXPECTATION_NOT_AVAILABLE:
            return exp
            
    # Fallback policy rule
    severity = str(alert_row.get("severity", "")).upper()
    if severity in ("CRITICAL", "HIGH"):
        return EXPECTATION_YES
    elif severity in ("MEDIUM", "LOW"):
        return EXPECTATION_NO
        
    return EXPECTATION_NOT_AVAILABLE

def resolve_investigation_expectation(alert_row, profile_row=None) -> str:
    """
    Resolve if investigation is expected.
    """
    severity = str(alert_row.get("severity", "")).upper()
    if severity in ("CRITICAL", "HIGH"):
        return EXPECTATION_YES
    elif severity in ("MEDIUM", "LOW"):
        return EXPECTATION_NO
        
    return EXPECTATION_NOT_AVAILABLE

def resolve_remediation_expectation(alert_row) -> str:
    # Any valid alert implies remediation is expected.
    return EXPECTATION_YES

def determine_execution_gap(expected: str, observed: str) -> bool:
    """
    Returns True if an execution gap exists.
    Expected = YES, Observed = NO -> True
    If either is NOT_AVAILABLE, returns False (insufficient evidence, not a gap).
    """
    if expected == EXPECTATION_YES and observed == EVIDENCE_NO:
        return True
    return False

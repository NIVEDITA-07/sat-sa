# config.py
# SAT-SA Configuration and Thresholds

# EG-3: Suspiciously fast closure
FAST_CLOSURE_MINUTES = 10 # Alerts closed under this threshold are flagged

# EG-4: Repeated alerts, no remediation
REPEAT_ALERT_MIN_COUNT = 3 # Minimum alerts on same asset to consider repeated
REPEAT_UNREMEDIATED_RATIO = 0.5 # Minimum ratio of unresolved alerts

# NS-1: Monitoring blind spot
NEGATIVE_SPACE_MAX_COVERAGE_RATIO = 0.01 # 1% of expected events or lower is a blind spot

# PEER-1: Peer deviation (Leave-One-Out)
PEER_MIN_CSE_COUNT = 3 # Minimum total CSEs in peer group to compare (meaning at least 2 peers for target)
PEER_MIN_ELIGIBLE_ALERTS = 10 # Target and peers must have at least this many eligible alerts
PEER_STD_MULTIPLIER = 1.0 # Standard deviations below mean
PEER_MIN_RELATIVE_RATE = 0.5 # Must also be less than 50% of the mean

# T-1: Temporal drift
TEMPORAL_DRIFT_THRESHOLD = 0.20 # 20 percentage points drop
TEMPORAL_MIN_DAYS = 30 # Minimum span to calculate drift
TEMPORAL_MIN_OBSERVATIONS = 10 # Minimum alerts in baseline and recent

# K-1: KPI Contradiction
KPI_CONTRADICTION_THRESHOLD = 0.15 # 15 percentage points absolute difference

# I-1: Investigation Reuse
REPEATED_NOTE_THRESHOLD = 3 # Number of identical notes to trigger finding
REPEATED_NOTE_MIN_LENGTH = 10 # Minimum chars to be considered a real note
REPEATED_NOTE_MIN_SHARE = 0.10 # Reused note must be at least 10% of analyst's notes

# Sector-Wide Aggregation
CROSS_CSE_PROPORTION_THRESHOLD = 0.30 # 30% of eligible CSEs
CROSS_CSE_MIN_AFFECTED_CSES = 3 # At least 3 CSEs must be affected

# Attention Scoring
ATTENTION_WEIGHTS = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

ATTENTION_LEVEL_THRESHOLDS = {
    "HIGH": 10,
    "MEDIUM": 5
}


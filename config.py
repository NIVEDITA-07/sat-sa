# config.py
# SAT-SA Configuration and Thresholds

# EG-3: Suspiciously fast closure
FAST_CLOSURE_MINUTES = 10

# EG-4: Repeated alerts, no remediation
REPEAT_ALERT_THRESHOLD = 3
REPEAT_NO_REMEDIATION_RATIO = 0.5

# NS-1: Monitoring blind spot
BLIND_SPOT_THRESHOLD_ABSOLUTE = 2
BLIND_SPOT_RATIO = 0.1  # 10% of expected events is considered a material blind spot

# PEER-1: Peer deviation
PEER_DEVIATION_STD_MULTIPLIER = 1.0
PEER_DEVIATION_RATIO_FLOOR = 0.5

# T-1: Temporal drift
TEMPORAL_DRIFT_THRESHOLD = 0.20 # 20% drop
TEMPORAL_WINDOW_DAYS = 15 # Minimum window size

# K-1: KPI Contradiction
KPI_CONTRADICTION_THRESHOLD = 0.15 # 15% absolute difference

# I-1: Investigation Reuse
REPEATED_NOTE_THRESHOLD = 3

# Sector-Wide Aggregation
SECTOR_WIDE_PROPORTION_THRESHOLD = 0.30

# Attention Scoring
SCORE_WEIGHT_HIGH = 3
SCORE_WEIGHT_MEDIUM = 2
SCORE_WEIGHT_LOW = 1

SCORE_LEVEL_HIGH_MIN = 10
SCORE_LEVEL_MEDIUM_MIN = 5

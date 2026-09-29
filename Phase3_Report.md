# Phase 3: Core Analytical Engine - Report

**Status**: Completed
**Date**: 2026-09-28

## Accomplishments

1. **Schema Validation (`engine/schema.py`)**:
   - Implemented `validate_schema` to check for required columns, enforce enumerations (e.g., `Critical`, `High`), and verify referential integrity (e.g., alerts referencing valid assets).

2. **Execution Gap Rules (`engine/execution_gaps.py`)**:
   - **EG-1**: `check_eg1_critical_no_escalation` leverages Pandas merges to flag `Critical` / `High` alerts closed without escalation.
   - **EG-2**: `check_eg2_missing_investigation` flags High/Critical closures missing investigation evidence.
   - **EG-3**: `check_eg3_fast_closure` flags any alerts closed faster than the configured `FAST_CLOSURE_MINUTES`.
   - **EG-4**: `check_eg4_repeated_no_remediation` utilizes `.groupby()` and `.agg()` to identify assets facing repeated alerts with an unremediated ratio exceeding the threshold, pulling top evidence IDs dynamically.

3. **Negative Space Rules (`engine/negative_space.py`)**:
   - **NS-1**: `check_ns1_blind_spot` queries `assets_df` to find `Critical` assets logging fewer than `BLIND_SPOT_THRESHOLD` events.

4. **Peer Comparison (`engine/peer_comparison.py`)**:
   - **PEER-1**: `check_peer1_deviation` dynamically calculates the sector-wide mean and standard deviation for escalation rates, subsequently flagging CSEs whose escalation rates fall significantly below the threshold.

5. **Aggregation and Scoring (`engine/attention_score.py`, `engine/sector_wide.py`)**:
   - **Attention Scoring**: `compute_attention` assigns `HIGH`, `MEDIUM`, or `LOW` scores by summing weighted finding severities, and compiles the KPI reporting object.
   - **Sector-Wide Signals**: `compute_sector_wide_signals` groups findings across the sector to find rules triggering across more than 30% of CSEs, producing alerts for systemic failures.

6. **Pipeline Orchestrator (`engine/pipeline.py`)**:
   - Tied it all together in `run_analytical_engine`. This orchestrator ingests the 3 raw pandas DataFrames, runs validation, executes all rules, aggregates findings by CSE, calculates scores, and returns a dictionary payload that maps exactly to what the UI consumes.

## Next Steps
The engine logic is complete. Next is **Phase 4: Validation / Self-Check**, where we write unit tests (`tests/test_rules.py`) to formally verify that each of these rules processes DataFrame rows accurately without relying on manual observation.

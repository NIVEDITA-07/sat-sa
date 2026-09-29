# SAT-SA: The Complete Guide
## Everything You Need to Know — From Zero to Full Understanding

> **If you know absolutely nothing about SAT-SA, this document is for you.**
> It explains every concept, every rule, every button, every number, and every piece of math behind the system — in plain language first, then in technical detail.

---

## Table of Contents

1. [What is SAT-SA?](#1-what-is-sat-sa)
2. [Why Does SAT-SA Exist?](#2-why-does-sat-sa-exist)
3. [The Real-World Problem It Solves](#3-the-real-world-problem-it-solves)
4. [Key Terminology](#4-key-terminology)
5. [The Data: What Goes In](#5-the-data-what-goes-in)
6. [The Three Operating Modes](#6-the-three-operating-modes)
7. [How It Works: The Complete Backend Pipeline](#7-how-it-works-the-complete-backend-pipeline)
8. [The 9 Analytical Rules](#8-the-9-analytical-rules)
9. [The Attention Scoring System](#9-the-attention-scoring-system)
10. [The Validation System](#10-the-validation-system)
11. [The Frontend: Every Screen, Every Button, Every Box](#11-the-frontend)
12. [Frequently Asked Questions](#12-faq)
13. [Technical Architecture Map](#13-technical-architecture)

---

## 1. What is SAT-SA?

**SAT-SA** stands for **Supervisory Analytics Tool for SOC Assessment**.

In the simplest possible terms:

> SAT-SA is a **desktop application** that reads spreadsheet files (CSVs) containing cybersecurity operational data, **automatically analyzes** that data using mathematical rules, and **produces a visual report** showing where a Security Operations Center (SOC) might have problems — problems that a human supervisor should investigate further.

### What it is NOT

| It is NOT | Explanation |
|---|---|
| An AI/ML system | There is no machine learning, no neural network, no ChatGPT, no AI model of any kind. Every calculation is a deterministic math formula. |
| A cloud service | It runs 100% offline on your laptop. No internet connection is needed. No data leaves your machine. |
| A hacking tool | It does not attack anything. It only reads CSV files and analyzes numbers. |
| A replacement for human judgment | It produces signals and observations — a human examiner makes the final call. |
| A Docker/containerized app | No Docker, no Kubernetes, no cloud deployment. Just python and streamlit. |

### What it IS

- A **Python application** using the **Streamlit** framework for the visual interface
- A **rule-based analytical engine** that applies 9 deterministic rules to cybersecurity data
- A **supervisory decision-support tool** designed for government regulators (specifically India's **NCIIPC** — National Critical Information Infrastructure Protection Centre)
- Built for the **Smart India Hackathon 2026** (Problem Statement **SIH26157**)

---

## 2. Why Does SAT-SA Exist?

India has **Critical Information Infrastructure (CII)** — power grids, banks, telecom networks, hospitals, government systems. These are systems where a cyberattack could cause real-world damage.

Each critical sector has a **SOC (Security Operations Center)** — a team monitoring computer systems 24/7 for cyberattacks. When something suspicious happens, the SOC team is supposed to:

1. **Acknowledge** the alert
2. **Investigate** it
3. **Escalate** it to senior management if serious
4. **Remediate** it (fix the problem)
5. **Close** the alert with documentation

The government regulator (NCIIPC) needs to **supervise** these SOCs. But they get self-reported KPIs like "We investigated 95% of alerts." **How does the regulator know if those numbers are true?**

SAT-SA takes the raw operational data and independently calculates whether the SOC's self-reported numbers match reality. It also looks for specific patterns that indicate problems.

**In one sentence:** SAT-SA is a "trust but verify" tool for cybersecurity regulators.

---

## 3. The Real-World Problem It Solves

Imagine you are a government examiner. A bank SOC tells you: "We investigated 95% of all critical alerts this quarter."

But when SAT-SA looks at their actual operational data, it finds:

- 12 Critical alerts were closed **without any escalation** to management
- 8 High-severity cases were closed **without any investigation notes**
- 6 alerts were closed in **under 3 minutes** (suspiciously fast)
- The SOC's reported 95% investigation rate actually computes to **73%** from the raw data

Now the examiner has **evidence-based supervisory intelligence** — not just the SOC's word for it.

---

## 4. Key Terminology

### People and Organizations

| Term | What It Means |
|---|---|
| **CSE** | Critical Sector Entity. A single SOC organization being assessed. Example: CSE-BANK-01 is a banking SOC. |
| **NCIIPC** | National Critical Information Infrastructure Protection Centre. The Indian government agency that oversees CII security. |
| **Examiner / Supervisor** | The human government official who uses SAT-SA's output to make decisions. |
| **Investigator** | A person inside a SOC who investigates security alerts. Identified by IDs like INV-174. |
| **SIH** | Smart India Hackathon — the competition this was built for (Problem ID: SIH26157). |

### Data Concepts

| Term | What It Means |
|---|---|
| **Alert** | A single security event that was detected. Each alert has a unique ID like ALT-910CA8D3. |
| **Case** | An investigation record created when someone looks into an alert. Each case has a unique ID like CAS-9A2BAA39. |
| **Asset** | A computer system, server, or device being monitored. Each asset has a unique ID like AST-8C65C7F3. |
| **Severity** | How dangerous an alert is: Critical (most dangerous) to High to Medium to Low (least dangerous). |
| **Disposition / Status** | Whether an alert is still open or has been closed. |
| **Escalation** | When a SOC analyst sends an alert up the chain to a senior person or team. |
| **Investigation** | The process of analyzing an alert to determine if it is a real threat. |
| **Remediation** | The process of fixing the problem that caused the alert. |
| **KPI** | Key Performance Indicator. A number measuring how well the SOC is performing. |
| **MTTR** | Mean Time To Resolution. The average minutes to close an alert. |
| **Monitoring Coverage** | What percentage of critical assets are actually being watched by security tools. |

### SAT-SA Concepts

| Term | What It Means |
|---|---|
| **Finding** | A single detected problem. Example: CSE-BANK-01 had 12 Critical alerts closed without escalation. |
| **Rule** | A specific mathematical test that SAT-SA runs. Example: EG-1 checks for critical alerts without escalation. |
| **Attention Score** | A number representing how many problems SAT-SA found for a CSE. Higher means more concerning. |
| **Attention Level** | A category based on the score: HIGH (score >= 10), MEDIUM (score >= 5), or LOW (score < 5). |
| **Evidence ID** | The specific alert/case/asset ID that proves a finding. SAT-SA always traces back to the source record. |
| **Ground Truth** | A separate validation file with known answers — pre-planted problems that SAT-SA should detect. |
| **Sector Signal** | When the same problem appears in 30% or more of all assessed CSEs, flagged as a sector-wide systemic issue. |

---

## 5. The Data: What Goes In

SAT-SA reads **5 CSV files**. The first 4 are the assessment evidence. The 5th is a separate validation file.

### File 1: cse_profiles.csv (12 rows)

The identity card for each SOC entity.

| Column | Example | Purpose |
|---|---|---|
| cse_id | CSE-BANK-01 | Unique identifier for the entity |
| sector | Finance | Which industry sector |
| cse_name | CSE-BANK-01 Corporation | Human-readable name |
| organization_size | Large | How big the organization is |
| assessment_period | Q1 2026 | Which quarter is being assessed |
| criticality_tier | Tier 3 | How critical to national infrastructure |
| reported_escalation_rate | 0.90 | Self-reported: We escalated 90% of critical alerts |
| reported_investigation_rate | 0.95 | Self-reported: We investigated 95% |
| reported_monitoring_coverage | 0.98 | Self-reported: 98% of our assets are monitored |
| reported_mttr_minutes | 67 | Self-reported: Average resolution time is 67 minutes |

These reported numbers are what the SOC claims. SAT-SA checks if they match reality.

### File 2: assets.csv (1200 rows)

Every computer system or device that the SOC monitors.

| Column | Example | Purpose |
|---|---|---|
| asset_id | AST-8C65C7F3 | Unique identifier |
| cse_id | CSE-BANK-01 | Which SOC entity owns this asset |
| criticality | Critical | How important this asset is |
| asset_type | Server | What kind of device |
| expected_monitoring | Yes | Should this asset be monitored? |
| observed_monitoring_events | 4500 | How many monitoring log entries were actually recorded |
| expected_events_per_day | 50 | How many events per day should there be |

### File 3: alerts.csv (35041 rows)

Every security alert generated during the assessment period.

| Column | Example | Purpose |
|---|---|---|
| alert_id | ALT-910CA8D3 | Unique identifier |
| cse_id | CSE-TELECOM-02 | Which SOC entity received this alert |
| asset_id | AST-FA28CC46 | Which asset triggered the alert |
| severity | Critical | How dangerous |
| created_at | 2026-03-06 11:06:00 | When the alert was created |
| closed_at | 2026-03-06 12:08:00 | When the alert was closed |
| status | Closed | Is it still open or closed? |
| escalated | Yes / No | Was it sent to management? |
| investigation_present | Yes / No | Was it investigated? |
| remediation_status | Closed / Open | Was the fix applied? |

### File 4: cases.csv (33100 rows)

Investigation records — what happened when someone investigated an alert.

| Column | Example | Purpose |
|---|---|---|
| case_id | CAS-9A2BAA39 | Unique identifier |
| cse_id | CSE-TELECOM-02 | Which SOC entity |
| primary_alert_id | ALT-910CA8D3 | Which alert triggered this case |
| investigator_id | INV-954 | Who investigated |
| investigation_note | Reviewed alert; no malicious activity identified. | What the investigator wrote |
| investigation_status | Completed | Was the investigation finished? |
| remediation_status | Closed | Was the fix applied? |

### File 5: validation_ground_truth.csv (2104 rows)

This file is NEVER read by the analytical engine. It is a separate answer key used only to verify that SAT-SA's rules are working correctly.

### How They Connect (Data Relationships)

```
cse_profiles.cse_id
    |
    v
assets.cse_id          (Which assets belong to which CSE?)
    |
    v
alerts.asset_id        (Which alerts are about which asset?)
    |
    v
alerts.case_id         (Which case investigated this alert?)
    |
    v
cases.case_id          (Full investigation details)
    |
    v
cases.cse_id  -->  cse_profiles.cse_id  (Back to the CSE)
```

SAT-SA can trace: CSE -> Asset -> Alert -> Case and reverse.

---

## 6. The Three Operating Modes

### Mode 1: CONTROLLED_DEMO (Default)

- Loads the 5 CSV files from the data folder automatically
- For demonstrating SAT-SA's capabilities to evaluators, judges, or stakeholders
- Pre-generated synthetic dataset with deliberately injected anomalies
- CSV column names already match SAT-SA's internal format
- All 9 rules run with full evidence

### Mode 2: PUBLIC_SOC

- Simulates loading data from a public cybersecurity benchmark dataset
- Same CSV files but with columns renamed to mimic a public dataset (e.g., alert_id becomes event_id)
- Some columns are deliberately dropped (like escalated, investigation_present)
- Rules that depend on missing columns show Insufficient Evidence
- Proves SAT-SA can gracefully handle incomplete data

### Mode 3: CSE_SUBMISSION

- Allows a real SOC entity to upload their own operational data for assessment
- Production use — when a real CSE submits data to the regulator
- Uses the same format as CONTROLLED_DEMO
- Rules that can run depend on what columns the CSE provides

### Key Difference Summary

| Feature | CONTROLLED_DEMO | PUBLIC_SOC | CSE_SUBMISSION |
|---|---|---|---|
| Data loaded from | data/ folder | data/ folder (renamed columns) | User upload |
| Column names | Standard | Non-standard (mapped) | Standard |
| Evidence completeness | Full | Partial (some missing) | Varies |
| Rules that can run | All 9 | Fewer (some disabled) | Depends |
| Validation possible? | Yes | Limited | No |
| Purpose | Demo and validation | Interoperability proof | Real-world use |

---

## 7. How It Works: The Complete Backend Pipeline

Here is the exact sequence of operations that happens when SAT-SA starts.

### Step 1: Bootstrap (engine/bootstrap.py)

Reads all 4 CSV files from disk, passes them to the ingestion layer, runs the analytical engine, loads the ground truth file separately for validation, and returns complete results to the UI.

### Step 2: Ingestion and Normalization (engine/ingestion.py)

The translation layer. Converts whatever column names the source data has into SAT-SA's standard internal format.

Example: If the raw CSV has a column called "status" (values: Closed, Open), SAT-SA maps it to its internal column "disposition".

Missing data handling: If a column does not exist in the source, every row gets the value NOT_AVAILABLE. This is critically important — NOT_AVAILABLE is NOT the same as No. It means we do not have this information — it does NOT mean this thing did not happen.

Computed fields:
- closure_time_minutes = difference between closed_at and created_at timestamps, in minutes
- remediation_present = derived from remediation_status (Closed -> Yes, Open -> No)

### Step 3: Data Store Construction (engine/data_store.py)

All data is loaded into the DataStore — an in-memory data structure that provides fast access to any record.

The DataStore builds indexes for instant lookup:
- Given an alert_id, get all details about that alert (O(1) lookup)
- Given a cse_id, get all their alerts, assets, and cases (filtered query)
- Given a case_id, get the full investigation record (O(1) lookup)

The DataStore also validates referential integrity — checking that every asset_id in alerts exists in the assets table, every cse_id in alerts exists in profiles, and every alert_id in cases exists in alerts.

### Step 4: Schema Validation (engine/schema.py)

Checks that all required columns exist and contain valid values. Severities must be Critical/High/Medium/Low/NOT_AVAILABLE. Referential integrity warnings are logged but do not crash the system.

### Step 5: Evidence Coverage Check (engine/evidence_coverage.py)

Before running any rules, SAT-SA checks which rules CAN run for each CSE based on what data is available.

Example: Rule EG-1 needs the escalated column. If it is all NOT_AVAILABLE, EG-1 is marked as INSUFFICIENT EVIDENCE and will not generate findings for that CSE.

This prevents false accusations — if the data does not exist, SAT-SA does not guess.

### Step 6: Data Quality Checks (engine/data_quality.py)

- DQ-1: Duplicate alert records (same alert_id appears more than once)
- DQ-2: Missing severity (alert has no severity assigned)
- DQ-3: Impossible lifecycle (negative closure time — alert closed before it was created)

### Step 7: Execute the 9 Analytical Rules

Each rule is a separate Python module that iterates through each CSE, retrieves that CSE's data from the DataStore, applies a mathematical condition, and if met, generates a Finding with specific evidence.

### Step 8: Filter Findings by Evidence Availability

After all rules have run, SAT-SA filters out any findings for CSEs where the evidence was insufficient.

### Step 9: Compute Attention Scores (engine/attention_score.py)

Score = (HIGH findings x 3) + (MEDIUM findings x 2) + (LOW findings x 1)

Score >= 10 -> HIGH Attention. Score >= 5 -> MEDIUM Attention. Score < 5 -> LOW Attention.

### Step 10: Compute Sector-Wide Signals (engine/sector_wide.py)

Looks across ALL CSEs. If any single rule triggers for 30% or more of entities, it is flagged as a systemic sector-wide signal.

### Step 11: Validation Against Ground Truth (engine/validation.py)

Compares detected findings against the known answer key to measure detection accuracy.

### Step 12: Results Sent to UI

All results are packaged into a Python dictionary and passed to the Streamlit frontend for visualization.

---

## 8. The 9 Analytical Rules

### Rule EG-1: Critical Alert Without Escalation

- ID: EG-1 | Category: Execution Gap | Severity: Always HIGH
- File: engine/execution_gaps.py

Detects Critical or High-severity alerts that were closed but never escalated to management.

Why it matters: Critical and High-severity alerts are supposed to be escalated to a Tier-2 team. If someone just closes a Critical alert without telling management, that is a serious process failure.

The exact logic:

```
For each CSE:
  1. Get all alerts where severity = Critical OR High
  2. AND closed_at is present (alert was actually closed)
  3. Among those, count how many have escalated = No
  4. If count > 0 -> generate finding

  violation_rate = not_escalated_count / total_critical_closed_count
```

Example finding: "12 of 45 critical alerts (27%) were closed without mandatory Tier-2 supervisor escalation."

### Rule EG-2: Missing Investigation Evidence

- ID: EG-2 | Category: Execution Gap | Severity: HIGH if any Critical alerts affected, otherwise MEDIUM
- File: engine/execution_gaps.py

Detects High/Critical alerts that were closed without any investigation being performed.

The exact logic:

```
For each CSE:
  1. Get all alerts where severity = Critical OR High AND disposition = Closed
  2. Check if investigation_present = No
     OR if the linked case has investigation_status = Bypassed
  3. Count violations
  4. If count > 0 -> generate finding
```

Note: If investigation_present = NOT_AVAILABLE, it does NOT count as No. SAT-SA only flags explicitly recorded absences.

### Rule EG-3: Suspiciously Fast Closure

- ID: EG-3 | Category: Execution Gap
- Severity: HIGH if >= 15% of alerts are fast-closed, MEDIUM if >= 5%, LOW otherwise
- Threshold: 10 minutes (configurable in config.py as FAST_CLOSURE_MINUTES)
- File: engine/execution_gaps.py

Detects alerts that were closed in under 10 minutes.

The exact logic:

```
For each CSE:
  1. Get all alerts where disposition = Closed
  2. Calculate closure_time_minutes = (closed_at - created_at) / 60
  3. Count alerts where closure_time_minutes < 10
  4. If count > 0 -> generate finding

  violation_rate = fast_closed_count / total_closed_count
```

### Rule EG-4: Repeated Alerts Without Remediation

- ID: EG-4 | Category: Execution Gap | Severity: Always HIGH
- Thresholds: >= 3 alerts on same asset, >= 50% unremediated
- File: engine/execution_gaps.py

Detects assets that keep generating security alerts but the underlying problem is never fixed.

The exact logic:

```
For each CSE:
  For each asset:
    1. Count total alerts for this asset
    2. Count alerts where remediation_present = No
    3. If total >= 3 AND (unremediated / total) >= 50%
       -> generate finding for this asset

  One finding per violating asset (not per alert).
```

### Rule NS-1: Monitoring Blind Spot (Negative Space Detection)

- ID: NS-1 | Category: Negative Space
- Severity: HIGH if >= 30% blind spots, MEDIUM if >= 10%, LOW otherwise
- File: engine/negative_space.py

Detects critical assets that should be monitored but have zero monitoring events recorded.

This is negative space analysis — looking for what is missing rather than what is present. If a critical server has expected_monitoring = Yes but observed_monitoring_events = 0, the security tools are not watching that server.

The exact logic:

```
For each CSE:
  1. Get all assets where expected_monitoring is Yes, High, or Standard
  2. Count assets where observed_monitoring_events = 0
  3. If count > 0 -> generate finding

  blind_rate = zero_event_assets / total_expected_monitoring_assets
```

### Rule PEER-1: Peer Deviation (Comparative Analysis)

- ID: PEER-1 | Category: Peer Deviation
- Severity: HIGH if rate < 25% of sector mean, MEDIUM otherwise
- Threshold: Below (mean - 1.0 x standard deviation) OR below 50% of mean
- File: engine/peer_comparison.py

Detects a CSE whose escalation rate is significantly below their sector peers.

The exact math:

```
1. Group all CSEs by sector (Finance, Telecom, Power, etc.)
2. For each sector with >= 2 CSEs:
   a. Calculate each CSE's operational escalation rate:
      rate = (critical/high alerts with escalated = Yes) / (total critical/high alerts)
   b. Calculate sector mean = average of all rates
   c. Calculate sector standard deviation (sample std, n-1)
   d. Threshold = max(mean - 1.0 x std, 0.5 x mean)
   e. If a CSE's rate < threshold -> flag as peer deviation
```

This rule requires at least 2 CSEs in the same sector to compute a meaningful comparison.

### Rule T-1: Temporal Drift (Performance Deterioration Over Time)

- ID: T-1 | Category: Temporal Drift
- Severity: HIGH if drop >= 40 percentage points, MEDIUM otherwise
- Threshold: >= 20% drop (TEMPORAL_DRIFT_THRESHOLD)
- Minimum window: 15 days per half (TEMPORAL_WINDOW_DAYS)
- File: engine/temporal_drift.py

Detects a CSE whose investigation rate has gotten significantly worse over time.

The exact math:

```
For each CSE:
  1. Sort all alerts by created_at timestamp
  2. Find the date range (earliest alert to latest alert)
  3. If range < 30 days (2 x 15), skip (not enough data)
  4. Split alerts into two halves: baseline (first 50%) and recent (second 50%)
  5. For each half, calculate investigation rate:
     rate = (closed alerts where investigation_present != No) / (total closed alerts)
  6. difference = baseline_rate - recent_rate
  7. If difference >= 0.20 (20% drop) -> generate finding
```

### Rule K-1: KPI Contradiction (Reported vs Observed Discrepancy)

- ID: K-1 | Category: KPI Contradiction
- Severity: HIGH if discrepancy >= 40 percentage points, MEDIUM otherwise
- Threshold: >= 15% absolute difference (KPI_CONTRADICTION_THRESHOLD)
- File: engine/kpi_contradiction.py

Detects cases where the CSE's self-reported KPI does not match what SAT-SA calculates from the raw data.

The exact math:

```
For each CSE:
  1. Read reported_escalation_rate from cse_profiles.csv (e.g., 0.90 = 90%)
  2. Calculate observed escalation rate from alerts:
     observed = (critical/high alerts with escalated = Yes) / (total critical/high closed alerts)
  3. difference = reported - observed
  4. If difference > 0.15 (15%) -> generate finding

  Same logic is applied separately for investigation rate.
```

This rule generates up to 2 findings per CSE — one for escalation, one for investigation.

### Rule I-1: Investigation Note Reuse (Boilerplate Detection)

- ID: I-1 | Category: Investigation Reuse
- Severity: HIGH if max frequency >= 6, MEDIUM otherwise
- Threshold: >= 3 identical notes from the same investigator (REPEATED_NOTE_THRESHOLD)
- File: engine/investigation_reuse.py

Detects investigators who copy-paste the same investigation note into multiple case records.

The exact logic:

```
For each CSE:
  For each investigator:
    1. Normalize their investigation notes (lowercase, remove punctuation, collapse whitespace)
    2. Group by normalized note text
    3. If any single note appears >= 3 times for this investigator:
       -> generate ONE finding per investigator

  The finding includes ALL cases from that investigator as evidence.
```

Text normalization example:
- Original: "Reviewed alert; no malicious activity identified."
- Normalized: "reviewed alert no malicious activity identified"

---

## 9. The Attention Scoring System

### The Formula

```
Attention Score = (HIGH findings x 3) + (MEDIUM findings x 2) + (LOW findings x 1)
```

### The Levels

| Score Range | Level | What It Means |
|---|---|---|
| >= 10 | HIGH | Multiple serious issues detected. Immediate supervisory attention recommended. |
| 5 to 9 | MEDIUM | Some concerns identified. Review during next scheduled audit. |
| 0 to 4 | LOW | Minimal or no issues detected. Routine monitoring sufficient. |

### Example Calculation

Suppose CSE-BANK-02 has these findings:
- EG-1 (Critical no escalation) -> HIGH -> +3
- K-1 (KPI contradiction 1) -> MEDIUM -> +2
- K-1 (KPI contradiction 2) -> MEDIUM -> +2
- PEER-1 (Peer deviation) -> HIGH -> +3

Total Score = 3 + 2 + 2 + 3 = 10 -> HIGH Attention

### Important Properties

1. **Deterministic:** The same data always produces the same score. There is no randomness.
2. **Additive:** Scores stack — more problems = higher score.
3. **Transparent:** Every point can be traced back to a specific finding, which traces back to specific evidence IDs.
4. **Configurable:** The weights (3/2/1) and thresholds (10/5) are defined in config.py.

---

## 10. The Validation System

### The Problem of Trust

If SAT-SA claims it can detect supervision failures, how do we prove it actually works?

### The Solution: Ground Truth Validation

We created validation_ground_truth.csv containing 2,104 known anomaly scenarios — specific problems deliberately planted in the operational data.

Critical design principle: The ground truth file is NEVER read by the analytical engine when generating findings. The engine only reads the 4 operational files. The ground truth is loaded separately, after the engine has finished, to compare results.

### How Validation Works

```
1. Run SAT-SA engine using ONLY: cse_profiles.csv, assets.csv, alerts.csv, cases.csv
2. Collect all generated findings
3. Load validation_ground_truth.csv SEPARATELY
4. For each row in ground truth:
   a. Look for a matching finding (same cse_id, same rule, same entity)
   b. If found -> PASS (True Positive)
   c. If not found -> FAIL (False Negative)
5. Count findings that were not in ground truth -> Unexpected Detections
```

### Current Results

| Metric | Value |
|---|---|
| Ground-truth scenarios | 2,104 |
| Detected (True Positives) | ~2,040+ |
| Not detected (False Negatives) | ~60 |
| Detection rate | ~97-98% |
| Unexpected detections | ~162 |

---

## 11. The Frontend: Every Screen, Every Button, Every Box

SAT-SA has 4 pages accessible from the sidebar.

### Page 1: Overview (Supervisory Dashboard)

The landing page — the first thing a supervisor sees.

**Top Metrics Row (3 boxes):**
- Total CSEs Assessed: Count of unique cse_id values
- High Attention: How many CSEs have HIGH attention level
- Findings Generated: Total number of individual findings

**Sector-Wide Supervisory Signal (Yellow Banner):**
If any single rule triggers for >= 30% of all assessed CSEs, it appears here. The Systemic Blindspot button takes you to the Review Queue page pre-filtered for that rule.

**Supervisory Attention Landscape (Left Column Table):**
A ranked table of all CSEs sorted by attention score. Each row shows CSE ID, Score, Level badge, and Top Finding.

**Expected vs Observed Evidence (Right Column Flow Chart):**
A workflow diagram showing 5 stages: Alert Detection -> Investigation -> Escalation -> Remediation -> Closure. Select a CSE from the dropdown to see which stages had evidence. The View evidence drilldown button takes you to the CSE Assessment page.

**Operational Evidence Cards (3 cards at bottom):**
Summary cards for EG-1, EG-2, and EG-3. The View Details buttons take you to the Review Queue filtered for that rule.

### Page 2: CSE Assessment (Deep Dive)

Focuses on a single CSE.

**CSE Selector + Score Badge:** Dropdown to select a CSE, attention badge, and WHY THIS SCORE panel showing each finding's contribution.

**KPI Reporting vs Operational Evidence:** Two cards side by side. Left shows self-reported KPIs with green checkmarks. Right shows what SAT-SA actually found in the data.

**Explicit Reported vs Observed Comparison (4 cards):** Investigation Rate, Escalation Rate, Avg MTTR, and Monitoring Coverage — each showing REPORTED value, OBSERVED value, and DIFFERENCE.

**Peer Benchmark Analysis:** If the CSE has a peer deviation finding, shows the CSE's escalation rate vs sector average with progress bars.

**Official Supervisory Observation Memo:** A Generate Supervisory Memo button creates a formal text document. A Download Memo button saves it as a .txt file.

**Evidence Coverage:** Shows which types of evidence are available for this CSE.

**WHY Panel — Traceable Evidence Breakdown:** Expandable panels for every finding. Each shows the explanation, source metadata, normalized field, deterministic equation, attention impact, and a full data table of the raw source records that triggered the finding.

### Page 3: Review Queue (Priority Triage)

Shows ALL findings across ALL CSEs, ranked by severity.

**Filter Bar:** Filter by CSE, Severity, Rule, or free-text search.

**Ranked Table:** Up to 20 findings sorted by priority (HIGH first).

**Inspection Drawer:** Select a finding to see full details including WHY WAS THIS FLAGGED, EVIDENCE REFERENCES, and RECOMMENDED ACTION.

### Page 4: Data and Validation

Shows the data pipeline and validation results.

**Data Ingestion Pipeline (5 steps):** Source Detection, Record Count, Field Mapping table, Evidence Coverage chart, and Data Provenance.

**Ground Truth Validation:** True Positives, False Negatives, Unexpected Detections, Detection Rate, and a detailed scenario-by-scenario table.

---

## 12. Frequently Asked Questions

**Is this AI?**
No. Zero AI, zero machine learning, zero neural networks, zero LLMs. Every calculation is a deterministic mathematical formula.

**Can it analyze any SOC's data?**
Yes, as long as the data is in CSV format with the required columns. If some columns are missing, SAT-SA gracefully degrades.

**Does my data leave my computer?**
No. SAT-SA runs 100% locally. There are no API calls, no cloud services, no telemetry.

**How accurate is it?**
Against the controlled validation dataset (2,104 known scenarios), SAT-SA achieves a ~98% detection rate.

**Can the thresholds be changed?**
Yes. All thresholds are defined in config.py. A regulator can adjust them.

**What happens when data is missing?**
NOT_AVAILABLE is NEVER treated as No. If escalation data is missing, SAT-SA will NOT accuse the CSE of failing to escalate. It will simply say escalation evidence is unavailable and disable the rules that need it.

**Can I add new rules?**
Yes. Each rule is an independent Python module. Create a new file in engine/, write a function that takes a DataStore and returns a list of Finding objects, and add it to the pipeline in engine/pipeline.py.

---

## 13. Technical Architecture Map

### File Structure

```
sat-sa/
  app.py                      -- Streamlit entry point
  config.py                   -- All configurable thresholds
  requirements.txt            -- Python dependencies (streamlit, pandas, numpy)
  integration_test.py         -- Automated test runner

  data/
    cse_profiles.csv          -- 12 rows: CSE identity + reported KPIs
    assets.csv                -- 1200 rows: IT assets
    alerts.csv                -- 35041 rows: security alerts
    cases.csv                 -- 33100 rows: investigation records
    validation_ground_truth.csv -- 2104 rows: answer key (never read by engine)

  engine/
    bootstrap.py              -- Orchestrator: loads data, runs pipeline
    ingestion.py              -- Data normalization + column mapping
    data_store.py             -- In-memory data relationship layer
    schema.py                 -- Schema validation
    evidence_coverage.py      -- Evidence availability checker
    data_quality.py           -- DQ-1, DQ-2, DQ-3 checks
    execution_gaps.py         -- EG-1, EG-2, EG-3, EG-4 rules
    negative_space.py         -- NS-1 rule
    peer_comparison.py        -- PEER-1 rule
    temporal_drift.py         -- T-1 rule
    kpi_contradiction.py      -- K-1 rule
    investigation_reuse.py    -- I-1 rule
    attention_score.py        -- Score computation
    sector_wide.py            -- Sector-wide signal aggregation
    findings.py               -- Finding + CSEAttention data classes
    pipeline.py               -- Rule orchestration pipeline
    validation.py             -- Ground truth comparison

  ui/
    styles.py                 -- CSS design system
    sidebar.py                -- Navigation sidebar
    overview.py               -- Page 1: Supervisory Overview
    cse_detail.py             -- Page 2: CSE Assessment
    review_queue.py           -- Page 3: Review Queue
    data_validation.py        -- Page 4: Data and Validation
```

### Dependencies

The entire system runs on just 3 Python packages:

| Package | Purpose |
|---|---|
| streamlit | Web-based UI framework |
| pandas | Data manipulation and analysis |
| numpy | Numerical computations |

No scikit-learn. No TensorFlow. No PyTorch. No external APIs.

### How to Run

```bash
pip install -r requirements.txt
python -m streamlit run app.py
python integration_test.py
```

The application opens in your browser at http://localhost:8501.

---

> Final Note: SAT-SA is a decision-support tool. Every finding is a signal, not a verdict. The system is designed to surface patterns that deserve human review — not to replace the examiner's judgment. The mathematical rules are transparent, the evidence is traceable, and the thresholds are configurable. Nothing is a black box.

---

SAT-SA | Supervisory Analytics Tool for SOC Assessment | SIH26157 | NCIIPC
Built for the Smart India Hackathon 2026

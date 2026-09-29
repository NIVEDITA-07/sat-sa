# SAT-SA: Master Architecture & Submission Document
**Project:** Supervisory Analytics Tool for SOC Assessment (SAT-SA)
**Problem Statement:** SIH26157 | NCIIPC | Cybersecurity / Software

---

## 1. Executive Summary & SIH Criteria Met
SAT-SA is an enterprise-grade supervisory analytics tool built to help examiners assess whether Critical Sector Entities (CSEs) are operating their Security Operations Centres (SOCs) effectively. It mathematically identifies the "negative space"—expected SOC actions that failed to occur—and provides undeniable, raw telemetry proof for every finding.

**Strict Criteria Successfully Met:**
*   **100% Offline / Air-Gapped Capable:** The entire application runs locally. No external APIs, CDNs, or telemetry calls are made, ensuring absolute security for sensitive NCIIPC data.
*   **Zero AI / ML:** The engine avoids "black box" heuristic guessing. All decisions are derived through 100% deterministic mathematical logic and Boolean rule sets, guaranteeing repeatability and fairness.
*   **Deep Traceability:** Every supervisory flag maps 1:1 to the exact raw CSV rows (Evidence IDs) that triggered it, eliminating false positives and providing legal proof for audits.

---

## 2. Core Innovations (The "Wow" Factor)
Instead of just showing raw tables of alerts, SAT-SA introduces several highly innovative visualization and workflow concepts:
1.  **KPI Reporting vs. Reality Contrast Panel:** The dashboard displays a side-by-side comparison of a CSE's *self-reported* KPIs (e.g., "94% Escalation SLA") directly against the *operational evidence* (e.g., "12 Critical Alerts closed without escalation"). This instantly highlights metric gaming.
2.  **Expected vs. Observed Workflow Visualizer:** A dynamic pipeline diagram that maps the standard SOC lifecycle (Alert &rarr; Investigate &rarr; Escalate &rarr; Remediate). It uses the data to pinpoint the exact stage where a specific CSE's process broke down (marked in red).
3.  **Automated Supervisory Observation Memo:** Translates the mathematical findings into an examiner-ready, formal text document that can be downloaded with a single click and attached to official audits.
4.  **Peer Benchmark Deviations:** Automatically computes sector-wide averages and alerts examiners if a specific CSE falls statistically outside the standard deviation of its peers.

---

## 3. Frontend Architecture (UI / UX)
Built using Python and **Streamlit**, the frontend is designed to look like a premium, enterprise-level application rather than a basic script.
*   **Custom Styling Engine (`ui/styles.py`):** Features a bespoke "Deep Indigo / Violet" design system. It uses a custom `render_html()` parsing engine that safely injects complex CSS Grids and flexbox layouts while bypassing Streamlit's native markdown restrictions.
*   **Tabbed Single-Page Application (SPA):** Uses a seamless sidebar router (`app.py` & `ui/sidebar.py`) to navigate between four primary views without reloading the page state.
*   **The "WHY" Evidence Expanders:** Every finding in the UI features a dropdown that queries the active Pandas DataFrames in memory and renders the exact unmodified raw row that proved the violation.

---

## 4. Backend Architecture (Core Analytical Engine)
The backend (`engine/` directory) is a modular, pipeline-driven architecture utilizing **Pandas** for high-speed, vectorized data evaluation.

*   **`bootstrap.py`**: The entrypoint that loads the `alerts.csv`, `assets.csv`, and `cases.csv` fixtures from disk.
*   **`schema.py`**: A strict gatekeeper that validates columns, Enum values (e.g., Ensuring severity is only Critical/High/Medium/Low), and verifies referential integrity (ensuring an alert's `asset_id` actually exists in the asset catalog).
*   **`pipeline.py`**: The orchestrator that passes the DataFrames through all rule modules, flattens the results, computes the final Attention Scores, and returns canonical `CSEAttention` python dataclasses to the UI.

---

## 5. Mathematical & Logical Workings (The Rules Engine)
The system uses precise dataset merging, grouping, and statistical math to identify failures.

### A. Execution Gaps (`engine/execution_gaps.py`)
These rules catch direct violations of standard operating procedures.
*   **EG-1 (Critical Alert Without Escalation):**
    *   *Logic:* Filters `alerts_df` where `severity IN ('Critical', 'High')` AND `disposition == 'Closed'` AND `escalated == 'No'`.
*   **EG-2 (Missing Investigation):**
    *   *Logic:* Filters where `severity IN ('Critical', 'High')` AND `investigation_present == 'No'`.
*   **EG-3 (Suspiciously Fast Closure):**
    *   *Logic:* Filters where `closure_time_minutes < 10` (configured threshold). Highlights potential "ticket-closing" automation bypassing human review.
*   **EG-4 (Repeated Alerts, No Remediation):**
    *   *Mathematics:* Groups data by `[cse_id, asset_id]`. Calculates `total_alerts` and `unremediated_alerts`. 
    *   *Trigger:* `(total_alerts >= 3) AND (unremediated_alerts / total_alerts >= 0.5)`. This proves a SOC is repeatedly bombarded by the same issue without fixing the root cause.

### B. Negative Space (`engine/negative_space.py`)
These rules look for what is *missing* from the data.
*   **NS-1 (Monitoring Blindspot):**
    *   *Logic:* Queries `assets_df` where `criticality == 'Critical'` but `observed_monitoring_events < 2`. This identifies highly important infrastructure that the SOC is entirely blind to.

### C. Peer Comparison (`engine/peer_comparison.py`)
*   **PEER-1 (Escalation Rate Deviation):**
    *   *Mathematics:* Calculates the escalation rate ($R$) for each CSE. Calculates the sector-wide Mean ($\mu$) and Standard Deviation ($\sigma$).
    *   *Trigger:* Flags any CSE where their specific rate $R < (\mu - 1\sigma)$. This mathematically proves the entity is performing significantly worse than the industry average, rather than relying on an arbitrary hardcoded percentage.

### D. Scoring & Aggregation (`engine/attention_score.py`)
*   Every finding is assigned a weight (`HIGH`=3, `MEDIUM`=2, `LOW`=1). 
*   The final Attention Score determines the entity's supervisory level (`Score >= 10` is HIGH Attention; `Score >= 5` is MEDIUM).
*   **Sector-Wide Signals:** The engine groups findings by `rule_id` and checks the proportion of affected CSEs. If $Proportion \ge 0.30$ (30%), it triggers a sector-wide systemic alert (e.g., "40% of the grid is failing to remediate Firewall alerts").

---

## Conclusion
SAT-SA completely replaces the manual, sampling-based audits currently plaguing examiners. By utilizing deterministic data pipelines and an intuitive, evidence-first UI, SAT-SA allows a single NCIIPC examiner to mathematically verify the operational integrity of dozens of SOCs simultaneously.

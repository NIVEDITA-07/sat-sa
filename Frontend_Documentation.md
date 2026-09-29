# SAT-SA: Examiner's User Manual

Welcome to the **Supervisory Analytics Tool for SOC Assessment (SAT-SA)**. 

If you are an NCIIPC Examiner logging into this dashboard for the first time, this guide explains exactly what this tool is for, what each screen means, and how you should use it to conduct your assessments.

---

## What is SAT-SA?
SAT-SA helps you assess whether Critical Sector Entities (CSEs) are actually operating their Security Operations Centres (SOCs) effectively. Instead of manually sampling alerts, SAT-SA ingests raw SOC data (alerts, cases, assets) and mathematically verifies if the SOC is doing its job. It finds the "negative space"—the things the SOC *should* have done but didn't.

---

## 1. Overview Page (The Sector-Wide View)
**Purpose:** This is your starting point. It gives you a bird's-eye view of the entire critical sector's health. 

* **KPI Cards (Top):** Shows you immediately how many CSEs require your attention. 
  * **High Attention (Red):** These CSEs have critical failures (e.g., ignoring severe alerts). They need your immediate intervention.
  * **Medium Attention (Yellow):** Elevated procedural issues.
  * **Low Attention (Green):** Operating normally.
* **Sector-Wide Signal Banner:** If SAT-SA detects a problem happening across *multiple* CSEs (e.g., a systemic failure to patch a specific firewall), it alerts you here. It means the issue isn't just one bad SOC, but a sector-wide blindspot.
* **CSE Supervisory Landscape (Table):** Your triage list. It ranks all entities by their "Attention Score". You can use the search bar to find a specific entity. **Action:** Look at the CSEs at the top of this list first.
* **Expected vs Observed Workflow (Visualizer):** This is a forensic trace. Select a CSE to see its pipeline. The left column shows what a SOC *should* do (Alert → Investigate → Escalate → Remediate). The right column shows what they *actually* did. If you see a red **"✕ Missing"**, it means the SOC dropped the ball at that exact stage.

---

## 2. CSE Assessment Page (The Entity Deep-Dive)
**Purpose:** Once you've identified a problematic CSE from the Overview page, you come here to investigate them specifically.

* **Entity Selector (Top Left):** Choose the CSE you want to audit.
* **KPI Reporting vs. Operational Evidence (The Contrast Panel):** This is the most powerful tool for an examiner. 
  * **Left Side (Reported KPIs):** What the CSE *claims* they are doing (e.g., "We escalate 96% of critical alerts!").
  * **Right Side (Reality/Evidence):** What SAT-SA's data actually proves. If the left side looks great, but the right side shows 12 Critical Alerts were closed without escalation, you know the CSE has a major blindspot (or is falsifying metrics).
* **Peer Benchmark Analysis:** A bar chart comparing this specific CSE's failure rate against the average of all other CSEs in the sector. It helps you determine if they are an outlier.
* **Official Supervisory Observation Memo:** Once you are done reviewing the CSE, click "Generate Supervisory Memo". The system will automatically draft a formal, formatted text document summarizing the failures and the recommended actions. You can download this `.txt` file and attach it directly to your official NCIIPC audit report.
* **WHY Panel (Traceable Evidence Breakdown):** This lists every single violation found for this CSE. 
  * **Action:** Click on a finding to expand it. It will explain exactly *why* it was flagged, and most importantly, it will display the **Raw Source Records** (the exact rows from the CSV file) so you have undeniable proof to show the CSE's Chief Information Security Officer (CISO) during an audit.

---

## 3. Priority Review Queue
**Purpose:** Instead of looking at CSEs one by one, this page gives you a master list of **every single violation** found across the entire sector, ranked by severity.

* **Filters (Top):** Use these to narrow down your work. For example, you can filter by "Severity: HIGH" to only see the most dangerous violations across the country today.
* **Queue Table:** Your to-do list. 
* **Inspection Drawer (Right Side):** Select an item number from the dropdown to inspect it. The drawer will slide open and give you a plain-English explanation of the failure and a **Recommended Action** (e.g., "Immediate corrective review requested within 30 days"). 

---

## 4. Data & Validation Page
**Purpose:** This is the administrative backend for the examiner. 

* **Upload SOC Audit Artifacts:** In a real-world scenario, the CSEs send you their raw CSV files periodically. You will upload those files here.
* **Schema & Referential Integrity Check:** SAT-SA automatically runs checks on the uploaded data to ensure it isn't corrupted and has all the required columns. If any checks fail, you must ask the CSE to re-submit their data.
* **Active In-Memory Telemetry Data:** These tabs let you browse the raw, unedited data that is currently loaded into the system, just in case you need to verify something manually.

---

## Typical Examiner Workflow
1. Open the **Overview** tab to see the sector's general health.
2. Check the **Supervisory Landscape** table for any CSEs marked "High Attention".
3. Navigate to the **CSE Assessment** tab and select the worst-performing CSE.
4. Compare their self-reported KPIs against the operational evidence.
5. Drill down into the **WHY Panel** to see the raw data proving their failures.
6. Generate and download the **Supervisory Memo**.
7. (Optional) Go to the **Priority Review Queue** to see if any specific rules are being violated repeatedly across multiple entities.

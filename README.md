<div align="center">

# SAT-SA: Supervisory Analytics Tool for SOC Assessment
### 🛡️ Smart India Hackathon (SIH 26157) — NCIIPC Use Case

*A Deterministic, Heterogeneous Supervisory Engine that bridges the gap between Operational SOC Evidence and Executive Human Adjudication.*

[**Try the Interactive Demo**](#try-the-demo) | [**View Architecture**](#core-architecture) | [**Data & Requirements**](#requirements--installation) | [**How It Works**](#workflow--user-experience)

</div>

---

## 📖 The Problem
**National Critical Information Infrastructure Protection Centre (NCIIPC)** requires a way to assess the cybersecurity posture of Critical Sector Entities (CSEs) across the nation. Currently, auditing these entities is a massive, manual effort. 

The primary challenge is that **every organization uses different tools, vendors, and formats (Splunk, QRadar, Service-Now, Jira, etc.)**. Forcing hundreds of organizations to adopt a single logging standard is impossible.

## 💡 The SAT-SA Solution
SAT-SA (Supervisory Analytics Tool for SOC Assessment) is an offline, deterministic, and highly responsive local application that acts as a **Supervisory Assistant**. It does **not** rely on AI, ML, or Cloud APIs, ensuring absolute data privacy and explainability.

**SAT-SA does not force entities to change their tools.** Instead, it ingests heterogeneous evidence logs, semantically normalizes them into a canonical format, checks the data quality, and executes a deterministic rule engine to identify **Execution Gaps** (e.g., Critical alerts closed without investigation). It then presents these gaps to a human Examiner for final adjudication.

---

## 🚀 Key Features

- **Heterogeneous Ingestion Engine**: Automatically maps disparate log formats (Splunk, QRadar, generic CSVs) to a unified internal schema without demanding complex ETL from the entities.
- **Tri-State Semantic Logic (Yes / No / Not Available)**: Missing data does *not* mean "No". If evidence of an investigation is missing, SAT-SA treats it as `NOT_AVAILABLE`, leading to an "Insufficient Evidence" rule violation rather than hallucinating a negative outcome.
- **Data Quality & Evaluability Gate**: Before any rules are run, the engine checks data coverage. If critical fields (like `disposition` or `severity`) are malformed, it throws a `DQ` (Data Quality) error rather than a false-positive operational error.
- **Deterministic Rule Engine**: 100% reproducible, explainable, and traceable rules (Execution Gaps, Negative Space, Temporal Drift, Peer Deviations).
- **Blazing Fast React UI**: A custom-built, modern frontend designed specifically for human examiners, featuring a Guided Demo Workflow to effortlessly onboard new judges.
- **100% Offline & Local**: Runs entirely locally via a Python API adapter and a Vite/React frontend. No data leaves the machine.

### PHASE 3 — EVIDENCE INTEGRITY
SAT-SA creates a local cryptographic integrity manifest for assessment evidence using SHA-256.
This allows the system to detect whether source artifacts have changed relative to the evidence state recorded for an assessment. (Note: This is tamper-evident, not an absolute tamper-proof blockchain solution).

---

## 🏗️ Core Architecture

The system is split into two perfectly decoupled layers:

### 1. The Python Analytical Backend
A pure, deterministic Python engine that acts as a pipeline:
`Ingestion → Semantic Normalization → Coverage Check → Rule Execution → Finding Aggregation → JSON Snapshot API`.

- **Engine Data Store:** `engine/data_store.py` manages the massive in-memory graph of Alerts, Cases, and Assets.
- **Rule Modules:** (`execution_gaps.py`, `negative_space.py`, `data_quality.py`) apply strict boolean logic to identify supervisory signals.
- **API Adapter:** `frontend/api.py` exposes exactly three endpoints: `/api/health`, `/api/snapshot`, and `/api/evidence/*`.

### 2. The React Frontend
A modern, zero-dependency (other than React/Vite) single-page application that renders the analytical snapshot into a stunning, interactive workspace for the examiner.
- **Single Page Application:** Built on React 19 and Vite.
- **Vanilla CSS Design System:** A highly optimized `styles.css` utilizing modern CSS variables, Flexbox/Grid, and micro-animations to create a premium, glassmorphic UI.
- **Interactive Drawer System:** Allows examiners to drill down from a high-level entity score straight into the raw JSON evidence of a single alert.

---

## 🛠️ How It Works (The Workflow)

1. **Ingestion & Validation:** The CSE provides an export of their SOC data (e.g., `alerts.csv`, `cases.csv`). SAT-SA ingests this and maps the columns. If `alert_status` is missing, it logs a DQ error.
2. **Dashboard Overview:** The Examiner opens the UI and sees an aggregation of all entities, sorted by an **Attention Score** (calculated based on rule violation severity and coverage).
3. **Evidence & Gap Analysis:** The Examiner selects a specific entity (e.g., `CSE-TELECOM-02`). They review the **Expected vs. Observed** operational chains.
4. **Drill-Down & Traceability:** The Examiner clicks on a finding (e.g., *EG-1: Critical alert without escalation*). A side drawer opens, showing exactly which rule was triggered, the underlying source record ID, and the raw evidence payload.
5. **Review Queue (Adjudication):** The examiner formally reviews the finding and records their qualitative judgement. SAT-SA *prepares* the evidence; the human *decides*.

---

## 🎮 Try the Demo

We have built a **Guided Demo Workflow** directly into the application so judges can understand the core value of SAT-SA in exactly 90 seconds.

1. Launch the application (see instructions below).
2. Click **✦ Try Demo** in the left sidebar.
3. You will be guided through a tiny, controlled scenario involving exactly 4 alerts and 1 organization. 
4. Follow the **Next Step** buttons in the permanent workflow banner to experience exactly how SAT-SA validates data, surfaces execution gaps, and maintains traceability.

---

## 💻 Tech Stack & Requirements

- **Backend:** Python 3.9+ (Standard Library + Pandas for ingestion)
- **Frontend:** Node.js 18+, React 19, TypeScript, Vite
- **No Databases Required:** Uses in-memory processing for rapid local audits.
- **No Cloud Services:** 100% offline.

---

## 🚀 Installation & How to Run

### Step 1: Clone & Setup Backend
```bash
git clone https://github.com/your-org/sat-sa.git
cd sat-sa

# Install Python requirements (pandas)
pip install -r requirements.txt

# Start the Python API Adapter (runs on port 8000)
python frontend/api.py
```

### Step 2: Setup & Run Frontend
Open a **new terminal window** in the same repository:
```bash
cd sat-sa/frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

### Step 3: View the Application
Open your browser and navigate to the URL provided by Vite (usually `http://localhost:5173` or `http://127.0.0.1:5173`). 

---

## 📊 Data Used

SAT-SA includes a robust set of mock operational data for demonstration purposes, located in the `data/` directory:
- **`alerts.csv` (35,000+ records):** Simulates massive heterogeneous exports from various SIEMs (Splunk, QRadar).
- **`cases.csv` (2,000+ records):** Simulates incident management tickets.
- **`assets.csv`:** Critical sector assets categorized by tier.
- **`cse_profiles.csv`:** Metadata for the organizations being audited.

*Note: The **Try Demo** mode utilizes a completely isolated, hardcoded 4-record dataset to ensure the learning experience is untainted by the massive production datasets.*

---

## 📚 Further Documentation

For deep-dive documentation on the exact logical decisions, tri-state semantic normalization, and architecture scaling, please refer to the `SAT_SA_Documentation.pdf` file bundled with this submission (located in the `docs/` directory of the repository).

*Designed with precision for Smart India Hackathon 2026 (Problem Statement 26157).*

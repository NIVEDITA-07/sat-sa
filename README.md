# SAT-SA: Supervisory Analytics Engine

SAT-SA does NOT require CSEs (Critical Sector Entities) to use one universal source format. 

Instead, the architecture utilizes a heterogeneous ingestion pipeline:
1. CSE/SOC submits available security evidence (e.g., SIEM exports, ticketing data).
2. SAT-SA identifies the source format.
3. Evidence is mapped to the canonical SAT-SA internal model.
4. Evidence availability is assessed (Coverage).
5. Only sufficiently supported rules are executed (Rule Availability).
6. Findings are generated deterministically.
7. Findings remain 100% traceable to the raw source evidence (Evidence Lineage).
8. The Examiner makes the final qualitative judgement.

This ensures that SAT-SA can operate across varied infrastructure environments without demanding massive ETL or standardization efforts from the target CSEs.

## How to Run

1. **Install Dependencies:**
   Ensure you have Python installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**
   Launch the Streamlit dashboard:
   ```bash
   python -m streamlit run app.py
   ```

3. **Run the Test Suite:**
   To execute the deterministic rule engine tests and verify data ingestion integrity:
   ```bash
   python -m unittest tests/test_rules.py
   ```

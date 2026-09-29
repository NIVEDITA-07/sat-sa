import re

with open("frontend/src/main.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update validation in demoSnapshot
val_old = """    validation: {},
    validation_status: "N/A"
  };"""

val_new = """    validation: {
      expected_total: 4,
      detected: 4,
      not_detected: 0,
      unexpected_detections: 0
    },
    validation_status: "PASSED"
  };"""

content = content.replace(val_old, val_new)

# 2. Update the Try Demo button in sidebar to start at validation
sidebar_try_old = """onClick={() => {
              setIsDemoMode(true);
              navigate("overview");
            }}"""

sidebar_try_new = """onClick={() => {
              setIsDemoMode(true);
              navigate("validation");
            }}"""

content = content.replace(sidebar_try_old, sidebar_try_new)

# 3. Replace the Demo Banner in main area with the new workflow indicator
main_banner_old = """          {isDemoMode && (
            <div style={{ padding: "12px 24px", background: "rgba(100, 100, 255, 0.05)", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span className="badge" style={{ background: "var(--accent)" }}>CONTROLLED DEMO</span>
                <span style={{ marginLeft: "12px", color: "var(--text-secondary)", fontSize: "0.9rem" }}>A compact controlled scenario for demonstrating SAT-SA's supervisory analysis workflow.</span>
              </div>
              <button onClick={() => { setIsDemoMode(false); navigate("overview"); }} className="secondary-btn" style={{ padding: "4px 12px", background: "transparent", border: "1px solid var(--border)", borderRadius: "4px", color: "var(--text)" }}>Exit Demo</button>
            </div>
          )}"""

main_banner_new = """          {isDemoMode && (
            <div style={{ padding: "16px 24px", background: "rgba(100, 100, 255, 0.05)", borderBottom: "1px solid var(--border)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <span className="badge" style={{ background: "var(--accent)", marginRight: "8px" }}>CONTROLLED DEMO</span>
                  <span style={{ fontWeight: "bold", fontSize: "0.95rem" }}>
                    Workflow: {view === "validation" ? "1. Ingestion & Validation" : view === "overview" ? "2. Dashboard Overview" : view === "entities" ? "3. Evidence & Gap Analysis" : "4. Examiner Review"}
                  </span>
                </div>
                <button onClick={() => { setIsDemoMode(false); navigate("overview"); }} className="secondary-btn" style={{ padding: "4px 12px", fontSize: "0.85rem", background: "transparent", border: "1px solid var(--border)", borderRadius: "4px", color: "var(--text)" }}>Exit Demo</button>
              </div>
              <div style={{ display: "flex", gap: "24px", fontSize: "0.9rem" }}>
                <div style={{ flex: 1 }}>
                  <b style={{ color: "var(--text-secondary)", fontSize: "0.8rem", letterSpacing: "1px" }}>WHAT YOU ARE SEEING</b>
                  <p style={{ margin: "4px 0 0 0", lineHeight: 1.5 }}>
                    {view === "validation" && "SAT-SA receives raw SOC records and verifies data quality before analysis."}
                    {view === "overview" && "A high-level aggregation of all organizations, findings, and attention scores."}
                    {view === "entities" && "A deep dive into a single organization's expected vs. observed operational evidence."}
                    {view === "queue" && "A unified queue where human examiners review and adjudicate the final findings."}
                  </p>
                </div>
                <div style={{ flex: 1 }}>
                  <b style={{ color: "var(--text-secondary)", fontSize: "0.8rem", letterSpacing: "1px" }}>WHY IT MATTERS</b>
                  <p style={{ margin: "4px 0 0 0", lineHeight: 1.5 }}>
                    {view === "validation" && "Bad data produces false positives. SAT-SA traps semantic errors immediately."}
                    {view === "overview" && "Examiners must prioritize their limited time on the most critical supervision targets."}
                    {view === "entities" && "Rules are traceable. Missing operational steps (like a missing investigation) generate clear, undeniable signals."}
                    {view === "queue" && "SAT-SA is an assistant, not an automated judge. It prepares the evidence; the examiner makes the decision."}
                  </p>
                </div>
                <div style={{ flex: "0 0 auto", display: "flex", alignItems: "center" }}>
                  {view === "validation" && <button className="primary-btn" onClick={() => navigate("overview")}>Next: Overview →</button>}
                  {view === "overview" && <button className="primary-btn" onClick={() => { navigate("entities"); setSelectedCse("CSE-DEMO-01"); }}>Next: Assessment →</button>}
                  {view === "entities" && <button className="primary-btn" onClick={() => navigate("queue")}>Next: Review Queue →</button>}
                  {view === "queue" && <button className="primary-btn" onClick={() => { setIsDemoMode(false); navigate("overview"); }}>Finish Demo ✓</button>}
                </div>
              </div>
            </div>
          )}"""

content = content.replace(main_banner_old, main_banner_new)

with open("frontend/src/main.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Injected successfully!")

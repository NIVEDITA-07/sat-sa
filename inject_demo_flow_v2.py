import re

with open("frontend/src/main.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the sidebar Try Demo button to navigate to overview
sidebar_try_old = """          <button 
            className={`nav-item ${isDemoMode ? "active" : ""}`}
            style={{ marginTop: "1rem", color: "var(--accent)", border: isDemoMode ? "1px solid var(--accent)" : "1px dashed var(--border)", background: isDemoMode ? "var(--accent-hover)" : "transparent" }}
            onClick={() => {
              setIsDemoMode(true);
              navigate("validation");
            }}
          >"""

sidebar_try_new = """          <button 
            className={`nav-item ${isDemoMode ? "active" : ""}`}
            style={{ marginTop: "1rem", color: "var(--accent)", border: isDemoMode ? "1px solid var(--accent)" : "1px dashed var(--border)", background: isDemoMode ? "var(--accent-hover)" : "transparent" }}
            onClick={() => {
              setIsDemoMode(true);
              navigate("overview");
            }}
          >"""

content = content.replace(sidebar_try_old, sidebar_try_new)


# 2. Replace the main banner with the newly organized box
main_banner_start = "          {isDemoMode && ("
main_banner_end = "          {!data && !error && ("

# Find the block
start_idx = content.find(main_banner_start)
end_idx = content.find(main_banner_end, start_idx)

if start_idx != -1 and end_idx != -1:
    old_banner = content[start_idx:end_idx]
    new_banner = """          {isDemoMode && (
            <div style={{ margin: "24px", padding: "0", background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: "8px", boxShadow: "0 4px 12px rgba(0,0,0,0.05)", overflow: "hidden" }}>
              <div style={{ background: "var(--bg-secondary)", padding: "16px 24px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                  <span className="badge" style={{ background: "var(--accent)" }}>CONTROLLED DEMO</span>
                  <span style={{ fontWeight: "600", fontSize: "1.05rem" }}>
                    {view === "overview" && "Step 1: Dashboard Overview"}
                    {view === "entities" && "Step 2: Evidence & Gap Analysis"}
                    {view === "queue" && "Step 3: Examiner Review"}
                    {view === "validation" && "Step 4: Ingestion & Validation"}
                  </span>
                </div>
                <button onClick={() => { setIsDemoMode(false); navigate("overview"); }} className="secondary-btn" style={{ padding: "6px 16px", fontSize: "0.85rem", background: "transparent", border: "1px solid var(--border)", borderRadius: "4px", color: "var(--text)", cursor: "pointer" }}>Exit Demo ✕</button>
              </div>
              <div style={{ padding: "24px", display: "flex", gap: "32px" }}>
                <div style={{ flex: 2 }}>
                  <h4 style={{ color: "var(--accent)", fontSize: "0.75rem", letterSpacing: "1.5px", textTransform: "uppercase", margin: "0 0 12px 0" }}>What is happening here?</h4>
                  <ul style={{ margin: 0, paddingLeft: "20px", color: "var(--text)", lineHeight: 1.6, fontSize: "0.95rem" }}>
                    {view === "overview" && (
                      <>
                        <li><b>Aggregation:</b> The system aggregates all organizations, findings, and attention scores into a single pane of glass.</li>
                        <li><b>Prioritization:</b> Examiners use this to prioritize their limited time on the most critical supervision targets.</li>
                        <li><b>Action:</b> Notice that <b>Demo Scenario Organization</b> requires High Attention.</li>
                      </>
                    )}
                    {view === "entities" && (
                      <>
                        <li><b>Drill-down:</b> You are now looking at a single organization's operational evidence.</li>
                        <li><b>Traceability:</b> Rules are strictly traceable. Missing operational steps (like a missing investigation) generate undeniable signals.</li>
                        <li><b>Action:</b> Click the <b>"Missing investigation evidence"</b> finding below to see exactly what triggered it.</li>
                      </>
                    )}
                    {view === "queue" && (
                      <>
                        <li><b>Human-in-the-loop:</b> SAT-SA is an assistant, not an automated judge. It prepares the evidence; the examiner makes the final decision.</li>
                        <li><b>Adjudication:</b> All findings across all entities are centralized here for formal review.</li>
                        <li><b>Action:</b> An examiner would approve or reject the finding here.</li>
                      </>
                    )}
                    {view === "validation" && (
                      <>
                        <li><b>Data Quality First:</b> Bad data produces false positives. SAT-SA traps semantic errors immediately upon ingestion.</li>
                        <li><b>Transparency:</b> The system confirms exactly how many records were successfully mapped to expected schemas.</li>
                        <li><b>Action:</b> You can verify that all 4 demo records were correctly processed.</li>
                      </>
                    )}
                  </ul>
                </div>
                <div style={{ flex: 1, borderLeft: "1px solid var(--border)", paddingLeft: "32px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
                  <div style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "16px", fontWeight: "600", textTransform: "uppercase", letterSpacing: "1px" }}>Next Step</div>
                  {view === "overview" && <button className="primary-btn" style={{ padding: "12px 24px", fontSize: "1rem" }} onClick={() => { navigate("entities"); setSelectedCse("CSE-DEMO-01"); }}>Explore Assessment →</button>}
                  {view === "entities" && <button className="primary-btn" style={{ padding: "12px 24px", fontSize: "1rem" }} onClick={() => navigate("queue")}>View Review Queue →</button>}
                  {view === "queue" && <button className="primary-btn" style={{ padding: "12px 24px", fontSize: "1rem" }} onClick={() => navigate("validation")}>View Validation Log →</button>}
                  {view === "validation" && <button className="primary-btn" style={{ padding: "12px 24px", fontSize: "1rem", background: "var(--success)" }} onClick={() => { setIsDemoMode(false); navigate("overview"); }}>Finish Demo ✓</button>}
                </div>
              </div>
            </div>
          )}
"""
    content = content.replace(old_banner, new_banner)
else:
    print("Could not find the banner block!")


with open("frontend/src/main.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Injected successfully!")

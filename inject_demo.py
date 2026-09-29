import re

with open("frontend/src/main.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove DemoComponent import and view type demo if they exist from last time
content = content.replace('import { DemoComponent } from "./DemoComponent";\n', '')
content = content.replace('type View = "overview" | "entities" | "queue" | "validation" | "demo";', 'type View = "overview" | "entities" | "queue" | "validation";')

# 2. Inject Demo state and data just inside App()
demo_data_block = """
  const [isDemoMode, setIsDemoMode] = useState(false);

  const demoSnapshot: Snapshot = {
    meta: {
      mode: "Controlled Demo Data",
      entity_count: 1,
      alert_count: 4,
      case_count: 0,
      asset_count: 1,
      finding_count: 1,
    },
    entities: [
      {
        cse_id: "CSE-DEMO-01",
        name: "Demo Scenario Organization",
        sector: "Finance",
        assessment_period: "Current submission",
        criticality_tier: "Tier 1",
        attention_score: 1,
        attention_level: "HIGH",
        finding_count: 1,
        kpi_summary: {},
        coverage: {
          "Alerts": "READY",
          "Investigation": "READY",
          "Escalation": "READY",
          "Remediation": "READY",
        },
        warnings: [],
        reported: {},
        observed: {
          sample_count: 4,
          escalation_rate: 0.5,
          investigation_rate: 0.75,
        }
      }
    ],
    findings: [
      {
        finding_id: "DEMO-EG2-01",
        cse_id: "CSE-DEMO-01",
        rule_id: "EG-2",
        category: "execution_gap",
        severity: "HIGH",
        title: "Missing investigation evidence",
        explanation: "Critical alert was closed, but the available operational evidence does not show investigation or escalation.",
        evidence_ids: ["A-002"],
        metric_value: null,
        peer_value: null,
        related_asset_type: null
      }
    ],
    sector_signals: [],
    validation: {},
    validation_status: "N/A"
  };

  const mockDemoEvidence = (id: string): Evidence => {
    if (id === "A-002") {
      return {
        kind: "alert",
        id: "A-002",
        record: {
          alert_id: "A-002",
          severity: "Critical",
          disposition: "Closed",
          investigation_present: "No",
          escalated: "No",
          remediation_present: "Open"
        },
        related: {}
      };
    }
    return { kind: "alert", id, record: {}, related: {} };
  };

  const displayData = isDemoMode ? demoSnapshot : data;
"""

# Replace all occurrences of `data` (where it refers to the state) with `displayData` inside the component
content = content.replace("const [data, setData] = useState<Snapshot | null>(null);", 
"""const [realData, setData] = useState<Snapshot | null>(null);
""" + demo_data_block + """
  const data = isDemoMode ? demoSnapshot : realData;
""")

# 3. Update openEvidence
open_ev_replace = """  async function openEvidence(id: string) {
    if (isDemoMode) {
      setEvidence(mockDemoEvidence(id));
      return;
    }
    const kind = kindFor(id);"""

content = content.replace("""  async function openEvidence(id: string) {
    const kind = kindFor(id);""", open_ev_replace)

# 4. Update the sidebar
sidebar_old = """        <nav aria-label="Main navigation">
          {(
            [
              ["overview", "Overview", "◫"],
              ["entities", "CSE assessments", "▤"],
              ["queue", "Review queue", "≡"],
              ["validation", "Data & validation", "◇"],
            ] as const
          ).map(([id, label, icon]) => (
            <button
              key={id}
              className={`nav-item ${view === id ? "active" : ""}`}
              onClick={() => navigate(id)}
            >
              <span className="nav-icon">{icon}</span>
              {label}
              {id === "queue" && data && (
                <span className="nav-count">{data.meta.finding_count}</span>
              )}
            </button>
          ))}
        </nav>"""

sidebar_new = """        <nav aria-label="Main navigation">
          {(
            [
              ["overview", "Overview", "◫"],
              ["entities", "CSE assessments", "▤"],
              ["queue", "Review queue", "≡"],
              ["validation", "Data & validation", "◇"],
            ] as const
          ).map(([id, label, icon]) => (
            <button
              key={id}
              className={`nav-item ${view === id && !isDemoMode ? "active" : ""}`}
              onClick={() => {
                setIsDemoMode(false);
                navigate(id);
              }}
            >
              <span className="nav-icon">{icon}</span>
              {label}
              {id === "queue" && data && (
                <span className="nav-count">{data.meta.finding_count}</span>
              )}
            </button>
          ))}
          <button 
            className={`nav-item ${isDemoMode ? "active" : ""}`}
            style={{ marginTop: "1rem", color: "var(--accent)", border: isDemoMode ? "1px solid var(--accent)" : "1px dashed var(--border)", background: isDemoMode ? "var(--accent-hover)" : "transparent" }}
            onClick={() => {
              setIsDemoMode(true);
              navigate("overview");
            }}
          >
            <span className="nav-icon">✦</span>
            Try Demo
          </button>
        </nav>"""

content = content.replace(sidebar_old, sidebar_new)

# 5. Add Demo Banner to main area
main_old = """        <main>
          {!data && !error && ("""

main_new = """        <main>
          {isDemoMode && (
            <div style={{ padding: "12px 24px", background: "rgba(100, 100, 255, 0.05)", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span className="badge" style={{ background: "var(--accent)" }}>CONTROLLED DEMO</span>
                <span style={{ marginLeft: "12px", color: "var(--text-secondary)", fontSize: "0.9rem" }}>A compact controlled scenario for demonstrating SAT-SA's supervisory analysis workflow.</span>
              </div>
              <button onClick={() => { setIsDemoMode(false); navigate("overview"); }} className="secondary-btn" style={{ padding: "4px 12px", background: "transparent", border: "1px solid var(--border)", borderRadius: "4px", color: "var(--text)" }}>Exit Demo</button>
            </div>
          )}
          {!data && !error && ("""

content = content.replace(main_old, main_new)


# 6. Add "Expected vs Observed" to CSE Assessment page (Entities view)
entities_old = """              {view === "entities" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">
                        {data.entities.length} ASSESSMENTS
                      </div>
                      <h1>CSE assessments</h1>
                      <p>
                        Select an entity to review its rules, coverage, and
                        signals.
                      </p>
                    </div>
                  </div>
                  <div className="layout-row">"""

entities_new = entities_old + """
                    {isDemoMode && selectedCse === "CSE-DEMO-01" && (
                      <div className="card" style={{ marginBottom: "2rem", gridColumn: "1 / -1" }}>
                        <h3>Expected vs Observed Evidence</h3>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", marginTop: "1rem" }}>
                          <div>
                            <h4 style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.5rem" }}>EXPECTED</h4>
                            <ul style={{ listStyle: "none", padding: 0, margin: 0, lineHeight: 1.8 }}>
                              <li>Critical Alert</li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Investigation</li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Escalation</li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Remediation</li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Closure</li>
                            </ul>
                          </div>
                          <div>
                            <h4 style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.5rem" }}>OBSERVED (A-002)</h4>
                            <ul style={{ listStyle: "none", padding: 0, margin: 0, lineHeight: 1.8 }}>
                              <li>Critical Alert <span style={{ color: "var(--success)", float: "right" }}>✓</span></li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Investigation — <span style={{ color: "var(--error)", float: "right" }}>Not observed</span></li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Escalation — <span style={{ color: "var(--error)", float: "right" }}>Not observed</span></li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Remediation — <span style={{ color: "var(--warning)", float: "right" }}>Open</span></li>
                              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
                              <li>Closure <span style={{ color: "var(--success)", float: "right" }}>✓</span></li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}"""

content = content.replace(entities_old, entities_new)


# 7. Remove the old Try Demo card that we injected into overview
old_demo_card = """                  <div style={{ padding: "16px", borderRadius: "8px", background: "var(--bg-card)", borderLeft: "4px solid var(--accent)", display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
                    <div>
                      <h3 style={{ margin: "0 0 4px 0", fontSize: "1rem" }}>TRY DEMO</h3>
                      <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "0.95rem" }}>See SAT-SA analyze a controlled SOC scenario.</p>
                    </div>
                    <button className="primary-btn" onClick={() => navigate("demo")}>Try the Demo →</button>
                  </div>"""

content = content.replace(old_demo_card, "")


# 8. Also remove the <DemoComponent ... /> from view === "demo"
demo_comp_block = """              {view === "demo" && (
                <DemoComponent onExit={() => navigate("overview")} />
              )}"""
content = content.replace(demo_comp_block, "")


with open("frontend/src/main.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Injected successfully!")

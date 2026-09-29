import React, { useState } from "react";

function Badge({ level }: { level: string }) {
  return (
    <span className={`badge ${level.toLowerCase().replaceAll(" ", "-")}`}>
      {level}
    </span>
  );
}

export function DemoComponent({ onExit }: { onExit: () => void }) {
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [selectedRecord, setSelectedRecord] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  const demoRecords = [
    { id: "A-001", sev: "Critical", status: "Closed", inv: "Yes", esc: "Yes", rem: "Completed" },
    { id: "A-002", sev: "Critical", status: "Closed", inv: "No", esc: "No", rem: "Open" },
    { id: "A-003", sev: "High", status: "Closed", inv: "Yes", esc: "No", rem: "Open" },
    { id: "A-004", sev: "Medium", status: "Closed", inv: "Yes", esc: "Yes", rem: "Completed" },
  ];

  if (step === 0) {
    return (
      <div className="demo-view intro-screen" style={{ maxWidth: "600px", margin: "40px auto", textAlign: "center" }}>
        <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>SAT-SA — Controlled Demonstration</h1>
        <h2 style={{ fontSize: "1.2rem", fontWeight: "normal", color: "var(--text-secondary)", marginBottom: "2rem" }}>From SOC evidence to a traceable supervisory signal.</h2>
        <p style={{ marginBottom: "2rem" }}>
          Select a sample CSE and see how SAT-SA moves from operational evidence to an examiner-reviewable finding.
        </p>
        <button className="primary-button" style={{ fontSize: "1.1rem", padding: "12px 24px" }} onClick={() => setStep(1)}>
          Start Demo →
        </button>
      </div>
    );
  }

  return (
    <div className="demo-view" style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
      <div style={{ marginBottom: "1.5rem" }}>
        <span className="badge" style={{ background: "rgba(255, 255, 255, 0.1)" }}>CONTROLLED DEMONSTRATION</span>
        <p style={{ color: "var(--text-secondary)", marginTop: "0.5rem", fontSize: "0.9rem" }}>
          This demonstration uses a deliberately small controlled dataset to make SAT-SA's analytical workflow immediately understandable.
        </p>
      </div>

      <div className="card" style={{ marginBottom: "2rem" }}>
        <h2>Sample SOC Evidence</h2>
        <p className="card-meta">CSE-DEMO-01 · Controlled assessment scenario</p>
        <div className="table-wrapper" style={{ marginTop: "1rem" }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Investigation</th>
                <th>Escalation</th>
                <th>Remediation</th>
              </tr>
            </thead>
            <tbody>
              {demoRecords.map((r) => {
                const isViolator = r.id === "A-002";
                const isSelected = selectedRecord === r.id;
                return (
                  <tr 
                    key={r.id} 
                    className={isSelected ? "selected-row" : ""} 
                    style={isViolator ? { background: isSelected ? "var(--accent-hover)" : "rgba(255,100,100,0.1)", cursor: "pointer" } : { opacity: 0.7 }}
                    onClick={() => { if (isViolator) setSelectedRecord(r.id); }}
                  >
                    <td><b>{r.id}</b></td>
                    <td><Badge level={r.sev} /></td>
                    <td>{r.status}</td>
                    <td>{r.inv}</td>
                    <td>{r.esc}</td>
                    <td>{r.rem}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {selectedRecord && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem", marginBottom: "2rem" }}>
          <div className="card">
            <h3 style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>EXPECTED OPERATIONAL CHAIN</h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, lineHeight: 2 }}>
              <li>Alert</li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Investigation</li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Escalation when required</li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Remediation</li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Closure</li>
            </ul>
          </div>
          <div className="card">
            <h3 style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>OBSERVED EVIDENCE</h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, lineHeight: 2 }}>
              <li>Alert <span style={{ color: "var(--success)" }}>✓</span></li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Investigation <span style={{ color: "var(--error)" }}>✕</span></li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Escalation <span style={{ color: "var(--error)" }}>✕</span></li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Remediation <span style={{ color: "var(--warning)" }}>⚠</span></li>
              <li style={{ color: "var(--text-secondary)", marginLeft: "0.5rem" }}>↓</li>
              <li>Closure <span style={{ color: "var(--success)" }}>✓</span></li>
            </ul>
          </div>
        </div>
      )}

      {selectedRecord && (
        <div className="card" style={{ border: "1px solid var(--error)", marginBottom: "2rem" }}>
          <h2 style={{ color: "var(--error)" }}>POTENTIAL EXECUTION GAP</h2>
          <p style={{ margin: "1rem 0", fontSize: "1.1rem" }}>
            Critical alert was closed, but the available operational evidence does not show investigation or escalation.
          </p>
          <p style={{ color: "var(--text-secondary)" }}>Requires examiner review.</p>
          
          <div style={{ marginTop: "1.5rem", borderTop: "1px solid var(--border)", paddingTop: "1rem" }}>
            <button 
              className="entity-link" 
              style={{ fontWeight: "bold" }} 
              onClick={() => setExpanded(!expanded)}
            >
              Why was this flagged? {expanded ? "▴" : "▾"}
            </button>
            
            {expanded && (
              <div style={{ marginTop: "1rem", background: "var(--bg-secondary)", padding: "1rem", borderRadius: "6px" }}>
                <div className="kv" style={{ marginBottom: "0.5rem" }}>
                  <span>Rule</span><b>EG-2 — Missing Investigation</b>
                </div>
                <div className="kv" style={{ marginBottom: "0.5rem" }}>
                  <span>Source Record</span><b>{selectedRecord}</b>
                </div>
                <div className="kv" style={{ marginBottom: "0.5rem" }}>
                  <span>Observed</span><b>investigation_present = No</b>
                </div>
                <div className="kv" style={{ marginBottom: "0.5rem" }}>
                  <span>Severity</span><b>Critical</b>
                </div>
                <div className="kv" style={{ marginBottom: "0.5rem" }}>
                  <span>Result</span><b>Potential execution gap requiring examiner review.</b>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {selectedRecord && (
        <div style={{ borderTop: "1px solid var(--border)", paddingTop: "2rem", paddingBottom: "4rem", textAlign: "center" }}>
          <h3 style={{ fontSize: "0.9rem", color: "var(--text-secondary)", letterSpacing: "1px", marginBottom: "1rem" }}>WHAT SAT-SA DID</h3>
          <p style={{ color: "var(--text-secondary)", lineHeight: 1.8, marginBottom: "2rem" }}>
            Evidence<br/>↓<br/>Expected vs Observed<br/>↓<br/>Evidence Gap<br/>↓<br/>Traceable Finding<br/>↓<br/>Examiner Review
          </p>
          <p style={{ fontSize: "1.1rem", marginBottom: "2rem" }}>
            SAT-SA supports supervisory assessment.<br/>
            It does not replace examiner judgement.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <button className="primary-button" onClick={onExit}>Explore Full SAT-SA →</button>
            <button className="secondary-button" onClick={onExit}>Back to Dashboard</button>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Level = "HIGH" | "MEDIUM" | "LOW";
type EvidenceLineage = {
  source_name: string;
  source_type: string;
  source_record_id: string;
  normalized_record_id: string;
  record_type: string;
  relevant_fields: Record<string, any>;
};

type FindingProvenance = {
  rule_version: string;
  assessment_id: string;
  analysis_timestamp: string;
  configuration_version: string;
  evidence_lineage: EvidenceLineage[];
  aggregate_context: Record<string, any>;
};

type Finding = {
  finding_id: string;
  cse_id: string;
  rule_id: string;
  category: string;
  severity: Level;
  title: string;
  explanation: string;
  evidence_ids: string[];
  metric_value: number | null;
  peer_value: number | null;
  related_asset_type: string | null;
  provenance?: FindingProvenance;
};
type Entity = {
  cse_id: string;
  name: string;
  sector: string;
  assessment_period: string;
  criticality_tier: string;
  attention_score: number;
  attention_level: Level;
  finding_count: number;
  kpi_summary: Record<string, string>;
  coverage: Record<string, string>;
  warnings: string[];
  reported: Record<string, number | null>;
  observed: {
    sample_count: number;
    escalation_rate: number | null;
    investigation_rate: number | null;
  };
};
type Snapshot = {
  meta: {
    mode: string;
    entity_count: number;
    alert_count: number;
    case_count: number;
    asset_count: number;
    finding_count: number;
  };
  entities: Entity[];
  findings: Finding[];
  sector_signals: {
    rule_id: string;
    affected_count: number;
    proportion: number;
    description: string;
  }[];
  validation: {
    expected_total?: number;
    detected?: number;
    not_detected?: number;
    unexpected_detections?: number;
  };
  validation_status?: string;
  integrity?: {
    assessment_id: string;
    overall_status: string;
    verified_at: string;
    artifacts_checked: number;
    unchanged_count: number;
    changed_count: number;
    missing_count: number;
    unavailable_count: number;
    artifact_results: {
      source_name: string;
      expected_hash: string;
      current_hash: string | null;
      status: string;
      reason: string | null;
    }[];
  };
};
type Evidence = {
  kind: string;
  id: string;
  record: Record<string, unknown>;
  related: { cases?: string[]; asset?: string; alert?: string };
};
type View = "overview" | "entities" | "queue" | "validation";
const ruleNames: Record<string, string> = {
  "EG-1": "Critical alert without escalation",
  "EG-2": "Missing investigation evidence",
  "EG-3": "Unusually fast closure",
  "EG-4": "Repeated alerts without remediation",
  "NS-1": "Monitoring blind spot",
  "PEER-1": "Peer deviation",
  "T-1": "Temporal drift",
  "K-1": "KPI contradiction",
  "I-1": "Investigation note reuse",
  "DQ-1": "Data quality",
  "DQ-2": "Data quality",
  "DQ-3": "Data quality",
};
const count = (n: number | undefined) => (n ?? 0).toLocaleString("en-IN");
const percentage = (n: number | null | undefined) =>
  n == null ? "Not available" : `${Math.round(n * 100)}%`;
const titleCase = (text: string) =>
  text.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
function kindFor(id: string): "alert" | "case" | "asset" | null {
  if (id.startsWith("ALT-")) return "alert";
  if (id.startsWith("CAS-")) return "case";
  if (id.startsWith("AST-")) return "asset";
  return null;
}
function Badge({ level }: { level: string }) {
  return (
    <span className={`badge ${level.toLowerCase().replaceAll(" ", "-")}`}>
      {level}
    </span>
  );
}

function App() {
  const [realData, setData] = useState<Snapshot | null>(null);

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
    validation: {
      expected_total: 4,
      detected: 4,
      not_detected: 0,
      unexpected_detections: 0
    },
    validation_status: "PASSED"
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

  const data = isDemoMode ? demoSnapshot : realData;

  const [error, setError] = useState("");
  const [view, setView] = useState<View>("overview");
  const [selectedCse, setSelectedCse] = useState<string | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [evidenceLimit, setEvidenceLimit] = useState(30);
  const [evidence, setEvidence] = useState<Evidence | null>(null);
  const [evidenceError, setEvidenceError] = useState("");
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("ALL");
  const [rule, setRule] = useState("ALL");
  const [sector, setSector] = useState("ALL");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const API_BASE = (import.meta as any).env.VITE_API_URL || "";

  useEffect(() => {
    fetch(`${API_BASE}/api/snapshot`)
      .then(async (response) => {
        if (!response.ok)
          throw new Error("The analytics service is unavailable.");
        return response.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);
  useEffect(() => {
    setPage(1);
  }, [search, level, rule, sector, view, selectedCse]);

  async function openEvidence(id: string) {
    if (isDemoMode) {
      setEvidence(mockDemoEvidence(id));
      return;
    }
    const kind = kindFor(id);
    if (!kind) return;
    setEvidence(null);
    setEvidenceError("");
    setEvidenceLoading(true);
    try {
      const response = await fetch(
        `${API_BASE}/api/evidence/${kind}/${encodeURIComponent(id)}`,
      );
      if (!response.ok)
        throw new Error(
          "This source record is not available in the current submission.",
        );
      setEvidence(await response.json());
    } catch (e) {
      setEvidenceError((e as Error).message);
    } finally {
      setEvidenceLoading(false);
    }
  }
  function navigate(next: View) {
    setView(next);
    setSelectedCse(null);
    setSelectedFinding(null);
    setEvidence(null);
  }
  function showEntity(id: string) {
    setView("entities");
    setSelectedCse(id);
    setSelectedFinding(null);
    setEvidence(null);
  }
  function showFinding(finding: Finding) {
    setSelectedFinding(finding);
    setEvidenceLimit(30);
    setEvidence(null);
  }
  function queueFor(ruleId?: string, cseId?: string) {
    setRule(ruleId || "ALL");
    setSelectedCse(cseId || null);
    setView("queue");
    setSelectedFinding(null);
    setEvidence(null);
  }

  const sectors = useMemo(
    () => [...new Set(data?.entities.map((e) => e.sector) ?? [])].sort(),
    [data],
  );
  const filteredEntities = useMemo(
    () =>
      (data?.entities ?? []).filter(
        (e) =>
          (sector === "ALL" || e.sector === sector) &&
          (level === "ALL" || e.attention_level === level) &&
          `${e.cse_id} ${e.name} ${e.sector}`
            .toLowerCase()
            .includes(search.toLowerCase()),
      ),
    [data, sector, level, search],
  );
  const filteredFindings = useMemo(
    () =>
      (data?.findings ?? []).filter(
        (f) =>
          (!selectedCse || f.cse_id === selectedCse) &&
          (rule === "ALL" || f.rule_id === rule) &&
          (level === "ALL" || f.severity === level) &&
          `${f.cse_id} ${f.title} ${f.rule_id} ${f.evidence_ids.join(" ")}`
            .toLowerCase()
            .includes(search.toLowerCase()),
      ),
    [data, selectedCse, rule, level, search],
  );
  const selectedEntity = data?.entities.find((e) => e.cse_id === selectedCse);
  const totalPages = Math.max(
    1,
    Math.ceil(
      (view === "queue" ? filteredFindings.length : filteredEntities.length) /
        pageSize,
    ),
  );
  const pageControls = (
    <div className="pagination">
      <span>
        Page {page} of {totalPages}
      </span>
      <button disabled={page === 1} onClick={() => setPage(page - 1)}>
        Previous
      </button>
      <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
        Next
      </button>
    </div>
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            S<span>·</span>
          </div>
          <div>
            <strong>SAT-SA</strong>
            <small>Supervisory analytics</small>
          </div>
        </div>
        <div className="side-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
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
        </nav>
        <div className="sidebar-bottom">
          <div className="environment">
            <span className="live-dot" /> LOCAL ANALYSIS
          </div>
          <p>
            Evidence from a periodic submission. Examiner review required for
            every finding.
          </p>
        </div>
      </aside>
      <div className="main-wrap">
        <header className="topbar">
          <div className="breadcrumb">
            SAT-SA <span>/</span>{" "}
            {view === "overview"
              ? "Overview"
              : view === "entities"
                ? "CSE assessments"
                : view === "queue"
                  ? "Review queue"
                  : "Data & validation"}
          </div>
          <div className="top-meta">
            <span className="period">
              {data?.entities[0]?.assessment_period || "Assessment period"}
            </span>
            <span className="workspace-label">Examiner workspace</span>
          </div>
        </header>
        <main>
          {isDemoMode && (
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
          {!data && !error && (
            <div className="loading">
              <div className="spinner" />
              <h2>Preparing the assessment</h2>
              <p>
                The local rules are evaluating submitted evidence. The first
                load can take a moment.
              </p>
            </div>
          )}
          {error && (
            <div className="error-state">
              <h2>Unable to load assessment</h2>
              <p>{error}</p>
              <p>
                Start the local adapter with <code>python frontend/api.py</code>{" "}
                from the repository root, then refresh this page.
              </p>
              <button onClick={() => location.reload()}>Retry</button>
            </div>
          )}
          {data && (
            <>
              {view === "overview" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">SUPERVISORY WORKSPACE</div>
                      <h1>Assessment overview</h1>
                      <p>
                        Start with the entities that need examination, then
                        trace each signal to its submitted evidence.
                      </p>
                    </div>
                    <button className="primary-btn" onClick={() => queueFor()}>
                      Open review queue <span>→</span>
                    </button>
                  </div>
                  <div className="scope-strip">
                    <span>
                      <b>Submission</b> {data.meta.mode}
                    </span>
                    <span>
                      <b>Period</b>{" "}
                      {data.entities[0]?.assessment_period || "Not available"}
                    </span>
                    <span>
                      <b>Method</b> Deterministic rules
                    </span>
                    <span>
                      <b>Decision</b> Human examiner
                    </span>
                  </div>



                  <div className="metric-grid">
                    <div className="metric-card">
                      <span>Entities assessed</span>
                      <strong>{count(data.meta.entity_count)}</strong>
                      <small>Across {sectors.length} sectors</small>
                    </div>
                    <div className="metric-card metric-alert">
                      <span>High attention</span>
                      <strong>
                        {count(
                          data.entities.filter(
                            (e) => e.attention_level === "HIGH",
                          ).length,
                        )}
                      </strong>
                      <small>Prioritise for manual review</small>
                    </div>
                    <div className="metric-card">
                      <span>Rule findings</span>
                      <strong>{count(data.meta.finding_count)}</strong>
                      <small>Traceable to evidence records</small>
                    </div>
                    <div className="metric-card">
                      <span>Evidence analysed</span>
                      <strong>{count(data.meta.alert_count)}</strong>
                      <small>
                        Alerts · {count(data.meta.case_count)} cases
                      </small>
                    </div>
                  </div>
                  <div className="overview-grid">
                    <section className="panel">
                      <div className="section-head">
                        <div>
                          <h2>Entities needing attention</h2>
                          <p>Ranked by the engine’s attention score</p>
                        </div>
                        <button
                          className="text-btn"
                          onClick={() => navigate("entities")}
                        >
                          View all →
                        </button>
                      </div>
                      <div className="table-scroll">
                        <table>
                          <thead>
                            <tr>
                              <th>ENTITY</th>
                              <th>SECTOR</th>
                              <th>FINDINGS</th>
                              <th>ATTENTION</th>
                              <th>SCORE</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.entities.slice(0, 7).map((e) => (
                              <tr
                                key={e.cse_id}
                                role="button"
                                tabIndex={0}
                                onClick={() => showEntity(e.cse_id)}
                                onKeyDown={(event) => {
                                  if (
                                    event.key === "Enter" ||
                                    event.key === " "
                                  ) {
                                    event.preventDefault();
                                    showEntity(e.cse_id);
                                  }
                                }}
                              >
                                <td>
                                  <strong>{e.cse_id}</strong>
                                  <small>{e.name}</small>
                                </td>
                                <td>{e.sector}</td>
                                <td>{e.finding_count}</td>
                                <td>
                                  <Badge level={e.attention_level} />
                                </td>
                                <td className="score">
                                  {e.attention_score}
                                  <span> →</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </section>
                    <div className="stack">
                      <section className="panel signal-panel">
                        <div className="section-head">
                          <div>
                            <h2>Across the submission</h2>
                            <p>Patterns present in multiple CSEs</p>
                          </div>
                        </div>
                        {data.sector_signals.length ? (
                          data.sector_signals.slice(0, 4).map((s) => (
                            <button
                              className="signal-row"
                              key={s.rule_id}
                              onClick={() => queueFor(s.rule_id)}
                            >
                              <div className="signal-code">{s.rule_id}</div>
                              <div>
                                <strong>
                                  {ruleNames[s.rule_id] || s.rule_id}
                                </strong>
                                <span>
                                  {s.affected_count} of {data.meta.entity_count}{" "}
                                  entities · {Math.round(s.proportion * 100)}%
                                </span>
                              </div>
                              <span className="arrow">↗</span>
                            </button>
                          ))
                        ) : (
                          <p className="muted-pad">
                            No rule reached the sector-wide threshold.
                          </p>
                        )}
                      </section>
                      <section className="panel method-panel">
                        <div className="section-head">
                          <div>
                            <h2>How to use this assessment</h2>
                            <p>A finding is a prompt for examination</p>
                          </div>
                        </div>
                        <ol>
                          <li>
                            <b>Prioritise</b> an entity or finding.
                          </li>
                          <li>
                            <b>Inspect</b> the source alert, case, or asset.
                          </li>
                          <li>
                            <b>Apply judgement</b> using the full submission and
                            context.
                          </li>
                        </ol>
                      </section>
                    </div>
                  </div>
                  <section className="panel recent-panel">
                    <div className="section-head">
                      <div>
                        <h2>First in the review queue</h2>
                        <p>High severity signals are shown first</p>
                      </div>
                      <button className="text-btn" onClick={() => queueFor()}>
                        Review all →
                      </button>
                    </div>
                    <div className="finding-cards">
                      {data.findings.slice(0, 3).map((f) => (
                        <button
                          className="finding-card"
                          key={f.finding_id}
                          onClick={() => {
                            queueFor(undefined, f.cse_id);
                            showFinding(f);
                          }}
                        >
                          <div>
                            <span className="rule-chip">{f.rule_id}</span>
                            <Badge level={f.severity} />
                          </div>
                          <strong>{f.title}</strong>
                          <small>
                            {f.cse_id} · {count(f.evidence_ids.length)} evidence
                            references
                          </small>
                          <span className="card-link">Inspect finding →</span>
                        </button>
                      ))}
                    </div>
                  </section>
                </>
              )}

              {view === "entities" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">ENTITY ASSESSMENT</div>
                      <h1>
                        {selectedEntity
                          ? selectedEntity.cse_id
                          : "CSE assessments"}
                      </h1>
                      <p>
                        {selectedEntity
                          ? `${selectedEntity.sector} · ${selectedEntity.assessment_period} · ${selectedEntity.criticality_tier}`
                          : "Compare attention levels and open an entity’s evidence-backed findings."}
                      </p>
                    </div>
                    {selectedEntity && (
                      <button
                        className="secondary-btn"
                        onClick={() => setSelectedCse(null)}
                      >
                        ← All entities
                      </button>
                    )}
                  </div>
                  {selectedEntity ? (
                    <>
                      <div className="entity-summary">
                        <div>
                          <span>Attention score</span>
                          <strong>{selectedEntity.attention_score}</strong>
                          <Badge level={selectedEntity.attention_level} />
                        </div>
                        <div>
                          <span>Findings</span>
                          <strong>{selectedEntity.finding_count}</strong>
                          <small>Across available rules</small>
                        </div>
                        <div>
                          <span>Sector</span>
                          <strong className="word-value">
                            {selectedEntity.sector}
                          </strong>
                          <small>{selectedEntity.criticality_tier}</small>
                        </div>
                        <div>
                          <span>Assessment period</span>
                          <strong className="word-value">
                            {selectedEntity.assessment_period}
                          </strong>
                          <small>Periodic submission</small>
                        </div>
                      </div>
                      <div className="detail-grid">
                        <section className="panel">
                          <div className="section-head">
                            <div>
                              <h2>Findings for this entity</h2>
                              <p>
                                Select a finding to inspect the rationale and
                                evidence
                              </p>
                            </div>
                            <button
                              className="text-btn"
                              onClick={() =>
                                queueFor(undefined, selectedEntity.cse_id)
                              }
                            >
                              Full queue →
                            </button>
                          </div>
                          {data.findings
                            .filter((f) => f.cse_id === selectedEntity.cse_id)
                            .slice(0, 15)
                            .map((f) => (
                              <button
                                className="entity-finding"
                                key={f.finding_id}
                                onClick={() => showFinding(f)}
                              >
                                <span className="rule-chip">{f.rule_id}</span>
                                <div>
                                  <strong>{f.title}</strong>
                                  <small>{f.explanation}</small>
                                </div>
                                <Badge level={f.severity} />
                                <span>→</span>
                              </button>
                            ))}
                          {selectedEntity.finding_count > 15 && (
                            <p className="more-note">
                              Showing 15 of {selectedEntity.finding_count}{" "}
                              findings. Open the full queue to review all.
                            </p>
                          )}
                        </section>
                        <div className="stack">
                          <section className="panel">
                            <div className="section-head">
                              <div>
                                <h2>Evidence availability</h2>
                                <p>Coverage affects which rules can run</p>
                              </div>
                            </div>
                            <div className="coverage-list">
                              {Object.entries(selectedEntity.coverage).map(
                                ([key, value]) => (
                                  <div key={key}>
                                    <span>{key}</span>
                                    <Badge level={value} />
                                  </div>
                                ),
                              )}
                            </div>
                            {selectedEntity.warnings.length > 0 && (
                              <div className="warnings">
                                {selectedEntity.warnings.map((w) => (
                                  <p key={w}>{w}</p>
                                ))}
                              </div>
                            )}
                          </section>
                          <section className="panel">
                            <div className="section-head">
                              <div>
                                <h2>Reported vs observed</h2>
                                <p>
                                  Closed High/Critical alerts ·{" "}
                                  {count(selectedEntity.observed.sample_count)}{" "}
                                  records
                                </p>
                              </div>
                            </div>
                            <div className="comparison-head">
                              <span>MEASURE</span>
                              <span>REPORTED</span>
                              <span>OBSERVED</span>
                            </div>
                            <div className="comparison-row">
                              <span>Escalation</span>
                              <b>
                                {percentage(
                                  selectedEntity.reported
                                    .reported_escalation_rate,
                                )}
                              </b>
                              <strong>
                                {percentage(
                                  selectedEntity.observed.escalation_rate,
                                )}
                              </strong>
                            </div>
                            <div className="comparison-row">
                              <span>Investigation</span>
                              <b>
                                {percentage(
                                  selectedEntity.reported
                                    .reported_investigation_rate,
                                )}
                              </b>
                              <strong>
                                {percentage(
                                  selectedEntity.observed.investigation_rate,
                                )}
                              </strong>
                            </div>
                            <p className="fine-print">
                              Observed rates follow the existing K-1 rule
                              definition. Compare any discrepancy with the
                              underlying alerts before drawing a conclusion.
                            </p>
                          </section>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="filter-bar">
                        <label>
                          <span>Search entities</span>
                          <input
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Entity ID, name or sector"
                          />
                        </label>
                        <label>
                          <span>Sector</span>
                          <select
                            value={sector}
                            onChange={(e) => setSector(e.target.value)}
                          >
                            <option value="ALL">All sectors</option>
                            {sectors.map((s) => (
                              <option key={s}>{s}</option>
                            ))}
                          </select>
                        </label>
                        <label>
                          <span>Attention</span>
                          <select
                            value={level}
                            onChange={(e) => setLevel(e.target.value)}
                          >
                            <option value="ALL">All levels</option>
                            <option>HIGH</option>
                            <option>MEDIUM</option>
                            <option>LOW</option>
                          </select>
                        </label>
                      </div>
                      <section className="panel list-panel">
                        <div className="section-head">
                          <div>
                            <h2>Entity register</h2>
                            <p>
                              {filteredEntities.length} of{" "}
                              {data.entities.length} entities shown
                            </p>
                          </div>
                        </div>
                        <div className="table-scroll">
                          <table>
                            <thead>
                              <tr>
                                <th>ENTITY</th>
                                <th>SECTOR</th>
                                <th>PERIOD</th>
                                <th>FINDINGS</th>
                                <th>ATTENTION</th>
                                <th>SCORE</th>
                              </tr>
                            </thead>
                            <tbody>
                              {filteredEntities
                                .slice((page - 1) * pageSize, page * pageSize)
                                .map((e) => (
                                  <tr
                                    key={e.cse_id}
                                    role="button"
                                    tabIndex={0}
                                    onClick={() => showEntity(e.cse_id)}
                                    onKeyDown={(event) => {
                                      if (
                                        event.key === "Enter" ||
                                        event.key === " "
                                      ) {
                                        event.preventDefault();
                                        showEntity(e.cse_id);
                                      }
                                    }}
                                  >
                                    <td>
                                      <strong>{e.cse_id}</strong>
                                      <small>{e.name}</small>
                                    </td>
                                    <td>{e.sector}</td>
                                    <td>{e.assessment_period}</td>
                                    <td>{e.finding_count}</td>
                                    <td>
                                      <Badge level={e.attention_level} />
                                    </td>
                                    <td className="score">
                                      {e.attention_score}
                                      <span> →</span>
                                    </td>
                                  </tr>
                                ))}
                            </tbody>
                          </table>
                        </div>
                        {filteredEntities.length === 0 && (
                          <div className="empty">
                            No entities match these filters.
                          </div>
                        )}
                        {pageControls}
                      </section>
                    </>
                  )}
                </>
              )}
              {view === "queue" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">MANUAL REVIEW</div>
                      <h1>Review queue</h1>
                      <p>
                        Rule findings ranked for examiner inspection. Severity
                        is a triage aid, not a final judgement.
                      </p>
                    </div>
                    <span className="header-counter">
                      {filteredFindings.length} findings shown
                    </span>
                  </div>
                  <div className="filter-bar">
                    <label>
                      <span>Search findings or evidence IDs</span>
                      <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search CSE, rule, alert ID…"
                      />
                    </label>
                    <label>
                      <span>Entity</span>
                      <select
                        value={selectedCse || "ALL"}
                        onChange={(e) =>
                          setSelectedCse(
                            e.target.value === "ALL" ? null : e.target.value,
                          )
                        }
                      >
                        <option value="ALL">All entities</option>
                        {data.entities.map((e) => (
                          <option key={e.cse_id}>{e.cse_id}</option>
                        ))}
                      </select>
                    </label>
                    <label>
                      <span>Severity</span>
                      <select
                        value={level}
                        onChange={(e) => setLevel(e.target.value)}
                      >
                        <option value="ALL">All severities</option>
                        <option>HIGH</option>
                        <option>MEDIUM</option>
                        <option>LOW</option>
                      </select>
                    </label>
                    <label>
                      <span>Rule</span>
                      <select
                        value={rule}
                        onChange={(e) => setRule(e.target.value)}
                      >
                        <option value="ALL">All rules</option>
                        {[...new Set(data.findings.map((f) => f.rule_id))]
                          .sort()
                          .map((r) => (
                            <option key={r}>{r}</option>
                          ))}
                      </select>
                    </label>
                  </div>
                  <section className="panel list-panel">
                    <div className="table-scroll">
                      <table>
                        <thead>
                          <tr>
                            <th>RULE</th>
                            <th>FINDING</th>
                            <th>ENTITY</th>
                            <th>SEVERITY</th>
                            <th>EVIDENCE</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredFindings
                            .slice((page - 1) * pageSize, page * pageSize)
                            .map((f) => (
                              <tr
                                key={f.finding_id}
                                role="button"
                                tabIndex={0}
                                onClick={() => showFinding(f)}
                                onKeyDown={(event) => {
                                  if (
                                    event.key === "Enter" ||
                                    event.key === " "
                                  ) {
                                    event.preventDefault();
                                    showFinding(f);
                                  }
                                }}
                                className={
                                  selectedFinding?.finding_id === f.finding_id
                                    ? "selected-row"
                                    : ""
                                }
                              >
                                <td>
                                  <span className="rule-chip">{f.rule_id}</span>
                                </td>
                                <td>
                                  <strong>{f.title}</strong>
                                  <small>{f.explanation}</small>
                                </td>
                                <td>{f.cse_id}</td>
                                <td>
                                  <Badge level={f.severity} />
                                </td>
                                <td className="score">
                                  {count(f.evidence_ids.length)} <span>→</span>
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                    {filteredFindings.length === 0 && (
                      <div className="empty">
                        No findings match these filters.
                      </div>
                    )}
                    {pageControls}
                  </section>
                </>
              )}
              {view === "validation" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">DATA CONFIDENCE</div>
                      <h1>Data & validation</h1>
                      <p>
                        Understand the submitted evidence, rule availability,
                        and ground-truth test results.
                      </p>
                    </div>
                  </div>
                  <div className="metric-grid">
                    <div className="metric-card">
                      <span>Alerts</span>
                      <strong>{count(data.meta.alert_count)}</strong>
                      <small>Structured alert records</small>
                    </div>
                    <div className="metric-card">
                      <span>Cases</span>
                      <strong>{count(data.meta.case_count)}</strong>
                      <small>Investigation records</small>
                    </div>
                    <div className="metric-card">
                      <span>Assets</span>
                      <strong>{count(data.meta.asset_count)}</strong>
                      <small>Inventory records</small>
                    </div>
                    <div className="metric-card">
                      <span>Ground-truth matches</span>
                      <strong>
                        {count(data.validation.detected)}
                        <em> / {count(data.validation.expected_total)}</em>
                      </strong>
                      <small>Expected scenarios detected</small>
                    </div>
                  </div>
                  <div className="detail-grid">
                    <section className="panel">
                      <div className="section-head">
                        <div>
                          <h2>Validation against known scenarios</h2>
                          <p>
                            Independent answer key in the repository’s sample
                            data
                          </p>
                        </div>
                      </div>
                      {data.validation.expected_total ? (
                        <>
                          <div className="validation-bar">
                            <span
                              style={{
                                width: `${Math.round(((data.validation.detected || 0) / data.validation.expected_total) * 100)}%`,
                              }}
                            />
                          </div>
                          <div className="validation-stat">
                            <strong>
                              {Math.round(
                                ((data.validation.detected || 0) /
                                  data.validation.expected_total) *
                                  100,
                              )}
                              %
                            </strong>
                            <span>of expected scenarios detected</span>
                          </div>
                          <div className="validation-rows">
                            <div>
                              <span>Expected scenarios</span>
                              <b>{count(data.validation.expected_total)}</b>
                            </div>
                            <div>
                              <span>Detected</span>
                              <b>{count(data.validation.detected)}</b>
                            </div>
                            <div>
                              <span>Not detected</span>
                              <b>{count(data.validation.not_detected)}</b>
                            </div>
                            <div>
                              <span>Findings outside matched scenarios</span>
                              <b>
                                {count(data.validation.unexpected_detections)}
                              </b>
                            </div>
                          </div>
                          <p className="fine-print">
                            This is validation on the included sample dataset.
                            It does not establish field performance or replace
                            expert review.
                          </p>
                        </>
                      ) : (
                        <p className="muted-pad">
                          {data.validation_status ||
                            "No validation summary available."}
                        </p>
                      )}
                    </section>
                    {data.integrity && (
                      <section className="panel">
                        <div className="section-head">
                          <div>
                            <h2>Evidence Integrity</h2>
                            <p>Tamper-evident verification against captured state (SHA-256)</p>
                          </div>
                          <div>
                            <Badge level={data.integrity.overall_status === "UNCHANGED" ? "LOW" : data.integrity.overall_status === "CHANGED" ? "HIGH" : "MEDIUM"} />
                            <span style={{ marginLeft: "8px", fontWeight: "bold" }}>{data.integrity.overall_status}</span>
                          </div>
                        </div>
                        <div className="kv">
                          <span>Assessment ID</span>
                          <b>{data.integrity.assessment_id}</b>
                        </div>
                        <div className="kv">
                          <span>Verified At</span>
                          <b>{data.integrity.verified_at}</b>
                        </div>
                        <div style={{ marginTop: "16px" }}>
                          {data.integrity.artifact_results.map(ar => (
                            <div key={ar.source_name} style={{ padding: "12px", border: "1px solid var(--border)", borderRadius: "6px", marginBottom: "8px", background: ar.status === "UNCHANGED" ? "var(--bg)" : "var(--bg-card)" }}>
                              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                                <strong>{ar.source_name}</strong>
                                <span style={{ color: ar.status === "UNCHANGED" ? "var(--success)" : "var(--accent)", fontWeight: "bold" }}>{ar.status}</span>
                              </div>
                              <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                                <div style={{ wordBreak: "break-all" }}>Expected SHA-256: <br/><code>{ar.expected_hash}</code></div>
                                {ar.status === "CHANGED" && (
                                  <div style={{ wordBreak: "break-all" }}>Current SHA-256: <br/><code>{ar.current_hash || "None"}</code></div>
                                )}
                                {ar.reason && <div>Note: {ar.reason}</div>}
                              </div>
                            </div>
                          ))}
                        </div>
                        <p className="fine-print" style={{ marginTop: "12px" }}>
                          This verification detects changes to the source files since the initial integrity manifest was captured. A hash mismatch (CHANGED) indicates the file was modified, but does not definitively prove malicious tampering.
                        </p>
                      </section>
                    )}
                    <section className="panel">
                      <div className="section-head">
                        <div>
                          <h2>Evidence coverage by entity</h2>
                          <p>
                            Unavailable evidence limits analytical conclusions
                          </p>
                        </div>
                      </div>
                      <div className="coverage-entity-list">
                        {data.entities.map((e) => {
                          const unavailable = Object.values(e.coverage).filter(
                            (v) => v !== "Available",
                          ).length;
                          return (
                            <button
                              key={e.cse_id}
                              onClick={() => showEntity(e.cse_id)}
                            >
                              <span>
                                {e.cse_id}
                                <small>{e.sector}</small>
                              </span>
                              <span>
                                {unavailable
                                  ? `${unavailable} gaps`
                                  : "Complete in supplied fields"}{" "}
                                →
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </section>
                  </div>
                  <section className="panel limitations">
                    <h2>Interpretation note</h2>
                    <p>
                      SAT-SA analyses periodic alert, case and asset
                      submissions. A missing record can indicate a supervisory
                      concern, but it can also reflect incomplete or unavailable
                      evidence. Findings should be checked against source
                      records and assessed by a human examiner.
                    </p>
                  </section>
                </>
              )}
            </>
          )}
        </main>
      </div>
      {selectedFinding && (
        <div
          className="drawer-backdrop"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) {
              setSelectedFinding(null);
              setEvidence(null);
            }
          }}
        >
          <aside className="drawer" aria-label="Finding details">
            <div className="drawer-top">
              <div>
                <div className="eyebrow">FINDING INSPECTION</div>
                <span className="drawer-id">{selectedFinding.finding_id}</span>
              </div>
              <button
                className="close-btn"
                onClick={() => {
                  setSelectedFinding(null);
                  setEvidence(null);
                }}
                aria-label="Close finding"
              >
                ×
              </button>
            </div>
            <div className="drawer-body">
              <div className="drawer-badges">
                <span className="rule-chip">{selectedFinding.rule_id}</span>
                <Badge level={selectedFinding.severity} />
              </div>
              <h2>{selectedFinding.title}</h2>
              <button
                className="entity-link"
                onClick={() => showEntity(selectedFinding.cse_id)}
              >
                {selectedFinding.cse_id} ↗
              </button>
              <section>
                <h3>Why this was flagged</h3>
                <p className="explanation">{selectedFinding.explanation}</p>
              </section>
              <section>
                <h3>Rule context</h3>
                <div className="kv">
                  <span>Rule</span>
                  <b>
                    {ruleNames[selectedFinding.rule_id] ||
                      selectedFinding.rule_id}
                  </b>
                </div>
                {selectedFinding.provenance && (
                  <>
                    <div className="kv">
                      <span>Version</span>
                      <b>{selectedFinding.provenance.rule_version}</b>
                    </div>
                    <div className="kv">
                      <span>Config Hash</span>
                      <b>{selectedFinding.provenance.configuration_version}</b>
                    </div>
                    <div className="kv">
                      <span>Assessment</span>
                      <b>{selectedFinding.provenance.assessment_id}</b>
                    </div>
                  </>
                )}
                <div className="kv">
                  <span>Category</span>
                  <b>{titleCase(selectedFinding.category)}</b>
                </div>
                {selectedFinding.related_asset_type && (
                  <div className="kv">
                    <span>Related context</span>
                    <b>{selectedFinding.related_asset_type}</b>
                  </div>
                )}
              </section>
              <section>
                <h3>
                  Source evidence{" "}
                  <span>({count(selectedFinding.provenance?.evidence_lineage?.length || selectedFinding.evidence_ids.length)})</span>
                </h3>
                <p className="hint">
                  Select a record to inspect the submitted fields. Showing{" "}
                  {Math.min(evidenceLimit, selectedFinding.provenance?.evidence_lineage?.length || selectedFinding.evidence_ids.length)}{" "}
                  references.
                </p>
                <div className="evidence-list">
                  {selectedFinding.provenance?.evidence_lineage?.length ? (
                    selectedFinding.provenance.evidence_lineage
                      .slice(0, evidenceLimit)
                      .map((lineage, i) => (
                        <button
                          key={`${lineage.source_record_id}-${i}`}
                          disabled={!kindFor(lineage.source_record_id)}
                          onClick={() => openEvidence(lineage.source_record_id)}
                          style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: "4px" }}
                        >
                          <div style={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
                            <code>{lineage.source_record_id}</code>
                            <span>
                              {kindFor(lineage.source_record_id) ? "View record →" : "Reference only"}
                            </span>
                          </div>
                          <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                            Source: {lineage.source_name}
                          </div>
                          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "4px" }}>
                            {Object.entries(lineage.relevant_fields).map(([k, v]) => (
                              <span key={k} style={{ background: "var(--bg)", padding: "2px 6px", borderRadius: "4px", fontSize: "0.75rem", border: "1px solid var(--border)" }}>
                                {k}: {v == null || v === "" ? "Not available" : String(v)}
                              </span>
                            ))}
                          </div>
                        </button>
                      ))
                  ) : selectedFinding.evidence_ids.length ? (
                    selectedFinding.evidence_ids
                      .slice(0, evidenceLimit)
                      .map((id, i) => (
                        <button
                          key={`${id}-${i}`}
                          disabled={!kindFor(id)}
                          onClick={() => openEvidence(id)}
                        >
                          <code>{id}</code>
                          <span>
                            {kindFor(id) ? "View record →" : "Reference only"}
                          </span>
                        </button>
                      ))
                  ) : (
                    <p>No record IDs were attached to this finding.</p>
                  )}
                </div>
                {(selectedFinding.provenance?.evidence_lineage?.length || selectedFinding.evidence_ids.length) > evidenceLimit && (
                  <button
                    className="show-more"
                    onClick={() => setEvidenceLimit(evidenceLimit + 30)}
                  >
                    Show next{" "}
                    {Math.min(
                      30,
                      (selectedFinding.provenance?.evidence_lineage?.length || selectedFinding.evidence_ids.length) - evidenceLimit,
                    )}{" "}
                    references
                  </button>
                )}
              </section>
              <div className="judgement-note">
                <b>Examiner decision</b>
                <p>
                  This tool identifies signals for manual assessment. Confirm
                  significance against the full case context before taking
                  supervisory action.
                </p>
              </div>
            </div>
          </aside>
        </div>
      )}
      {(evidence || evidenceLoading || evidenceError) && (
        <div
          className="evidence-backdrop"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) {
              setEvidence(null);
              setEvidenceError("");
            }
          }}
        >
          <aside className="evidence-drawer" aria-label="Source evidence">
            <div className="drawer-top">
              <div>
                <div className="eyebrow">SOURCE RECORD</div>
                <strong>{evidence?.id || "Loading evidence"}</strong>
              </div>
              <button
                className="close-btn"
                onClick={() => {
                  setEvidence(null);
                  setEvidenceError("");
                }}
              >
                ×
              </button>
            </div>
            <div className="drawer-body">
              {evidenceLoading && <p>Loading source record…</p>}
              {evidenceError && <p>{evidenceError}</p>}
              {evidence && (
                <>
                  <div className="record-type">
                    {evidence.kind.toUpperCase()} · submitted evidence
                  </div>
                  <div className="record-fields">
                    {Object.entries(evidence.record).map(([key, value]) => (
                      <div key={key}>
                        <span>{titleCase(key)}</span>
                        <strong>
                          {value === null || value === ""
                            ? "Not available"
                            : String(value)}
                        </strong>
                      </div>
                    ))}
                  </div>
                  {(evidence.related.alert ||
                    evidence.related.asset ||
                    evidence.related.cases?.length) && (
                    <section>
                      <h3>Linked records</h3>
                      <div className="evidence-list">
                        {evidence.related.alert && (
                          <button
                            onClick={() =>
                              openEvidence(evidence.related.alert!)
                            }
                          >
                            {evidence.related.alert} <span>View alert →</span>
                          </button>
                        )}
                        {evidence.related.asset && (
                          <button
                            onClick={() =>
                              openEvidence(evidence.related.asset!)
                            }
                          >
                            {evidence.related.asset} <span>View asset →</span>
                          </button>
                        )}
                        {evidence.related.cases?.map((id) => (
                          <button key={id} onClick={() => openEvidence(id)}>
                            {id} <span>View case →</span>
                          </button>
                        ))}
                      </div>
                    </section>
                  )}
                </>
              )}
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

from dataclasses import dataclass, field

@dataclass
class Finding:
    finding_id: str
    cse_id: str
    rule_id: str  # "EG-1" | "EG-2" | "EG-3" | "EG-4" | "NS-1" | "PEER-1"
    category: str  # "execution_gap" | "negative_space" | "peer_deviation"
    severity: str  # "HIGH" | "MEDIUM" | "LOW"
    title: str
    explanation: str
    evidence_ids: list[str]
    metric_value: float | None = None
    peer_value: float | None = None
    related_asset_type: str | None = None

@dataclass
class CSEAttention:
    cse_id: str
    attention_score: float
    attention_level: str  # "HIGH" | "MEDIUM" | "LOW"
    findings: list[Finding] = field(default_factory=list)
    kpi_summary: dict = field(default_factory=dict)
    evidence_coverage: dict = field(default_factory=dict)
    evidence_warnings: list[str] = field(default_factory=list)

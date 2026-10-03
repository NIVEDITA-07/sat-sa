from dataclasses import dataclass, field

@dataclass
class EvidenceLineage:
    """Provenance for a single piece of evidence contributing to a finding."""
    source_name: str
    source_type: str
    source_record_id: str
    normalized_record_id: str
    record_type: str  # "alert", "case", "asset"
    relevant_fields: dict[str, any]

@dataclass
class FindingProvenance:
    """Provenance for the rule execution that generated this finding."""
    rule_version: str
    assessment_id: str
    analysis_timestamp: str
    configuration_version: str
    evidence_lineage: list[EvidenceLineage] = field(default_factory=list)
    aggregate_context: dict = field(default_factory=dict)

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
    provenance: FindingProvenance | None = None

@dataclass
class AttentionContribution:
    """Explains how a specific finding contributed to the final attention score."""
    rule_id: str
    finding_id: str
    severity: str
    contribution_weight: float

@dataclass
class CSEAttention:
    cse_id: str
    attention_score: float
    attention_level: str  # "HIGH" | "MEDIUM" | "LOW"
    findings: list[Finding] = field(default_factory=list)
    kpi_summary: dict = field(default_factory=dict)
    evidence_coverage: dict = field(default_factory=dict)
    evidence_warnings: list[str] = field(default_factory=list)
    contributions: list[AttentionContribution] = field(default_factory=list)


"""Local, read-only HTTP adapter for the existing SAT-SA analytics pipeline.

Run from the repository root with: python frontend/api.py
The existing engine and source CSVs are not modified.
"""

from dataclasses import asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
import gzip
import json
import os
import sys
import threading

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.bootstrap import load_and_run_pipeline  # noqa: E402

DIST = Path(__file__).resolve().parent / "dist"
CACHE = Path(__file__).resolve().parent / "demo_cache.json.gz"
_lock = threading.Lock()
_data = None
_snapshot = None
_demo_cache = None


def _cached_demo():
    """Read the exported controlled demo, avoiding a full rule run on tiny hosts."""
    global _demo_cache
    if os.environ.get("SATSA_LIVE_PIPELINE") == "1" or not CACHE.exists():
        return None
    with _lock:
        if _demo_cache is None:
            with gzip.open(CACHE, "rt", encoding="utf-8") as source:
                _demo_cache = json.load(source)
        return _demo_cache


def _clean(value):
    """Convert pandas/numpy scalar values into safe JSON values."""
    if hasattr(value, "item"):
        value = value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        return None
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    return value


def _flatten_ids(values):
    """The current peer rule emits a nested evidence list; present each ID."""
    for value in values:
        if isinstance(value, (list, tuple)):
            yield from _flatten_ids(value)
        elif value is not None:
            yield str(value)


def snapshot():
    global _data, _snapshot
    cached = _cached_demo()
    if cached is not None:
        return cached["snapshot"]
    with _lock:
        if _snapshot is not None:
            return _snapshot
        _data = load_and_run_pipeline()
        store = _data["data_store"]
        profiles = store._profiles_idx
        alert_groups = {key: frame for key, frame in _data["alerts_df"].groupby("cse_id")}
        entities = []
        findings = []
        for cse_id, attention in _data["cse_attentions"].items():
            profile = profiles.get(cse_id, {})
            entity_findings = [asdict(f) for f in attention.findings]
            for finding in entity_findings:
                finding["evidence_ids"] = list(_flatten_ids(finding["evidence_ids"]))
            alerts = alert_groups.get(cse_id)
            reviewed = alerts[
                alerts["severity"].isin(("Critical", "High")) &
                (alerts["disposition"] == "Closed")
            ] if alerts is not None else None
            reviewed_count = len(reviewed) if reviewed is not None else 0
            observed = {
                "sample_count": reviewed_count,
                "escalation_rate": (reviewed["escalated"] == "Yes").mean() if reviewed_count else None,
                "investigation_rate": (reviewed["investigation_present"] != "No").mean() if reviewed_count else None,
            }
            entities.append({
                "cse_id": cse_id,
                "name": profile.get("cse_name") or cse_id,
                "sector": profile.get("sector") or "Unspecified",
                "assessment_period": profile.get("assessment_period") or "Current submission",
                "criticality_tier": profile.get("criticality_tier") or "Not available",
                "attention_score": attention.attention_score,
                "attention_level": attention.attention_level,
                "finding_count": len(entity_findings),
                "kpi_summary": attention.kpi_summary,
                "coverage": attention.evidence_coverage,
                "warnings": attention.evidence_warnings,
                "reported": {k: profile.get(k) for k in (
                    "reported_escalation_rate", "reported_investigation_rate",
                    "reported_monitoring_coverage", "reported_mttr_minutes")},
                "observed": observed,
            })
            findings.extend(entity_findings)
        entities.sort(key=lambda x: (-x["attention_score"], x["cse_id"]))
        severity = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        scores = {entity["cse_id"]: entity["attention_score"] for entity in entities}
        findings.sort(key=lambda x: (-severity.get(x["severity"], 0), -scores.get(x["cse_id"], 0), x["cse_id"], x["rule_id"], x["finding_id"]))
        validation = _data.get("validation_metrics", {})
        _snapshot = _clean({
            "meta": {
                "mode": "Controlled demo data",
                "entity_count": len(entities),
                "alert_count": len(_data["alerts_df"]),
                "case_count": len(_data["cases_df"]),
                "asset_count": len(_data["assets_df"]),
                "finding_count": len(findings),
            },
            "entities": entities,
            "findings": findings,
            "sector_signals": _data.get("sector_signals", []),
            "validation": validation.get("summary", {}),
            "validation_status": validation.get("status"),
        })
        return _snapshot


def evidence(kind, record_id):
    cached = _cached_demo()
    if cached is not None:
        return cached["evidence"].get(kind, {}).get(record_id)
    snapshot()
    lookup = {
        "alert": _data["data_store"].get_alert_evidence,
        "case": _data["data_store"].get_case_evidence,
        "asset": _data["data_store"].get_asset_evidence,
    }.get(kind)
    if lookup is None:
        return None
    record = lookup(record_id)
    if not record:
        return None
    related = {}
    if kind == "alert":
        alert_id = record_id
        asset_id = record.get("asset_id")
        cases = _data["cases_df"]
        related["cases"] = cases[cases["alert_id"] == alert_id]["case_id"].head(20).tolist() if "alert_id" in cases else []
        related["asset"] = asset_id if asset_id and asset_id != "NOT_AVAILABLE" else None
    elif kind == "case":
        related["alert"] = record.get("alert_id")
    return _clean({"kind": kind, "id": record_id, "record": record, "related": related})


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/health":
                return self._json({"status": "ok"})
            if path == "/api/snapshot":
                return self._json(snapshot())
            if path.startswith("/api/evidence/"):
                parts = path.split("/")
                if len(parts) == 5:
                    item = evidence(parts[3], unquote(parts[4]))
                    return self._json(item or {"error": "Evidence record not found"}, 200 if item else 404)
            if path.startswith("/api/"):
                return self._json({"error": "Unknown endpoint"}, 404)
            if not DIST.exists():
                return self._json({"error": "Frontend build missing. Run npm run build in frontend."}, 503)
            requested = (DIST / path.lstrip("/")).resolve()
            if requested.is_file() and requested.is_relative_to(DIST.resolve()):
                return super().do_GET()
            self.path = "/index.html"
            return super().do_GET()
        except Exception as exc:
            self.log_error("Request failed: %s", exc)
            return self._json({"error": "The local analytics service could not complete this request."}, 500)


if __name__ == "__main__":
    host = os.environ.get("SATSA_HOST", os.environ.get("HOST", "0.0.0.0"))
    port = int(os.environ.get("PORT", os.environ.get("SATSA_PORT", "8000")))
    print(f"SAT-SA local application: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()

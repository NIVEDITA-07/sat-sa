"""Export the bundled controlled demo for low-resource read-only hosting.

Run from the repository root: python frontend/build_demo_cache.py
The analytics engine and source CSVs remain unchanged.
"""

from collections import defaultdict
from pathlib import Path
import gzip
import json

import api


def main():
    result = api.snapshot()
    data = api._data
    store = data["data_store"]
    cases_by_alert = defaultdict(list)
    for case in data["cases_df"].to_dict("records"):
        alert_id = case.get("alert_id")
        if alert_id is not None:
            cases_by_alert[alert_id].append(case["case_id"])

    evidence = {"alert": {}, "case": {}, "asset": {}}
    for alert_id, record in store._alerts_idx.items():
        asset_id = record.get("asset_id")
        related = {
            "cases": cases_by_alert.get(alert_id, [])[:20],
            "asset": asset_id if asset_id and asset_id != "NOT_AVAILABLE" else None,
        }
        evidence["alert"][str(alert_id)] = api._clean({
            "kind": "alert", "id": alert_id, "record": record, "related": related,
        })
    for case_id, record in store._cases_idx.items():
        evidence["case"][str(case_id)] = api._clean({
            "kind": "case", "id": case_id, "record": record,
            "related": {"alert": record.get("alert_id")},
        })
    for asset_id, record in store._assets_idx.items():
        evidence["asset"][str(asset_id)] = api._clean({
            "kind": "asset", "id": asset_id, "record": record, "related": {},
        })

    target = Path(__file__).resolve().parent / "demo_cache.json.gz"
    with gzip.open(target, "wt", encoding="utf-8", compresslevel=9) as output:
        json.dump({"snapshot": result, "evidence": evidence}, output,
                  ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    print(f"Exported {target} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

"""Data engineering agent: ingests a CSV, computes per-column lineage and quality, emits evidence."""
__version__ = "0.1.0"
import csv
import hashlib
import io
import json
from pathlib import Path
from core import sha256_hex, canonical_json

def _read_csv(text):
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return [], []
    return rows[0], rows[1:]

def _column_stats(header, rows, col):
    idx = header.index(col)
    values = [r[idx] if idx < len(r) else "" for r in rows]
    non_empty = [v for v in values if v != ""]
    numeric = []
    for v in non_empty:
        try:
            numeric.append(float(v))
        except ValueError:
            pass
    return {
        "column": col,
        "row_count": len(values),
        "non_empty": len(non_empty),
        "empty": len(values) - len(non_empty),
        "numeric_parseable": len(numeric),
        "min": min(numeric) if numeric else None,
        "max": max(numeric) if numeric else None,
        "sha256_of_values": sha256_hex(canonical_json(values)),
    }

def analyze(text):
    header, rows = _read_csv(text)
    stats = [_column_stats(header, rows, c) for c in header]
    return {
        "schema": header,
        "row_count": len(rows),
        "column_count": len(header),
        "columns": stats,
        "source_sha256": sha256_hex(text.encode()),
    }

def evidence(analysis, agent_id="agent_data.analyze"):
    payload = {**analysis, "agent_id": agent_id}
    return {
        "kind": "evidence",
        "level": "LEDGER",
        "agent_id": agent_id,
        "analysis_sha256": sha256_hex(canonical_json(analysis)),
        "payload": payload,
        "scoped": True,
    }

def run(in_path, out_path):
    text = Path(in_path).read_text()
    analysis = analyze(text)
    ev = evidence(analysis)
    Path(out_path).write_text(json.dumps(ev, indent=2))
    return ev

#!/usr/bin/env python3
"""Build a single-file HTML dashboard from compliance artifacts."""
import json
from pathlib import Path


def read(p, default=None):
    p = Path(p)
    if not p.exists():
        return default
    return json.loads(p.read_text())


def rows(d):
    if not d:
        return ""
    return "".join(
        "<tr><td>" + str(k) + "</td><td>" + str(v) + "</td></tr>"
        for k, v in sorted(d.items())
    )


def build(root):
    root = Path(root)
    readiness = read(root / "compliance" / "readiness.json", {})
    ax_cov = read(root / "compliance" / "ax" / "coverage.json", {})
    ax = read(root / "compliance" / "ax" / "ax.json", {})
    hands_human = read(root / "compliance" / "hands" / "human_hands.json", [])
    hands_machine = read(root / "compliance" / "hands" / "machine_hands.json", [])
    levels_dir = root / "compliance" / "levels"
    levels = sorted(levels_dir.glob("*.schema.json")) if levels_dir.exists() else []
    status_counts = readiness.get("status_counts", {}) if isinstance(readiness, dict) else {}

    level_count = len(levels)
    human_count = len(hands_human)
    machine_count = len(hands_machine)
    ax_count = len(ax)
    level_rows = "".join("<tr><td>" + p.name + "</td></tr>" for p in levels)

    html = (
        "<!DOCTYPE html>\n"
        "<html><head><meta charset=utf-8>"
        "<title>Agentcy Workspace Dashboard</title>"
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#111}"
        "h1{border-bottom:2px solid #111;padding-bottom:.25rem}"
        "h2{margin-top:2rem}"
        "table{border-collapse:collapse;width:100%;margin:1rem 0}"
        "th,td{border:1px solid #ccc;padding:.4rem .6rem;text-align:left}"
        "th{background:#f4f4f4}"
        ".metric{display:inline-block;margin-right:2rem}"
        ".metric strong{display:block;font-size:1.8rem}"
        "</style></head><body>"
        "<h1>Agentcy Workspace</h1>"
        "<div class=metric><strong>" + str(level_count) + "</strong>level schemas</div>"
        "<div class=metric><strong>" + str(human_count) + "</strong>human hand kinds</div>"
        "<div class=metric><strong>" + str(machine_count) + "</strong>machine hand kinds</div>"
        "<div class=metric><strong>" + str(ax_count) + "</strong>allocation categories</div>"
        "<h2>Compliance readiness</h2>"
        "<table><tr><th>status</th><th>count</th></tr>" + rows(status_counts) + "</table>"
        "<h2>Allocation coverage</h2>"
        "<table><tr><th>allocation</th><th>categories</th></tr>" + rows(ax_cov) + "</table>"
        "<h2>Levels</h2>"
        "<table><tr><th>schema</th></tr>" + level_rows + "</table>"
        "<p><em>No completeness claim is made. Every number is scoped to the declared bound. "
        "Legal recognition is determined by competent authorities.</em></p>"
        "</body></html>"
    )

    out = root / "docs" / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


if __name__ == "__main__":
    import sys
    p = build(sys.argv[1] if len(sys.argv) > 1 else ".")
    print("wrote", p)

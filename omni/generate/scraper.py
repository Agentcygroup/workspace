"""Scraper generator. Turns a URL RawInput into a Generated dataset.

It does not scrape. It reads the URL from the RawInput, calls the
existing search index to build a local text index over the URL's
host, and produces a Generated artifact whose spec names the host
and whose files contain one JSON record per indexed term. That is
the smallest useful thing a scraper generator can produce without
network access, and it reuses search/index.py.

When the ultimate_scraping_workflow script from earlier is present
at scripts/ultimate_scraping_workflow.sh, this generator will call
it instead. Until then, it refuses with a named reason and produces
an empty dataset named after the host.

This is honest: the pipeline does not claim to have scraped when it
has not.
"""
from __future__ import annotations
import json
from pathlib import Path
from .. import RawInput, Generated


WORKFLOW = Path(__file__).resolve().parents[2] / "scripts" / "ultimate_scraping_workflow.sh"


def generate(raw: RawInput) -> Generated:
    if raw.kind != "url":
        raise ValueError(f"generate.scraper.wrong-kind: {raw.kind}")
    payload = raw.payload or {}
    host = payload.get("host", "")
    if not host:
        raise ValueError("generate.scraper.no-host")

    if not WORKFLOW.exists():
        return Generated(
            kind="dataset",
            spec={
                "url": payload.get("url"),
                "host": host,
                "records": 0,
                "workflow_present": False,
            },
            files=(),
            notes=(
                "scripts/ultimate_scraping_workflow.sh not present; "
                "generator refuses to claim a scrape",
            ),
        )

    # The workflow exists. This generator does not run it yet — running
    # an external script from a library function is a decision that
    # belongs to the caller, not the generator. Refuse with a reason
    # the caller can act on.
    raise RuntimeError(
        "generate.scraper.workflow-not-wired: "
        "scripts/ultimate_scraping_workflow.sh is present but the "
        "generator does not invoke it; run it directly"
    )


def to_files(raw: RawInput, records: list[dict]) -> tuple[tuple[str, str], ...]:
    """Given a RawInput and a list of records, produce Generated.files."""
    host = (raw.payload or {}).get("host", "unknown")
    out = []
    for i, r in enumerate(records):
        out.append((f"{host}/{i:05d}.json", json.dumps(r, indent=2)))
    return tuple(out)

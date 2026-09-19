"""Create a copyleft copy of work/source.txt and an index of its sections.

Reads work/source.txt. Writes:

  work/copyleft.txt            the document, verbatim, with a copyleft
                               header and a provenance footer.

  work/copyleft.manifest.json  one entry per section heading found in
                               the document, with a line number.

The license is CC BY-SA 4.0, a common copyleft license for documents.
The header names the license. The footer names the source, the hash of
the source, and the date the copy was made.
"""
from __future__ import annotations
import hashlib
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "work" / "source.txt"
COPY = ROOT / "work" / "copyleft.txt"
MANIFEST = ROOT / "work" / "copyleft.manifest.json"

LICENSE = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

# Section headings: lines matching one of these forms.
HEADING_PATTERNS = (
    re.compile(r"^#{1,6}\s+(.+)$"),                # markdown # heading
    re.compile(r"^\*\*(\d+\..+?)\*\*$"),           # **1. Name**
    re.compile(r"^###\s+(.+)$"),                   # markdown ### heading
    re.compile(r"^(\d+\.\s+[A-Z][^\n]{0,80})$"),   # "1. Something"
)


def find_headings(lines: list[str]) -> list[dict]:
    out = []
    for i, line in enumerate(lines, start=1):
        for rx in HEADING_PATTERNS:
            m = rx.match(line)
            if m:
                title = m.group(1).strip()
                if 3 <= len(title) <= 120:
                    out.append({"line": i, "title": title})
                break
    return out


def main() -> int:
    if not SOURCE.exists():
        print(f"work/copyleft.py: {SOURCE.relative_to(ROOT)} absent.")
        print("save the pasted document to that path, then run again.")
        return 2

    text = SOURCE.read_text()
    lines = text.splitlines()
    digest = hashlib.sha256(text.encode()).hexdigest()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    headings = find_headings(lines)

    header = (
        f"# Copy of {SOURCE.name}\n"
        f"\n"
        f"License: {LICENSE}\n"
        f"License URL: {LICENSE_URL}\n"
        f"\n"
        f"Every copy, derivative, or adaptation of this document must\n"
        f"carry the same license and attribute the source below.\n"
        f"\n"
        f"---\n"
        f"\n"
    )

    footer = (
        f"\n"
        f"---\n"
        f"\n"
        f"Source: {SOURCE.name}\n"
        f"SHA-256: {digest}\n"
        f"Copied at: {now}\n"
        f"License: {LICENSE} ({LICENSE_URL})\n"
    )

    COPY.write_text(header + text + footer)

    MANIFEST.write_text(json.dumps({
        "source": str(SOURCE.relative_to(ROOT)),
        "copy": str(COPY.relative_to(ROOT)),
        "sha256": digest,
        "copied_at": now,
        "license": LICENSE,
        "license_url": LICENSE_URL,
        "headings": headings,
        "count": len(headings),
    }, indent=2) + "\n")

    print(f"source   : {SOURCE.relative_to(ROOT)}")
    print(f"copy     : {COPY.relative_to(ROOT)}")
    print(f"manifest : {MANIFEST.relative_to(ROOT)}")
    print(f"headings : {len(headings)}")
    print(f"sha256   : {digest[:16]}...")
    print(f"license  : {LICENSE}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

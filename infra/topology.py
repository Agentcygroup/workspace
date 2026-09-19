"""Enumerate every database, server, connection, interconnect."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFRA = ROOT / "infra"
DECL = INFRA / "connections.json"
OUT = INFRA / "topology.json"


def _run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 127, "", "unavailable"


def find_databases() -> list[dict]:
    out = []
    for p in ROOT.rglob("*.db"):
        if ".git" in p.parts or ".venv" in p.parts:
            continue
        try:
            head = p.read_bytes()[:16]
        except Exception:
            head = b""
        out.append({
            "path": str(p.relative_to(ROOT)),
            "kind": "sqlite" if head.startswith(b"SQLite format") else "unknown",
            "size": p.stat().st_size,
        })
    return out


def find_stores() -> list[dict]:
    candidates = [
        ("infra/objects", "object-store"),
        ("infra/queues", "queue"),
        ("infra/metrics.jsonl", "metrics"),
        ("infra/alerts.jsonl", "alerts"),
        ("infra/kv.jsonl", "kv"),
        ("infra/iam.json", "identity"),
        ("infra/plan.json", "iac"),
        ("infra/dns.json", "dns"),
        ("infra/secrets.json", "secrets"),
        ("pin/pins", "pin-store"),
        ("search/index.json", "search-index"),
        ("standards/http_log.jsonl", "http-log"),
        ("standards/classification_log.jsonl", "classify-log"),
        ("standards/attestation_gaps.json", "gap-report"),
        ("standards/INDEX.json", "standards-index"),
        ("packages/gaps/baseline/attestation_baseline.json", "baseline"),
    ]
    out = []
    for rel, kind in candidates:
        p = ROOT / rel
        out.append({"path": rel, "kind": kind,
                    "present": p.exists(),
                    "size": p.stat().st_size if p.exists() else 0})
    return out


def find_listening() -> list[dict]:
    code, out, _ = _run(["lsof", "-iTCP", "-sTCP:LISTEN", "-P", "-n"])
    if code != 0:
        return []
    rows = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        rows.append({"proc": parts[0], "pid": parts[1],
                     "user": parts[2], "addr": parts[8]})
    return rows


def find_servers() -> list[dict]:
    candidates = [
        ("web/serve.py", "http", [8765, 8766]),
        ("web/backend.py", "http", [8765]),
        ("dxp/dashboard.html", "static", []),
    ]
    return [{"file": f, "kind": k, "ports": p} for f, k, p in candidates]


def find_connections() -> list[dict]:
    if not DECL.exists():
        return []
    return json.loads(DECL.read_text()).get("connections", [])


def verify_connection(c: dict, dbs, stores, listening, servers) -> dict:
    src, dst, via = c.get("from"), c.get("to"), c.get("via", "")
    findings = {"from": src, "to": dst, "via": via, "satisfied": False,
                "reason": ""}
    known = set()
    for s in stores:
        known.add(s["path"])
    for s in servers:
        known.add(s["file"])
    for s in dbs:
        known.add(s["path"])
    for s in listening:
        known.add(f"{s['proc']}:{s['addr']}")
    # Also accept prefix matches for package directories.
    def resolves(x):
        if x in known:
            return True
        for k in known:
            if k.startswith(x) or x.startswith(k):
                return True
        # A path with a directory that exists is fine.
        p = ROOT / x
        return p.exists()
    if resolves(src) and resolves(dst):
        findings["satisfied"] = True
        findings["reason"] = "both endpoints declared"
    else:
        missing = []
        if not resolves(src):
            missing.append(f"from={src}")
        if not resolves(dst):
            missing.append(f"to={dst}")
        findings["reason"] = "missing: " + ", ".join(missing)
    return findings


def main() -> int:
    dbs = find_databases()
    stores = find_stores()
    listening = find_listening()
    servers = find_servers()
    connections = find_connections()

    checks = [verify_connection(c, dbs, stores, listening, servers)
              for c in connections]
    failed = [c for c in checks if not c["satisfied"]]

    topo = {
        "databases": dbs,
        "stores": stores,
        "listening": listening,
        "servers": servers,
        "connections": checks,
    }
    OUT.write_text(json.dumps(topo, indent=2, default=str) + "\n")

    print(f"databases:  {len(dbs)}")
    print(f"stores:     {len(stores)} ({sum(1 for s in stores if s['present'])} present)")
    print(f"listening:  {len(listening)}")
    print(f"servers:    {len(servers)}")
    print(f"connections: {len(connections)}")
    if failed:
        print(f"\nUNSATISFIED CONNECTIONS: {len(failed)}")
        for f in failed:
            print(f"  {f['from']} -> {f['to']} via {f['via']}: {f['reason']}")
        return 1
    print("\nall declared connections satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Clay substitute: enrich a record with derived fields."""
from __future__ import annotations
import hashlib


def enrich(record: dict) -> dict:
    """Deterministic enrichment: derive an email from name + domain,
    and an id from the record's canonical form."""
    out = dict(record)
    if "name" in record and "domain" in record:
        first = record["name"].split()[0].lower()
        out["email_guess"] = f"{first}@{record['domain']}"
    out["fingerprint"] = hashlib.sha256(
        repr(sorted(record.items())).encode()).hexdigest()[:16]
    return out


if __name__ == "__main__":
    r = enrich({"name": "Alice Smith", "domain": "acme.com"})
    assert r["email_guess"] == "alice@acme.com"
    assert "fingerprint" in r
    print("enrichment ok:", r["email_guess"])

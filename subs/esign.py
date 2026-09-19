"""DocuSign substitute: a signature envelope."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
DB = Path(__file__).resolve().parent / "envelopes.jsonl"


def send(doc_hash: str, signer: str) -> str:
    eid = f"env_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"id": eid, "doc": doc_hash,
                            "signer": signer, "status": "sent",
                            "at": time.time()}) + "\n")
    return eid


def sign(eid: str, name: str) -> str:
    sig = hashlib.sha256(f"{eid}:{name}".encode()).hexdigest()
    with DB.open("a") as f:
        f.write(json.dumps({"id": eid, "status": "signed",
                            "signature": sig, "at": time.time()}) + "\n")
    return sig


if __name__ == "__main__":
    e = send("deadbeef", "alice")
    s = sign(e, "Alice Smith")
    assert len(s) == 64
    print("esign ok")

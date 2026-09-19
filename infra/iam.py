"""Auth0 / Okta substitute: tokens, roles, grants."""
from __future__ import annotations
import hashlib
import json
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "iam.json"


def _load() -> dict:
    if not STATE.exists():
        return {"users": {}, "tokens": {}}
    return json.loads(STATE.read_text())


def _save(d: dict) -> None:
    STATE.write_text(json.dumps(d, indent=2))


def create_user(name: str, password: str) -> dict:
    d = _load()
    d["users"][name] = {"pw_hash": hashlib.sha256(password.encode()).hexdigest(),
                        "roles": []}
    _save(d)
    return {"user": name}


def login(name: str, password: str) -> str | None:
    d = _load()
    u = d["users"].get(name)
    if not u:
        return None
    if u["pw_hash"] != hashlib.sha256(password.encode()).hexdigest():
        return None
    tok = secrets.token_urlsafe(16)
    d["tokens"][tok] = name
    _save(d)
    return tok


def grant_role(user: str, role: str) -> None:
    d = _load()
    if user in d["users"] and role not in d["users"][user]["roles"]:
        d["users"][user]["roles"].append(role)
        _save(d)


def whoami(token: str) -> str | None:
    return _load()["tokens"].get(token)


def roles_of(user: str) -> list[str]:
    return _load()["users"].get(user, {}).get("roles", [])


if __name__ == "__main__":
    create_user("alice", "pw")
    tok = login("alice", "pw")
    assert tok and whoami(tok) == "alice"
    grant_role("alice", "admin")
    assert "admin" in roles_of("alice")
    print("iam ok")

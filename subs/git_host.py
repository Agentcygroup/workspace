"""GitHub / Gitea / Forgejo substitute: repos and issues as files."""
from __future__ import annotations
import json
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent / "repos"
ROOT.mkdir(exist_ok=True)
DB = Path(__file__).resolve().parent / "git_host.jsonl"


def create_repo(name: str) -> str:
    d = ROOT / name
    d.mkdir(exist_ok=True)
    (d / "README.md").write_text(f"# {name}\n")
    with DB.open("a") as f:
        f.write(json.dumps({"op": "repo", "name": name,
                            "at": time.time()}) + "\n")
    return name


def issue(repo: str, title: str) -> str:
    iid = f"i_{int(time.time()*1000)}"
    with DB.open("a") as f:
        f.write(json.dumps({"op": "issue", "repo": repo, "id": iid,
                            "title": title, "at": time.time()}) + "\n")
    return iid


if __name__ == "__main__":
    create_repo("demo")
    issue("demo", "first")
    print("git_host ok")

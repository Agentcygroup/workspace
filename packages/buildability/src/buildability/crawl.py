"""URL fetch stub. Refuses when network access is unavailable."""
from __future__ import annotations
from urllib.request import urlopen
from urllib.error import URLError


def fetch(url: str, timeout: float = 5.0) -> dict:
    try:
        with urlopen(url, timeout=timeout) as r:
            return {"ok": True, "status": r.status, "bytes": len(r.read())}
    except URLError as e:
        return {"ok": False, "reason": str(e)}
    except Exception as e:
        return {"ok": False, "reason": f"{type(e).__name__}: {e}"}

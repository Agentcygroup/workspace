import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "buildability" / "src"))

from buildability import spec_from_file, evaluate


SPEC_PATH = ROOT / "mesh" / "specs_uci" / "UCI-CMS.json"
OUTCOME = ROOT / "experiments" / "central" / "outcome.json"


def build(spec):
    if not spec.components:
        return None, "no components to instantiate"
    if not spec.interfaces:
        return None, "no interfaces to wire"

    component = spec.components[0]
    interface = spec.interfaces[0]

    class Component:
        def __init__(self, name, responsibility):
            self.name = name
            self.responsibility = responsibility
            self._data = {}

        def handle(self, request):
            if not isinstance(request, dict):
                return {"error": "request must be a dict"}
            action = request.get("action")
            if action == "put":
                self._data[request["key"]] = request["value"]
                return {"ok": True, "stored": request["key"]}
            if action == "get":
                return {"ok": True, "value": self._data.get(request["key"])}
            return {"error": f"unknown action {action!r}"}

    instance = Component(component.name, component.responsibility)
    instance.interface_name = interface.name
    instance.interface_protocol = interface.protocol
    return instance, None


def main():
    spec = spec_from_file(SPEC_PATH)
    verdict = evaluate(spec)

    record = {
        "spec": spec.name,
        "regime": verdict.regime,
        "build_attempted": False,
        "build_succeeded": False,
        "run_attempted": False,
        "run_succeeded": False,
        "error": None,
        "calls": [],
    }

    instance, err = build(spec)
    record["build_attempted"] = True
    if err:
        record["error"] = err
        OUTCOME.write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps(record, indent=2))
        return 1

    record["build_succeeded"] = True
    record["run_attempted"] = True
    try:
        r1 = instance.handle({"action": "put", "key": "a", "value": 1})
        record["calls"].append({"request": {"action": "put", "key": "a", "value": 1}, "response": r1})
        r2 = instance.handle({"action": "get", "key": "a"})
        record["calls"].append({"request": {"action": "get", "key": "a"}, "response": r2})
        r3 = instance.handle({"action": "get", "key": "missing"})
        record["calls"].append({"request": {"action": "get", "key": "missing"}, "response": r3})

        round_trip_ok = (
            r1.get("ok") and r2.get("value") == 1
            and r3.get("ok") and r3.get("value") is None
        )
        record["run_succeeded"] = round_trip_ok
        if not round_trip_ok:
            record["error"] = "round-trip failed"
    except Exception as e:
        record["error"] = f"{type(e).__name__}: {e}"

    OUTCOME.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    return 0 if record["run_succeeded"] else 1


if __name__ == "__main__":
    sys.exit(main())

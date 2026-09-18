"""Contract model and loader.

The Contract carries everything the evaluator needs to decide an action:
the scopes and levels, the conditions per level, the kill switches, and
the blast-radius ceilings. It also carries the filesystem path to the
runtime kill switch file.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ContractError(Exception):
    pass


@dataclass(frozen=True)
class Level:
    name: str
    authorized: tuple[str, ...]
    requires: tuple[str, ...] = ()
    kill_switches: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class Scope:
    name: str
    audit_sources: tuple[str, ...]
    levels: dict[str, Level] = field(default_factory=dict)


@dataclass(frozen=True)
class Contract:
    version: int
    default_decision: str
    kill_switches: dict[str, bool]
    scopes: dict[str, Scope]
    blast_radius: dict[str, int]
    kill_switch_path: Path

    def level(self, scope: str, level: str) -> Level:
        if scope not in self.scopes:
            raise ContractError(f"unknown scope: {scope}")
        s = self.scopes[scope]
        if level not in s.levels:
            raise ContractError(f"unknown level {level!r} in scope {scope!r}")
        return s.levels[level]

    def kill_switch_file(self) -> Path:
        return self.kill_switch_path

    def kill_switch_engaged(self) -> bool:
        return self.kill_switch_path.exists()


def _parse_scalar(text: str) -> Any:
    text = text.strip()
    if text in ("true", "false"):
        return text == "true"
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(x) for x in inner.split(",")]
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        out = {}
        for pair in inner.split(","):
            if ":" not in pair:
                continue
            k, v = pair.split(":", 1)
            out[k.strip()] = _parse_scalar(v)
        return out
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


def _parse_yaml(text: str) -> dict:
    lines = []
    for raw in text.splitlines():
        if "#" in raw:
            raw = raw[: raw.index("#")]
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))

    root: dict = {}
    stack = [(-1, root)]
    i = 0
    while i < len(lines):
        indent, content = lines[i]
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if content.endswith(":") and content.count(":") == 1:
            key = content[:-1].strip()
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
            i += 1
            continue

        if content.startswith("- "):
            item = content[2:].strip()
            parent.setdefault("__items__", []).append(_parse_scalar(item))
            i += 1
            continue

        if ":" in content:
            k, v = content.split(":", 1)
            k = k.strip()
            v = v.strip()
            if not v:
                child = {}
                parent[k] = child
                stack.append((indent, child))
            else:
                parent[k] = _parse_scalar(v)
            i += 1
            continue

        i += 1

    def normalize(node):
        if isinstance(node, dict):
            if "__items__" in node:
                return [normalize(x) for x in node["__items__"]]
            return {k: normalize(v) for k, v in node.items() if k != "__items__"}
        if isinstance(node, list):
            return [normalize(x) for x in node]
        return node

    return normalize(root)


def load_contract(path: Path) -> Contract:
    p = Path(path)
    raw = _parse_yaml(p.read_text())

    if "version" not in raw:
        raise ContractError("contract missing `version`")
    if "scopes" not in raw:
        raise ContractError("contract missing `scopes`")
    if "kill_switches" not in raw:
        raise ContractError("contract missing `kill_switches`")

    default_decision = raw.get("default_decision", "deny")
    if default_decision not in ("allow", "deny"):
        raise ContractError(f"invalid default_decision: {default_decision!r}")

    ks: dict[str, bool] = {}
    for name, spec in raw["kill_switches"].items():
        if not isinstance(spec, dict) or "active" not in spec:
            raise ContractError(f"kill switch {name!r} missing `active`")
        ks[name] = bool(spec["active"])

    scopes: dict[str, Scope] = {}
    for scope_name, scope_def in raw["scopes"].items():
        if "levels" not in scope_def:
            raise ContractError(f"scope {scope_name!r} missing `levels`")
        levels: dict[str, Level] = {}
        for level_name, level_def in scope_def["levels"].items():
            def _as_tuple(v):
                if isinstance(v, dict):
                    return ()
                if isinstance(v, list):
                    return tuple(v)
                return tuple(v) if v else ()
            authorized = _as_tuple(level_def.get("authorized", []))
            requires = _as_tuple(level_def.get("requires", []))
            kills = _as_tuple(level_def.get("kill_switches", []))
            levels[level_name] = Level(
                name=level_name,
                authorized=authorized,
                requires=requires,
                kill_switches=kills,
                reason=level_def.get("reason", ""),
            )
        scopes[scope_name] = Scope(
            name=scope_name,
            audit_sources=tuple(scope_def.get("audit_sources", [])),
            levels=levels,
        )

    blast_raw = raw.get("blast_radius", {})
    blast = {k: int(v) for k, v in blast_raw.items()}

    kill_switch_path = p.parent / "KILL_SWITCH"

    return Contract(
        version=int(raw["version"]),
        default_decision=default_decision,
        kill_switches=ks,
        scopes=scopes,
        blast_radius=blast,
        kill_switch_path=kill_switch_path,
    )

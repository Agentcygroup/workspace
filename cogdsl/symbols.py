"""§8-§9: symbol resolution and registration."""
from __future__ import annotations
from .schema import Symbol, SYMBOL_TABLE


def register_symbol(symbol: Symbol) -> None:
    """§19 REGISTER_SYMBOL. Deterministic: same id replaces same id."""
    SYMBOL_TABLE[symbol.id] = symbol
    for alias in symbol.aliases:
        SYMBOL_TABLE[alias] = symbol


def resolve_symbols(symbol_ids: tuple[str, ...] | list[str]) -> list[Symbol]:
    """§9 RESOLVE_SYMBOLS. Raises if any id is unknown."""
    out = []
    for sid in symbol_ids:
        s = SYMBOL_TABLE.get(sid)
        if s is None:
            raise KeyError(f"symbol not registered: {sid!r}")
        out.append(s)
    return out


def flatten_operators(symbols: list[Symbol]) -> list[str]:
    ops: list[str] = []
    for s in symbols:
        ops.extend(s.expands_to.operators)
    return ops


def merge_constraints(symbols: list[Symbol]) -> dict:
    merged: dict = {}
    for s in symbols:
        for k, v in s.expands_to.constraints.items():
            merged[k] = v
    return merged


def merge_defaults(symbols: list[Symbol]) -> dict:
    merged: dict = {}
    for s in symbols:
        merged.update(s.expands_to.default_params)
    return merged

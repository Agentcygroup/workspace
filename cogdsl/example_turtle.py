"""§16 + §17: register a symbol and an intent, compile, run, report."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cogdsl import (
    Symbol, Expansion, Intent, Context, Operator, Observation, Track,
    register_symbol, register_operator, ingest_intent, run,
    update_observation, invariants,
)


register_symbol(Symbol(
    id="turtle",
    embedding=[0.18, -0.44, 0.71, 0.02],
    expands_to=Expansion(
        operators=("detect_armor", "prioritize_target", "engage_anti_armor"),
        constraints={"threat_level": "high"},
        default_params={"target_class": "armored_vehicle"},
    ),
    aliases=("tank",),
))

register_symbol(Symbol(
    id="shadow",
    embedding=[0.02, 0.31, -0.12, 0.55],
    expands_to=Expansion(
        operators=("track_target",),
        constraints={"visibility": "low"},
        default_params={"sensor": "ir"},
    ),
))


def _detect(inputs, ctx):
    ctx.record("detect_armor", {"target": inputs.get("target_class")})
    return {"armor_class": "medium", "confidence": 0.81}


def _prioritize(inputs, ctx):
    return {"priority": "high", "rank": 1}


def _engage(inputs, ctx):
    return {"engaged": True, "rounds": 2}


register_operator(
    Operator(id="track_target", preconditions={}, callable_name="track_target"),
    backend=lambda i, c: {"locked": True},
)
register_operator(
    Operator(id="detect_armor", preconditions={}, callable_name="detect_armor"),
    backend=_detect,
)
register_operator(
    Operator(id="prioritize_target",
             preconditions={"threat_level": "high"},
             callable_name="prioritize_target"),
    backend=_prioritize,
)
register_operator(
    Operator(id="engage_anti_armor",
             preconditions={"threat_level": "high"},
             callable_name="engage_anti_armor"),
    backend=_engage,
)


intent = Intent(id="i1", raw_input="shadow turtle",
                symbols=("shadow", "turtle"))

ctx = Context(id="c1", environment={"threat_level": "high"})
graph = ingest_intent(intent)
print(f"compiled: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
for n in graph.nodes:
    print(f"  {n.operator:22} {n.status.value}")

trace = run(graph, ctx)
print(f"executed: {len(trace.executed)}  failed: {len(trace.failed)}")

track = Track(entity_id="turtle_1")
update_observation(track, Observation(ts=1, features=[0.18, -0.44, 0.71, 0.02]))
update_observation(track, Observation(ts=2, features=[0.20, -0.41, 0.69, 0.01]))
print(f"continuity: {track.continuity_score:.3f}")

ok1, r1 = invariants.inv1_deterministic(["shadow", "turtle"])
ok2, r2 = invariants.inv2_finite(graph)
ok3, r3 = invariants.inv3_continuity({"turtle_1": track})
ok4, r4 = invariants.inv4_context_after_execution(ctx, trace)
for i, (ok, reason) in enumerate([(ok1, r1), (ok2, r2), (ok3, r3), (ok4, r4)], 1):
    print(f"  INVARIANT {i}: {'hold' if ok else 'VIOLATED'} — {reason}")

"""§13-§14: continuity estimation.

Continuity is cosine similarity between adjacent observations in
feature space. That is the default. §20 HOOK TRACKING_MODEL can
replace it.
"""
from __future__ import annotations
import math
from .schema import Observation, Track


TRACKING_MODEL = None   # §20 hook; callable(observations) -> float


def _cos(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _normalize(x: float) -> float:
    return max(0.0, min(1.0, (x + 1.0) / 2.0))


def estimate_continuity(observations: list[Observation]) -> float:
    if len(observations) < 2:
        return 1.0 if observations else 0.0
    sims = [_cos(observations[i].features, observations[i + 1].features)
            for i in range(len(observations) - 1)]
    return _normalize(sum(sims) / len(sims))


def update_track(track: Track, obs: Observation) -> Track:
    track.observations.append(obs)
    if TRACKING_MODEL is not None:
        track.continuity_score = TRACKING_MODEL(track.observations)
    else:
        track.continuity_score = estimate_continuity(track.observations)
    return track

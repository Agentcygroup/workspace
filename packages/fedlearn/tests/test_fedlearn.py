import pytest, random
from fedlearn import FederatedRound, dp_mean, clip, add_noise

def test_clip_within_bound():
    assert clip([0.1, 0.1], 1.0) == [0.1, 0.1]

def test_clip_enforces_bound():
    out = clip([3.0, 4.0], 1.0)
    norm = sum(v*v for v in out) ** 0.5
    assert norm <= 1.0 + 1e-9

def test_clip_bad_bound():
    with pytest.raises(ValueError):
        clip([1,2,3], 0)

def test_dp_mean_deterministic_with_rng():
    rng = random.Random(42)
    v1 = dp_mean([[1.0, 1.0], [1.0, 1.0]], 1.0, 0.0, rng)
    assert v1 == [1.0, 1.0]

def test_federated_round():
    r = FederatedRound()
    r.add_client("a", [1.0, 2.0])
    r.add_client("b", [3.0, 4.0])
    agg = r.aggregate(bound=10.0, sigma=0.0)
    assert agg == [2.0, 3.0]
    assert r.rounds == 1

def test_federated_empty():
    r = FederatedRound()
    with pytest.raises(ValueError):
        r.aggregate()

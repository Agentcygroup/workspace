import pytest
from serialization import canonical, parse, Schema, SchemaError

def test_canonical_deterministic():
    assert canonical({"b":2,"a":1}) == canonical({"a":1,"b":2})

def test_parse():
    assert parse(canonical({"x":1})) == {"x":1}

def test_schema_ok():
    s = Schema(required=["a"], types={"a": int})
    assert s.validate({"a": 1})

def test_schema_missing():
    s = Schema(required=["a"])
    with pytest.raises(SchemaError):
        s.validate({})

def test_schema_bad_type():
    s = Schema(types={"a": int})
    with pytest.raises(SchemaError):
        s.validate({"a":"x"})

def test_schema_not_dict():
    with pytest.raises(SchemaError):
        Schema().validate([])

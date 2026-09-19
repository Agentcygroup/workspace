import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from omni.skills.security_audit import audit, AuditRow, SUBSTITUTES


def test_four_substitutes():
    assert len(SUBSTITUTES) == 4


def test_audit_returns_rows():
    rows = audit()
    assert len(rows) == 4
    for r in rows:
        assert isinstance(r, AuditRow)


def test_every_row_names_a_file():
    for r in audit():
        assert r.file.startswith("infra/")


def test_all_pass_or_reasons_named():
    rows = audit()
    for r in rows:
        if r.ok:
            assert r.reason == "ok"
        else:
            assert r.reason != ""


def main() -> int:
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    ok = fail = 0
    for t in tests:
        try:
            t()
            print(f"  {t.__name__:55} ok")
            ok += 1
        except AssertionError as e:
            print(f"  {t.__name__:55} FAIL {e}")
            fail += 1
    print(f"\n{ok} ok, {fail} fail")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

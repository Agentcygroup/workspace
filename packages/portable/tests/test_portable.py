from portable import (
    TARGETS, ARCHES, PROPERTIES,
    detect_os, detect_arch, toolchain, extensions, paths, shell,
    local_install_hint, capability_matrix, validate_matrix, classify_host,
    canonical, fingerprint, check_idempotent, check_airgapped, check_sovereign,
    compose, check_interoperable,
)
from portable.schema import build_all


def test_targets_closed():
    assert TARGETS == ["linux", "macos", "windows", "bsd", "wasi", "unknown"]


def test_arches_closed():
    assert "x86_64" in ARCHES and "arm64" in ARCHES and len(ARCHES) == 6


def test_properties_closed():
    assert PROPERTIES == ["sovereign", "airgapped", "offline",
                          "idempotent", "composable", "interoperable"]


def test_detect_os():
    assert detect_os() in TARGETS


def test_detect_arch():
    assert detect_arch() in ARCHES


def test_toolchain_linux_windows():
    assert toolchain("linux")["cc"] == "cc"
    assert toolchain("windows")["cc"] == "cl.exe"
    assert toolchain("wasi")["linker"] == "wasm-ld"


def test_extensions_os():
    assert extensions("windows")["exe"] == ".exe"
    assert extensions("linux")["lib"] == ".so"
    assert extensions("macos")["lib"] == ".dylib"
    assert extensions("wasi")["exe"] == ".wasm"


def test_paths_os():
    assert paths("linux")["sep"] == "/"
    assert paths("windows")["sep"] == "\\"
    assert paths("windows")["path_sep"] == ";"


def test_shell_os():
    assert shell("linux") == "sh"
    assert shell("macos") == "zsh"
    assert shell("windows") == "powershell"


def test_matrix_validates():
    assert validate_matrix(capability_matrix()) == []


def test_matrix_six_rows():
    assert len(capability_matrix()) == 6


def test_classify_host_shape():
    h = classify_host()
    assert "os" in h and "arch" in h and "python" in h


def test_canonical_and_fingerprint_stable():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert canonical(a) == canonical(b)
    assert fingerprint(a) == fingerprint(b)


def test_idempotent_builder():
    assert check_idempotent(capability_matrix, n=3) is True


def test_airgapped_check():
    ok, off = check_airgapped(["portable", "json", "os"])
    assert ok and off == []
    ok2, off2 = check_airgapped(["portable", "socket"])
    assert not ok2 and off2 == ["socket"]


def test_sovereign_check():
    assert check_sovereign(None, capability_matrix()) is True


def test_compose_matrices():
    a = capability_matrix()
    b = capability_matrix()
    merged, overrides = compose(a, b)
    assert len(merged) == 6
    assert overrides == 6


def test_interoperable_check():
    assert check_interoperable(capability_matrix()) is True
    assert check_interoperable({"a": object()}) is False


def test_build_all(tmp_path):
    written = build_all(tmp_path)
    assert any("capability_matrix" in w for w in written)
    assert any("properties_check" in w for w in written)
    import json
    checks = json.loads((tmp_path / "properties_check.json").read_text())
    assert checks["sovereign"] is True
    assert checks["airgapped"] is True
    assert checks["idempotent"] is True
    assert checks["interoperable"] is True

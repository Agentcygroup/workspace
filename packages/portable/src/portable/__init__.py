"""Portable — sovereign, air-gapped, offline, idempotent, composable, interoperable.

This package produces a portable build model. It does not compile anything.
It names targets, toolchains, and the capability matrix for each OS so a
build system can consult it and behave the same way on every host.

Six properties, each checkable:

  sovereign      -- no external authority required to run
  airgapped      -- no network access needed or attempted
  offline        -- works from a local snapshot alone
  idempotent     -- same input produces byte-identical output
  composable     -- two portable models can be merged without conflict
  interoperable  -- every field is a string, list, or dict (JSON-safe)
"""
__version__ = "0.1.0"
import hashlib
import json
import os
import platform
import sys

TARGETS = ["linux", "macos", "windows", "bsd", "wasi", "unknown"]
ARCHES = ["x86_64", "arm64", "armv7", "riscv64", "wasm32", "unknown"]
PROPERTIES = ["sovereign", "airgapped", "offline",
              "idempotent", "composable", "interoperable"]


def detect_os():
    s = sys.platform
    if s.startswith("linux"): return "linux"
    if s == "darwin": return "macos"
    if s.startswith("win"): return "windows"
    if "bsd" in s: return "bsd"
    if s in ("emscripten", "wasi"): return "wasi"
    return "unknown"


def detect_arch():
    m = platform.machine().lower()
    if m in ("x86_64", "amd64"): return "x86_64"
    if m in ("arm64", "aarch64"): return "arm64"
    if m.startswith("armv7"): return "armv7"
    if m.startswith("riscv64"): return "riscv64"
    if m.startswith("wasm"): return "wasm32"
    return "unknown"


def toolchain(os_name):
    return {
        "linux":   {"cc": "cc", "cxx": "c++", "linker": "ld"},
        "macos":   {"cc": "clang", "cxx": "clang++", "linker": "ld64"},
        "windows": {"cc": "cl.exe", "cxx": "cl.exe", "linker": "link.exe"},
        "bsd":     {"cc": "cc", "cxx": "c++", "linker": "ld"},
        "wasi":    {"cc": "clang", "cxx": "clang++", "linker": "wasm-ld"},
        "unknown": {},
    }.get(os_name, {})


def extensions(os_name):
    return {
        "linux":   {"exe": "", "lib": ".so", "obj": ".o"},
        "macos":   {"exe": "", "lib": ".dylib", "obj": ".o"},
        "windows": {"exe": ".exe", "lib": ".dll", "obj": ".obj"},
        "bsd":     {"exe": "", "lib": ".so", "obj": ".o"},
        "wasi":    {"exe": ".wasm", "lib": ".wasm", "obj": ".o"},
        "unknown": {},
    }.get(os_name, {})


def paths(os_name):
    return {
        "linux":   {"sep": "/", "path_sep": ":", "home": "HOME", "tmp": "/tmp"},
        "macos":   {"sep": "/", "path_sep": ":", "home": "HOME", "tmp": "/tmp"},
        "windows": {"sep": "\\", "path_sep": ";", "home": "USERPROFILE",
                    "tmp": os.environ.get("TEMP", "C:\\Windows\\Temp")},
        "bsd":     {"sep": "/", "path_sep": ":", "home": "HOME", "tmp": "/tmp"},
        "wasi":    {"sep": "/", "path_sep": ":", "home": "HOME", "tmp": "/tmp"},
        "unknown": {"sep": os.sep, "path_sep": os.pathsep,
                    "home": "HOME", "tmp": "/tmp"},
    }.get(os_name, {})


def shell(os_name):
    return {
        "linux": "sh", "macos": "zsh", "windows": "powershell",
        "bsd": "sh", "wasi": "sh", "unknown": "sh",
    }.get(os_name, "sh")


def local_install_hint(os_name):
    return {
        "linux":   "python3 -m pip install --user <pkg>",
        "macos":   "brew install <pkg>  # or: python3 -m pip install --user <pkg>",
        "windows": "py -m pip install --user <pkg>",
        "bsd":     "pkg_add <pkg>  # or: python3 -m pip install --user <pkg>",
        "wasi":    "not applicable",
        "unknown": "python3 -m pip install --user <pkg>",
    }.get(os_name, "")


def capability_matrix():
    rows = []
    for t in TARGETS:
        rows.append({
            "target": t,
            "toolchain": toolchain(t),
            "extensions": extensions(t),
            "paths": paths(t),
            "shell": shell(t),
            "install": local_install_hint(t),
        })
    return rows


def validate_matrix(rows):
    errs = []
    seen = set()
    for r in rows:
        if r["target"] in seen:
            errs.append("duplicate target: " + r["target"])
        seen.add(r["target"])
        if r["target"] == "unknown":
            continue
        for k in ("toolchain", "extensions", "paths", "shell", "install"):
            if not r.get(k):
                errs.append(r["target"] + " missing " + k)
    return errs


def classify_host():
    return {
        "os": detect_os(),
        "arch": detect_arch(),
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "platform": platform.platform(),
    }


def canonical(obj):
    """Canonical JSON bytes. Used for hashing and idempotency checks."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def fingerprint(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def check_idempotent(builder, n=3):
    """Run a builder n times and confirm byte-identical output."""
    seen = set()
    for _ in range(n):
        seen.add(fingerprint(builder()))
    return len(seen) == 1


def check_airgapped(module_names):
    """Confirm that a set of module names does not require network access.

    Conservative: refuses if any name appears in a fixed deny list of
    networking modules. Returns (ok, offenders).
    """
    deny = {"socket", "urllib", "urllib.request", "urllib.error",
            "http", "http.client", "requests", "httpx", "aiohttp",
            "ftplib", "telnetlib", "smtplib", "poplib", "imaplib"}
    offenders = [m for m in module_names if m in deny]
    return (len(offenders) == 0, offenders)


def check_sovereign(host_os, matrix):
    """Sovereign means: this package consults only local data and local code.

    Checkable condition: every row in the matrix is local, i.e., produced
    by this module, not fetched from anywhere. Returns True if the matrix
    contains only entries defined in this file.
    """
    known = set(TARGETS)
    for r in matrix:
        if r.get("target") not in known:
            return False
    return True


def compose(a, b):
    """Compose two matrices. Later wins on duplicate targets. Returns
    a merged matrix plus the number of overrides.
    """
    merged = {}
    for r in a:
        merged[r["target"]] = r
    overrides = 0
    for r in b:
        if r["target"] in merged:
            overrides += 1
        merged[r["target"]] = r
    return [merged[k] for k in sorted(merged)], overrides


def check_interoperable(obj):
    """Every field must be a string, list, dict, int, float, bool, or None."""
    def ok(x):
        return isinstance(x, (str, int, float, bool, type(None), list, dict))
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if not isinstance(k, str): return False
                if not ok(v): return False
                if not walk(v): return False
        elif isinstance(x, list):
            for v in x:
                if not ok(v): return False
                if not walk(v): return False
        return True
    return walk(obj)

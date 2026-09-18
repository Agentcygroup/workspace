"""Factory engine registry. Each engine exposes build(ctx) -> dict."""
__version__ = "0.1.0"
from .engine_scaffold import build as build_scaffold
from .engine_specs import build as build_specs
from .engine_engines import build as build_engines
from .engine_controller import build as build_controller
from .engine_tests import build as build_tests
from .engine_wire import build as build_wire

ENGINES = {
    "engine_scaffold": build_scaffold,
    "engine_specs": build_specs,
    "engine_engines": build_engines,
    "engine_controller": build_controller,
    "engine_tests": build_tests,
    "engine_wire": build_wire,
}

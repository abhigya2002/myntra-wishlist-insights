"""Load a helper module from another phase by file path.

Phases 1, 4, and 5 all define `config.py`, `ingest.py`, and `normalize.py`.
Putting another phase on `sys.path` makes `import normalize` resolve to
whichever directory happens to come first, so Phase 1's Reddit normaliser and
Phase 4's store normaliser shadow each other depending on import order.
Loading by explicit path removes the ordering question entirely.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load(alias: str, path: Path) -> ModuleType:
    if alias in sys.modules:
        return sys.modules[alias]
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {alias} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module

# scripts/validate_runtime.py

from __future__ import annotations

import sys
from pathlib import Path


def validate() -> None:
    project_root = Path(__file__).resolve().parents[1]
    project_root_text = str(project_root)

    if project_root_text not in sys.path:
        sys.path.insert(0, project_root_text)

    import app  # noqa: F401

    assert app is not None


if __name__ == "__main__":
    validate()
    print("Runtime validation passed")

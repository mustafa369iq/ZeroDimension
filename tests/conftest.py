"""
tests/conftest.py
====================
Ensures the `zerodimension` package is importable when running
pytest directly from the project root, without requiring an
editable install. (If the package IS installed via `pip install -e .`,
this has no effect — it's a convenience fallback.)
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

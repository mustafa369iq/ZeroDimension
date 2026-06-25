# Contributing

ZeroDimension is an experimental symbolic mathematics framework.

Before contributing:

1. Do not change mathematical behavior without documenting the axiom affected.
2. Add tests for every new rule or behavior.
3. Keep ordinary arithmetic unchanged unless a ZeroDimension transition is explicitly involved.
4. Do not silently allow cross-layer arithmetic.
5. Run tests before submitting changes:

```bash
pytest

New mathematical proposals should be documented first before implementation.

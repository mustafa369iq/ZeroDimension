"""
zerodimension.display
========================
Display utilities for the ZeroDimension V3 framework.

AXIOM F (Display rules) — the single source of truth for formatting
lives in theta._format_theta(); this module provides higher-level,
user-facing helpers built on top of it: a global debug-mode toggle,
pretty-printers, and string builders for layers/traces.
"""

from __future__ import annotations

from typing import Union, List

from .theta import ThetaValue, Gateway, _format_theta, _subscript, Number
from .operators import TransitionOperator


# ── Global debug mode ───────────────────────────────────────────────────────
#
# Normal display hides the layer:   Θ, 1Θ, -1Θ, 5Θ
# Debug display shows the layer:    Θ1, 1Θ1, 5Θ2   (rendered with subscripts)
#
# This is a convenience for the CLI / interactive shell. Library code
# should generally prefer calling `.debug()` explicitly rather than
# relying on this global flag, but the flag is provided because the
# spec explicitly asks for a debug "mode".

_debug_mode = {"enabled": False}


def set_debug_mode(enabled: bool) -> None:
    """Globally enable or disable debug-mode display (layer subscripts)."""
    _debug_mode["enabled"] = bool(enabled)


def is_debug_mode() -> bool:
    return _debug_mode["enabled"]


def render(value: Union[Number, ThetaValue, TransitionOperator]) -> str:
    """
    Render any ZeroDimension value (plain number, ThetaValue, Gateway,
    or TransitionOperator) as a string, honoring the global debug mode.
    """
    if isinstance(value, TransitionOperator):
        return value.debug() if is_debug_mode() else str(value)
    if isinstance(value, ThetaValue):
        return value.debug() if is_debug_mode() else str(value)
    return str(value)


def format_layer_label(layer: int) -> str:
    """Return a human-readable label for a layer, e.g. 'Layer 2'."""
    return f"Layer {layer}"


def format_trace(value: ThetaValue) -> str:
    """Render a ThetaValue's derivation trace as a multi-line string."""
    lines = [f"Trace for {value}:"]
    for i, step in enumerate(value.trace):
        prefix = "  ·" if i == 0 else "  →"
        lines.append(f"{prefix} {step}")
    return "\n".join(lines)


def show(value: Union[Number, ThetaValue, TransitionOperator]) -> None:
    """Pretty-print full diagnostics for any ZeroDimension value."""
    if isinstance(value, ThetaValue):
        value.show()
    elif isinstance(value, TransitionOperator):
        print(f"\n{'═'*46}")
        print(f"  TransitionOperator (0/0)")
        print(f"  This is NOT a number. Call it: T(x) to lift x one layer.")
        print(f"{'═'*46}\n")
    else:
        print(f"\n  {value}  (ordinary layer-0 number)\n")


def theta_table(values: List[Union[Number, ThetaValue]], labels: List[str] = None) -> None:
    """
    Print a small table summarizing a list of values: their display
    string, layer, state, and whether they're a gateway.
    """
    if labels is None:
        labels = [f"v{i}" for i in range(len(values))]
    max_label = max((len(l) for l in labels), default=1)

    header = f"  {'label':<{max_label}}  {'value':>10}  {'layer':>6}  {'state':>9}  gateway"
    print()
    print(header)
    print("  " + "─" * (len(header) - 2))
    for label, v in zip(labels, values):
        if isinstance(v, ThetaValue):
            print(f"  {label:<{max_label}}  {str(v):>10}  {v.layer:>6}  {v.state:>9}  {v.is_gateway}")
        else:
            print(f"  {label:<{max_label}}  {str(v):>10}  {'—':>6}  {'real':>9}  False")
    print()

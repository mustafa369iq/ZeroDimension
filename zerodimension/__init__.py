"""
ZeroDimension Framework V3
=============================
A symbolic mathematical framework for division by zero, built on a
layered Theta-space.

Core philosophy:
    - Ordinary mathematics is never modified.
    - Division by zero never crashes — it transitions into the next
      Theta layer instead.
    - Every ThetaValue carries a coefficient, a layer, and a state
      ("value" or "gateway"). Layer metadata is always preserved
      internally even when display hides it.

Quick start:
    from zerodimension import theta, zdiv, T, transition

    zdiv(5, 0)              # -> 5Θ   (layer 1, hidden in normal display)
    theta(5, layer=1) / theta(0, layer=1)   # -> 5Θ in layer 2 (gateway transition)
    T(5)                    # -> 5Θ   (TransitionOperator lifts 5 into layer 1)

See docs/AXIOMS_V3.md and docs/SPECIFICATION_V3.md for the full rule set.
"""

from .theta import (
    ThetaValue,
    Gateway,
    unify_layer,
)
from .operators import (
    TransitionOperator,
    T,
    transition,
    zdiv,
    zadd,
    zsub,
    zmul,
)
from .display import (
    set_debug_mode,
    is_debug_mode,
    render,
    show,
    theta_table,
    format_layer_label,
    format_trace,
)
from .solver import (
    solve_zero_division_equation,
    solve_equation_string,
)
from .exceptions import (
    ZeroDimensionError,
    CrossLayerOperationError,
    TransitionOperatorMisuseError,
    InvalidLayerError,
    GatewayDivisionError,
    SolverError,
)


def theta(coefficient=0, layer: int = 1) -> ThetaValue:
    """
    Convenience constructor for a ThetaValue.

    CORE AXIOM: theta() with no coefficient (or coefficient=0) returns
    the Gateway of the given layer — Θ — NOT 1Θ. The coefficient is
    purely a numeric attachment to the fixed symbol Θ.

    Examples:
        theta()             -> Θ     (Gateway of layer 1)
        theta(0)             -> Θ
        theta(1)              -> 1Θ
        theta(5)               -> 5Θ
        theta(5, layer=2)       -> 5Θ   (layer 2 internally; debug() shows 5Θ₂)
    """
    return ThetaValue(coefficient=coefficient, layer=layer)


__version__ = "3.0.0"
__author__ = "ZeroDimension Framework"

__all__ = [
    # Core objects
    "ThetaValue",
    "Gateway",
    "theta",
    "unify_layer",
    # Transition operator
    "TransitionOperator",
    "T",
    "transition",
    # Safe arithmetic
    "zdiv",
    "zadd",
    "zsub",
    "zmul",
    # Display
    "set_debug_mode",
    "is_debug_mode",
    "render",
    "show",
    "theta_table",
    "format_layer_label",
    "format_trace",
    # Solver
    "solve_zero_division_equation",
    "solve_equation_string",
    # Exceptions
    "ZeroDimensionError",
    "CrossLayerOperationError",
    "TransitionOperatorMisuseError",
    "InvalidLayerError",
    "GatewayDivisionError",
    "SolverError",
]

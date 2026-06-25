"""
zerodimension.exceptions
==========================
Custom exception hierarchy for the ZeroDimension V3 framework.

AXIOM (Core Philosophy): "Do not silently allow invalid operations."
Every operation that would violate a framework axiom must raise a
clear, specific exception rather than guessing, coercing, or
returning a misleading value.
"""

from __future__ import annotations


class ZeroDimensionError(Exception):
    """Base class for all ZeroDimension framework errors."""


class CrossLayerOperationError(ZeroDimensionError):
    """
    Raised when arithmetic is attempted directly between ThetaValues
    that live on different layers without explicit unification.

    AXIOM B (Cross-layer arithmetic):
        Direct arithmetic between different layers is not allowed.
        Example: 5Θ1 + 3Θ2 is invalid unless explicitly unified first.
    """

    def __init__(self, layer_a: int, layer_b: int, operation: str = "operation"):
        self.layer_a = layer_a
        self.layer_b = layer_b
        self.operation = operation
        super().__init__(
            f"Cross-layer {operation} is not allowed: "
            f"layer {layer_a} vs layer {layer_b}. "
            f"Use unify_layer(...) or transition(...) to align layers first."
        )


class TransitionOperatorMisuseError(ZeroDimensionError):
    """
    Raised when the TransitionOperator (0/0, 'T') is used as if it
    were an ordinary number.

    AXIOM D (TransitionOperator 0/0):
        0/0 is not a number. It is a unification/transition operator.
        It must never be silently treated as 0, 1, or any other scalar.
    """


class InvalidLayerError(ZeroDimensionError):
    """Raised when a layer index is invalid (e.g. negative)."""

    def __init__(self, layer):
        self.layer = layer
        super().__init__(
            f"Invalid layer: {layer!r}. Layers must be integers >= 0."
        )


class GatewayDivisionError(ZeroDimensionError):
    """
    Raised when an operation on a Gateway is attempted that the
    framework does not define (e.g. dividing a Gateway by itself
    using ordinary division instead of the transition rule).
    """


class SolverError(ZeroDimensionError):
    """Raised when solve_zero_division_equation cannot solve or parse
    the given equation under the framework's axioms."""

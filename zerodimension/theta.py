"""
zerodimension.theta
=====================
Core symbolic objects for the ZeroDimension V3 framework: ThetaValue
and Gateway.

CORE PHILOSOPHY (do not violate):
  - Ordinary mathematics is never modified. Arithmetic on plain
    Python numbers (layer 0, "real space") behaves exactly as usual.
  - Division by zero never crashes. It produces a ThetaValue in the
    NEXT layer instead of raising ZeroDivisionError or returning inf/nan.
  - Every ThetaValue carries three pieces of information:
        coefficient : numeric (or symbolic) value attached to Theta
        layer       : which Theta-layer this value lives in (>= 1)
        state       : "value" (an ordinary Theta value) or
                      "gateway" (the zero-coefficient gateway of a layer)
  - Layer metadata is part of the object's identity even when display
    hides it. Two ThetaValues with equal coefficients but different
    layers are NOT the same value (see CrossLayerOperationError).

NOTATION:
    aΘₙ   = ThetaValue(coefficient=a, layer=n)
    Θₙ    = Gateway(layer=n)              == ThetaValue(0, n, "gateway")
    Θ     = Gateway(layer=1)  (shorthand, layer defaults to 1)

DISPLAY AXIOM (Section F — must hold everywhere, no exceptions):
    coefficient == 0  -> "Θ"      (never "0Θ")
    coefficient == 1  -> "1Θ"     (never bare "Θ")
    coefficient == -1 -> "-1Θ"    (never "-Θ")
    coefficient == n  -> "nΘ"
    Debug mode additionally appends the layer as a subscript: Θ₂, 5Θ₃, 1Θ₁.
"""

from __future__ import annotations

from typing import Union, Optional

from .exceptions import (
    CrossLayerOperationError,
    InvalidLayerError,
)

Number = Union[int, float]

# Unicode subscript digits 0-9, used for debug-mode layer display (Θ₂, 5Θ₃, ...)
_SUBSCRIPT_DIGITS = str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋")


def _subscript(n: int) -> str:
    """Render an integer using unicode subscript digits, e.g. 12 -> '₁₂'."""
    return str(n).translate(_SUBSCRIPT_DIGITS)


def _is_thetaish(x) -> bool:
    return isinstance(x, ThetaValue)


class ThetaValue:
    """
    A symbolic value living in Theta-space layer `layer`.

    Attributes
    ----------
    coefficient : int | float | sympy expression
        The numeric (or symbolic) coefficient attached to Theta.
    layer : int
        Which Theta-layer this value belongs to. Must be >= 1 for any
        value actually "in" Theta-space. (Layer 0 is ordinary real
        space and is represented by plain Python numbers, not by
        ThetaValue — see module docstring.)
    state : str
        Either "value" (an ordinary coefficient*Θ term) or "gateway"
        (the zero-coefficient gateway of this layer, i.e. coefficient
        is exactly 0 AND this value was constructed/derived as the
        layer's gateway). A "value" ThetaValue with coefficient 0 that
        arose from cancellation (e.g. 5Θ - 5Θ) is automatically
        normalized to state="gateway" — see AXIOM A.
    """

    __slots__ = ("coefficient", "layer", "state", "_trace")

    def __init__(
        self,
        coefficient: Number = 0,
        layer: int = 1,
        state: str = "value",
        _trace: Optional[list] = None,
    ):
        if not isinstance(layer, int) or layer < 1:
            raise InvalidLayerError(layer)
        if state not in ("value", "gateway"):
            raise ValueError(f"state must be 'value' or 'gateway', got {state!r}")

        self.coefficient = coefficient
        self.layer = layer

        # AXIOM A (tail): "if coefficient becomes 0, display as Θ but
        # preserve layer internally". A coefficient of exactly 0 is
        # ALWAYS the gateway state — there is no other valid state for
        # coefficient 0, by definition of the Gateway.
        if _coeff_is_zero(coefficient):
            self.state = "gateway"
        else:
            self.state = state

        self._trace = _trace if _trace is not None else [self._self_repr()]

    # ── internal helpers ─────────────────────────────────────────────

    def _self_repr(self) -> str:
        return repr(self)

    def _check_same_layer(self, other: "ThetaValue", op: str) -> None:
        if self.layer != other.layer:
            raise CrossLayerOperationError(self.layer, other.layer, operation=op)

    def _with(self, coefficient, layer=None, state="value", trace_event: str = "") -> "ThetaValue":
        new = ThetaValue(
            coefficient=coefficient,
            layer=layer if layer is not None else self.layer,
            state=state,
            _trace=self._trace + ([trace_event] if trace_event else []),
        )
        return new

    # ── identity / inspection ───────────────────────────────────────

    @property
    def is_gateway(self) -> bool:
        """True if this value is the Gateway (coefficient 0) of its layer."""
        return self.state == "gateway"

    @property
    def trace(self) -> list:
        """Read-only view of this value's derivation history."""
        return list(self._trace)

    def to_gateway(self) -> "Gateway":
        """Return the Gateway object for this value's layer."""
        return Gateway(layer=self.layer)

    # ── display ──────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return _format_theta(self.coefficient, self.layer, debug=False)

    def __str__(self) -> str:
        return self.__repr__()

    def debug(self) -> str:
        """Return the debug-mode string, with the layer shown as a subscript."""
        return _format_theta(self.coefficient, self.layer, debug=True)

    def show(self) -> None:
        """Pretty-print full diagnostics for this value."""
        print(f"\n{'═'*46}")
        print(f"  Value        : {self}")
        print(f"  Debug form   : {self.debug()}")
        print(f"  Coefficient  : {self.coefficient}")
        print(f"  Layer        : {self.layer}")
        print(f"  State        : {self.state}")
        print(f"  Is gateway   : {self.is_gateway}")
        print(f"  Trace        :")
        for step in self._trace:
            print(f"    → {step}")
        print(f"{'═'*46}\n")

    # ── AXIOM A: same-layer arithmetic ──────────────────────────────

    def __add__(self, other):
        if _is_thetaish(other):
            self._check_same_layer(other, "addition")
            new_c = self.coefficient + other.coefficient
            return self._with(new_c, trace_event=f"{self} + {other} = {_format_theta(new_c, self.layer)}")
        # ThetaValue + plain number is undefined in this framework:
        # ordinary numbers live in layer 0 and Theta values live in
        # layer >= 1; mixing them directly is a cross-layer operation.
        raise CrossLayerOperationError(self.layer, 0, operation="addition")

    def __radd__(self, other):
        raise CrossLayerOperationError(0, self.layer, operation="addition")

    def __sub__(self, other):
        if _is_thetaish(other):
            self._check_same_layer(other, "subtraction")
            new_c = self.coefficient - other.coefficient
            return self._with(new_c, trace_event=f"{self} - {other} = {_format_theta(new_c, self.layer)}")
        raise CrossLayerOperationError(self.layer, 0, operation="subtraction")

    def __rsub__(self, other):
        raise CrossLayerOperationError(0, self.layer, operation="subtraction")

    def __mul__(self, other):
        if _is_thetaish(other):
            self._check_same_layer(other, "multiplication")
            new_c = self.coefficient * other.coefficient
            return self._with(new_c, trace_event=f"{self} * {other} = {_format_theta(new_c, self.layer)}")
        # Scalar multiplication by a plain number is allowed: it scales
        # the coefficient without changing layer (e.g. 5Θ1 * 3 = 15Θ1).
        # This does not violate cross-layer arithmetic because a plain
        # scalar has no layer of its own to conflict with.
        new_c = self.coefficient * other
        return self._with(new_c, trace_event=f"{self} * {other} = {_format_theta(new_c, self.layer)}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if _is_thetaish(other):
            # AXIOM C: division by the gateway of the SAME layer is a
            # transition — it moves the result to the next layer.
            if other.is_gateway and other.layer == self.layer:
                return self._gateway_transition()
            self._check_same_layer(other, "division")
            if _coeff_is_zero(other.coefficient):
                # Should be unreachable (is_gateway covers coefficient==0),
                # but guard explicitly for safety/clarity.
                return self._gateway_transition()
            new_c = self.coefficient / other.coefficient
            return self._with(new_c, trace_event=f"{self} / {other} = {_format_theta(new_c, self.layer)}")
        # Scalar division by a plain nonzero number: scales coefficient.
        if other == 0:
            # Dividing a Theta value by ordinary zero is itself a
            # gateway-style transition relative to ITS layer's gateway,
            # per the spirit of Axiom C generalized: dividing by "the
            # zero of the layer below" still lifts forward.
            return self._gateway_transition()
        new_c = self.coefficient / other
        return self._with(new_c, trace_event=f"{self} / {other} = {_format_theta(new_c, self.layer)}")

    def __rtruediv__(self, other):
        # other / ThetaValue: only defined when `self` is this layer's
        # gateway (the general a/0-style transition rule); otherwise
        # this is an undefined cross-layer scalar/Theta mix.
        if self.is_gateway:
            # a / Θₙ = aΘₙ₊₁  (a generalized form of Axiom C)
            return ThetaValue(
                coefficient=other,
                layer=self.layer + 1,
                state="value",
                _trace=self._trace + [f"{other} / {self} = {_format_theta(other, self.layer+1)}"],
            )
        raise CrossLayerOperationError(0, self.layer, operation="division")

    def _gateway_transition(self) -> "ThetaValue":
        """
        AXIOM C — Gateway transition:
            aΘₙ / Θₙ = aΘₙ₊₁
            0Θₙ / Θₙ = Θₙ₊₁   (coefficient 0 stays the gateway, one layer up)
        """
        new_layer = self.layer + 1
        result = ThetaValue(
            coefficient=self.coefficient,
            layer=new_layer,
            state="value",
            _trace=self._trace + [
                f"{self} / Θ{_subscript(self.layer)} "
                f"→ transition → {_format_theta(self.coefficient, new_layer)}"
            ],
        )
        return result

    # ── powers, negation, abs ────────────────────────────────────────

    def __pow__(self, exponent):
        # (nΘₖ)^m = (n^m)Θₖ — coefficient is exponentiated, layer fixed.
        new_c = self.coefficient ** exponent
        return self._with(new_c, trace_event=f"({self})^{exponent} = {_format_theta(new_c, self.layer)}")

    def __neg__(self):
        new_c = -self.coefficient
        return self._with(new_c, trace_event=f"-({self}) = {_format_theta(new_c, self.layer)}")

    def __abs__(self):
        new_c = abs(self.coefficient)
        return self._with(new_c, trace_event=f"|{self}| = {_format_theta(new_c, self.layer)}")

    # ── AXIOM E: equality ────────────────────────────────────────────

    def __eq__(self, other) -> bool:
        """
        AXIOM E: aΘₙ == bΘₙ iff a == b. Comparing across layers raises
        CrossLayerOperationError rather than silently returning False,
        because layer mismatch is a meaningful error condition the
        framework wants surfaced — use equals_after_unify() if you
        want a cross-layer comparison.
        """
        if _is_thetaish(other):
            if self.layer != other.layer:
                raise CrossLayerOperationError(self.layer, other.layer, operation="equality")
            return self.coefficient == other.coefficient and self.state == other.state
        # A ThetaValue (layer >= 1) is never equal to a plain real
        # number (layer 0) — they live in different layers.
        return False

    def __hash__(self):
        return hash((self.coefficient, self.layer, self.state))

    def equals_after_unify(self, other: "ThetaValue") -> bool:
        """
        Lift both operands to the higher of the two layers, then
        compare coefficients. This is the explicit, opt-in way to
        compare values across layers (see AXIOM E).
        """
        if not _is_thetaish(other):
            return False
        target = max(self.layer, other.layer)
        a = unify_layer(self, target)
        b = unify_layer(other, target)
        return a.coefficient == b.coefficient


class Gateway(ThetaValue):
    """
    The Gateway of a layer: ThetaValue(coefficient=0, layer=n, state="gateway").

    The Gateway represents the "zero of Theta-space" for a given layer
    — the entry point through which ordinary division-by-zero (or
    coefficient cancellation) arrives, and the value whose use as a
    divisor triggers a layer transition (AXIOM C).
    """

    __slots__ = ()

    def __init__(self, layer: int = 1, _trace: Optional[list] = None):
        super().__init__(coefficient=0, layer=layer, state="gateway", _trace=_trace)

    def __repr__(self) -> str:
        return _format_theta(0, self.layer, debug=False)


# ── module-level formatting helper (AXIOM F) ──────────────────────────────

def _coeff_is_zero(c) -> bool:
    try:
        return c == 0
    except Exception:
        return False


def _format_theta(coefficient, layer: int, debug: bool = False) -> str:
    """
    AXIOM F — Display rules. This is the single source of truth for
    how every ThetaValue / Gateway renders, used by both __repr__ and
    debug(). No other code path should hand-roll Theta formatting.

        coefficient == 0  -> "Θ"      (never "0Θ")
        coefficient == 1  -> "1Θ"     (never bare "Θ")
        coefficient == -1 -> "-1Θ"    (never "-Θ")
        coefficient == n  -> "nΘ"

    debug=True appends the layer as a unicode subscript: Θ₂, 5Θ₃, 1Θ₁.
    """
    if _coeff_is_zero(coefficient):
        base = "Θ"
    else:
        # Render ints without a trailing ".0"; leave floats/symbolic as-is.
        if isinstance(coefficient, float) and coefficient == int(coefficient):
            c_str = str(int(coefficient))
        else:
            c_str = str(coefficient)
        base = f"{c_str}Θ"

    if debug:
        return base + _subscript(layer)
    return base


# ── layer unification helpers ──────────────────────────────────────────────

def unify_layer(value: "ThetaValue", target_layer: int) -> "ThetaValue":
    """
    Lift (or validate) a ThetaValue to `target_layer` by repeatedly
    applying the gateway transition (AXIOM C) until it reaches the
    target layer. The transition is one-way by default (no automatic
    return / lowering), so target_layer must be >= value.layer.

    Examples:
        unify_layer(theta(5, layer=1), 2)   -> 5Θ2
        unify_layer(theta(5, layer=2), 2)   -> 5Θ2  (no-op)
    """
    if not isinstance(target_layer, int) or target_layer < 1:
        raise InvalidLayerError(target_layer)
    if target_layer < value.layer:
        raise CrossLayerOperationError(
            value.layer, target_layer,
            operation="unify_layer (cannot lower a layer; transition is one-way)",
        )
    current = value
    while current.layer < target_layer:
        # Lifting via the gateway transition rule: divide by this
        # layer's own gateway (coefficient unchanged, layer + 1).
        current = current._gateway_transition()
    return current

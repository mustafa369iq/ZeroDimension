"""
zerodimension.operators
==========================
TransitionOperator (the symbolic meaning of 0/0) and the safe
arithmetic helper functions: zdiv, zadd, zsub, zmul, transition.

AXIOM D (TransitionOperator 0/0):
    0/0 is NOT a number. It is a unification / transition operator.
    It is never equal to 0, never equal to 1, and must never be
    silently coerced into either.

    T = TransitionOperator()
    T(a)          = aΘ1        if a is an ordinary (layer-0) number
    T(aΘn)        = aΘ(n+1)
    T(0)          = Θ1
    T(Θn gateway) = Θ(n+1)
"""

from __future__ import annotations

from typing import Union

from .theta import ThetaValue, Gateway, unify_layer, _is_thetaish, Number
from .exceptions import TransitionOperatorMisuseError, CrossLayerOperationError


class TransitionOperator:
    """
    The symbolic operator representing 0/0.

    AXIOM D: T is not a number. Arithmetic operators on T (other than
    calling it, i.e. T(x)) raise TransitionOperatorMisuseError so that
    code can never accidentally treat T as 0 or 1.

    Usage:
        T = TransitionOperator()
        T(5)            # -> 5Θ1   (lifts an ordinary number into layer 1)
        T(theta(5, 1))  # -> 5Θ2   (lifts a Theta value one layer up)
        T(0)            # -> Θ1    (the gateway of layer 1)
    """

    __slots__ = ()

    def __call__(self, value: Union[Number, ThetaValue]) -> ThetaValue:
        """
        Apply the transition operator to `value`, lifting it one layer.

            T(a)    = aΘ1        for ordinary numbers a (including a=0)
            T(aΘn)  = aΘ(n+1)    for any Theta value, gateway or not
        """
        if _is_thetaish(value):
            return value._gateway_transition()
        # Ordinary (layer-0) number -> lift into layer 1.
        return ThetaValue(
            coefficient=value,
            layer=1,
            state="value",
            _trace=[f"T({value}) = {value}Θ1"],
        )

    # ── AXIOM D: T is not a number — block arithmetic misuse ────────

    def _refuse(self, *_args, **_kwargs):
        raise TransitionOperatorMisuseError(
            "TransitionOperator (0/0) is not a number. It cannot be "
            "added, subtracted, multiplied, divided, or compared with "
            "==. Call it instead: T(value) lifts value one Theta layer."
        )

    __add__ = __radd__ = _refuse
    __sub__ = __rsub__ = _refuse
    __mul__ = __rmul__ = _refuse
    __truediv__ = __rtruediv__ = _refuse
    __pow__ = __rpow__ = _refuse

    def __eq__(self, other):
        # T is never equal to 0, 1, or any other value — including
        # another TransitionOperator instance compared as a number.
        # We DO allow T == T (identity-style) so code can sanity-check
        # "is this the transition operator", but T == 0 / T == 1 are
        # always False rather than raising, since equality checks are
        # common and shouldn't crash exploratory code; arithmetic does.
        return isinstance(other, TransitionOperator)

    def __hash__(self):
        return hash("TransitionOperator")

    def __repr__(self) -> str:
        return "0/0"

    def __str__(self) -> str:
        return "0/0"

    def debug(self) -> str:
        return "T"


# Module-level convenience instance.
T = TransitionOperator()


# ══════════════════════════════════════════════════════════════════
# Safe arithmetic helpers (Section G)
# ══════════════════════════════════════════════════════════════════

def zdiv(a: Union[Number, ThetaValue], b: Union[Number, ThetaValue]) -> Union[Number, ThetaValue]:
    """
    Safe division. Never raises ZeroDivisionError.

    Ordinary math is preserved: zdiv(a, b) with b != 0 behaves exactly
    like a / b for plain numbers (AXIOM: "Do not modify ordinary
    mathematics").

    Division by zero creates a Theta-state in the next layer:
        zdiv(a, 0)  -> aΘ1     (a != 0)
        zdiv(0, 0)  -> Θ1      (the gateway of layer 1 — this IS the
                                 TransitionOperator's target state, but
                                 zdiv returns the ThetaValue directly
                                 rather than the operator itself, since
                                 the caller asked for a value, not a
                                 symbolic operator)

    For two ThetaValues, the same-layer arithmetic / gateway-transition
    rules (AXIOM A / C) apply automatically via ThetaValue.__truediv__.
    """
    if _is_thetaish(a) or _is_thetaish(b):
        a_val = a if _is_thetaish(a) else a  # plain numbers pass through to __rtruediv__/__truediv__
        if _is_thetaish(a) and _is_thetaish(b):
            return a / b
        if _is_thetaish(b) and not _is_thetaish(a):
            # a (plain) / bΘn — only defined if b is the gateway
            return a / b
        # a is ThetaValue, b is plain
        return a / b

    if b == 0:
        return T(a)  # ordinary a/0 -> aΘ1 (or Θ1 if a == 0)
    return a / b


def zadd(a: Union[Number, ThetaValue], b: Union[Number, ThetaValue]) -> Union[Number, ThetaValue]:
    """
    Safe addition. Ordinary math preserved for plain numbers.
    For ThetaValues, enforces same-layer arithmetic (AXIOM A) and
    raises CrossLayerOperationError on mismatched layers (AXIOM B).
    """
    if _is_thetaish(a) or _is_thetaish(b):
        if _is_thetaish(a) and _is_thetaish(b):
            return a + b
        # Mixing a plain number with a ThetaValue is a cross-layer op.
        layer_a = a.layer if _is_thetaish(a) else 0
        layer_b = b.layer if _is_thetaish(b) else 0
        raise CrossLayerOperationError(layer_a, layer_b, operation="addition")
    return a + b


def zsub(a: Union[Number, ThetaValue], b: Union[Number, ThetaValue]) -> Union[Number, ThetaValue]:
    """Safe subtraction — see zadd for the cross-layer rules."""
    if _is_thetaish(a) or _is_thetaish(b):
        if _is_thetaish(a) and _is_thetaish(b):
            return a - b
        layer_a = a.layer if _is_thetaish(a) else 0
        layer_b = b.layer if _is_thetaish(b) else 0
        raise CrossLayerOperationError(layer_a, layer_b, operation="subtraction")
    return a - b


def zmul(a: Union[Number, ThetaValue], b: Union[Number, ThetaValue]) -> Union[Number, ThetaValue]:
    """
    Safe multiplication. ThetaValue * ThetaValue requires the same
    layer (AXIOM A). ThetaValue * plain-number is scalar scaling and
    is always allowed (it doesn't introduce a layer conflict).
    """
    if _is_thetaish(a) or _is_thetaish(b):
        if _is_thetaish(a) and _is_thetaish(b):
            return a * b
        if _is_thetaish(a):
            return a * b   # scalar scaling, allowed
        return b * a       # scalar scaling, allowed (commutative)
    return a * b


def transition(value: Union[Number, ThetaValue]) -> ThetaValue:
    """
    Functional alias for T(value) — lifts `value` one Theta layer.
    Provided as a plain function for ergonomics (Section G requires
    both T as an operator object and `transition` as a function).
    """
    return T(value)

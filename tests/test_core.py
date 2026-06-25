"""
tests/test_core.py
=====================
Tests for AXIOM A (same-layer arithmetic), AXIOM C (gateway
transition), AXIOM E (equality), and basic ThetaValue construction.
"""

import pytest

from zerodimension import (
    theta,
    ThetaValue,
    Gateway,
    zdiv,
    zadd,
    zsub,
    zmul,
    unify_layer,
    CrossLayerOperationError,
    InvalidLayerError,
)


# ── Construction ─────────────────────────────────────────────────────────────

def test_default_layer_is_1():
    assert theta(5).layer == 1


def test_invalid_layer_raises():
    with pytest.raises(InvalidLayerError):
        ThetaValue(coefficient=5, layer=0)
    with pytest.raises(InvalidLayerError):
        ThetaValue(coefficient=5, layer=-1)


def test_coefficient_zero_is_always_gateway_state():
    v = ThetaValue(coefficient=0, layer=1, state="value")
    assert v.state == "gateway"
    assert v.is_gateway


def test_gateway_class_is_zero_coefficient():
    g = Gateway(layer=3)
    assert g.coefficient == 0
    assert g.layer == 3
    assert g.is_gateway


# ── AXIOM A: same-layer arithmetic ────────────────────────────────────────────

def test_same_layer_addition():
    a, b = theta(5, layer=1), theta(3, layer=1)
    result = a + b
    assert result.coefficient == 8
    assert result.layer == 1


def test_same_layer_subtraction():
    a, b = theta(10, layer=2), theta(6, layer=2)
    result = a - b
    assert result.coefficient == 4
    assert result.layer == 2


def test_same_layer_multiplication():
    a, b = theta(5, layer=1), theta(3, layer=1)
    result = a * b
    assert result.coefficient == 15
    assert result.layer == 1


def test_same_layer_division():
    a, b = theta(10, layer=1), theta(2, layer=1)
    result = a / b
    assert result.coefficient == 5
    assert result.layer == 1


def test_cancellation_preserves_layer_as_gateway():
    """aΘn - aΘn = Θn  (coefficient 0, but layer preserved internally)."""
    a = theta(5, layer=3)
    result = a - a
    assert result.coefficient == 0
    assert result.layer == 3
    assert result.is_gateway
    assert str(result) == "Θ"
    assert result.debug() == "Θ₃"


def test_scalar_multiplication_allowed():
    """ThetaValue * plain number scales the coefficient, same layer."""
    a = theta(5, layer=2)
    result = a * 3
    assert result.coefficient == 15
    assert result.layer == 2

    result2 = 3 * a
    assert result2.coefficient == 15


# ── AXIOM B: cross-layer arithmetic forbidden ─────────────────────────────────

def test_cross_layer_addition_raises():
    with pytest.raises(CrossLayerOperationError):
        theta(5, layer=1) + theta(3, layer=2)


def test_cross_layer_subtraction_raises():
    with pytest.raises(CrossLayerOperationError):
        theta(5, layer=1) - theta(3, layer=2)


def test_cross_layer_multiplication_raises():
    with pytest.raises(CrossLayerOperationError):
        theta(5, layer=1) * theta(3, layer=2)


def test_cross_layer_division_raises():
    with pytest.raises(CrossLayerOperationError):
        theta(5, layer=1) / theta(3, layer=2)


def test_theta_plus_plain_number_raises():
    """Plain numbers (layer 0) cannot be mixed directly with ThetaValue."""
    with pytest.raises(CrossLayerOperationError):
        theta(5, layer=1) + 3
    with pytest.raises(CrossLayerOperationError):
        3 + theta(5, layer=1)


# ── AXIOM C: gateway transition ───────────────────────────────────────────────

def test_division_by_same_layer_gateway_transitions():
    v = theta(5, layer=1)
    g = Gateway(layer=1)
    result = v / g
    assert result.coefficient == 5
    assert result.layer == 2


def test_zero_coefficient_over_gateway_stays_gateway_next_layer():
    """0Θn / Θn = Θ(n+1)"""
    v = theta(0, layer=1)  # this IS the gateway
    g = Gateway(layer=1)
    result = v / g
    assert result.coefficient == 0
    assert result.layer == 2
    assert result.is_gateway


def test_real_division_by_zero_goes_to_layer_1():
    """a / 0 = aΘ1  (from ordinary, layer-0 real space)."""
    result = zdiv(5, 0)
    assert isinstance(result, ThetaValue)
    assert result.coefficient == 5
    assert result.layer == 1


def test_zero_over_zero_is_gateway_of_layer_1():
    result = zdiv(0, 0)
    assert isinstance(result, ThetaValue)
    assert result.coefficient == 0
    assert result.layer == 1
    assert result.is_gateway


def test_ordinary_nonzero_division_unaffected():
    """Ordinary math must remain valid — zdiv behaves like / when b != 0."""
    assert zdiv(10, 2) == 5
    assert zdiv(7, 2) == 3.5


def test_transition_is_one_way_no_auto_return():
    """There is no method that lowers a layer automatically."""
    v = theta(5, layer=2)
    assert not hasattr(v, "lower_layer")
    assert not hasattr(v, "untransition")


# ── AXIOM E: equality ─────────────────────────────────────────────────────────

def test_equality_same_layer():
    assert theta(5, layer=1) == theta(5, layer=1)
    assert theta(5, layer=1) != theta(3, layer=1)


def test_equality_cross_layer_raises():
    with pytest.raises(CrossLayerOperationError):
        theta(5, layer=1) == theta(5, layer=2)


def test_equals_after_unify():
    a = theta(5, layer=1)
    b = theta(5, layer=2)
    assert a.equals_after_unify(b)

    c = theta(5, layer=1)
    d = theta(3, layer=2)
    assert not c.equals_after_unify(d)


def test_theta_value_never_equals_plain_number():
    assert (theta(5, layer=1) == 5) is False


# ── zadd / zsub / zmul safe helpers ───────────────────────────────────────────

def test_zadd_same_layer():
    result = zadd(theta(2, layer=1), theta(3, layer=1))
    assert result.coefficient == 5


def test_zadd_cross_layer_raises():
    with pytest.raises(CrossLayerOperationError):
        zadd(theta(2, layer=1), theta(3, layer=2))


def test_zsub_same_layer():
    result = zsub(theta(5, layer=1), theta(2, layer=1))
    assert result.coefficient == 3


def test_zmul_scalar():
    result = zmul(theta(5, layer=1), 3)
    assert result.coefficient == 15


def test_zmul_plain_numbers_unaffected():
    assert zmul(4, 5) == 20


# ── unify_layer ────────────────────────────────────────────────────────────

def test_unify_layer_lifts_correctly():
    v = theta(5, layer=1)
    lifted = unify_layer(v, 3)
    assert lifted.layer == 3
    assert lifted.coefficient == 5


def test_unify_layer_noop_when_already_at_target():
    v = theta(5, layer=2)
    same = unify_layer(v, 2)
    assert same.layer == 2
    assert same.coefficient == 5


def test_unify_layer_cannot_lower():
    v = theta(5, layer=3)
    with pytest.raises(CrossLayerOperationError):
        unify_layer(v, 1)

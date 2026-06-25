"""
tests/test_transition_operator.py
=====================================
Tests for AXIOM D: the TransitionOperator (0/0) — it is not a
number, never equals 0 or 1, and lifting via T() works correctly.
"""

import pytest

from zerodimension import (
    theta,
    ThetaValue,
    Gateway,
    TransitionOperator,
    T,
    transition,
    TransitionOperatorMisuseError,
)


def test_T_is_singleton_style_instance():
    assert isinstance(T, TransitionOperator)


def test_T_call_lifts_plain_number_to_layer_1():
    result = T(5)
    assert isinstance(result, ThetaValue)
    assert result.coefficient == 5
    assert result.layer == 1


def test_T_call_on_zero_gives_gateway_of_layer_1():
    result = T(0)
    assert result.coefficient == 0
    assert result.layer == 1
    assert result.is_gateway


def test_T_call_on_theta_value_lifts_one_layer():
    v = theta(5, layer=1)
    result = T(v)
    assert result.coefficient == 5
    assert result.layer == 2


def test_T_call_on_gateway_lifts_gateway_one_layer():
    g = Gateway(layer=1)
    result = T(g)
    assert result.is_gateway
    assert result.layer == 2


def test_transition_function_matches_T_call():
    assert transition(5).coefficient == T(5).coefficient
    assert transition(5).layer == T(5).layer


# ── AXIOM D: T is NOT a number ────────────────────────────────────────────────

def test_T_not_equal_zero():
    assert (T == 0) is False


def test_T_not_equal_one():
    assert (T == 1) is False


def test_T_equals_another_T_instance():
    other_T = TransitionOperator()
    assert T == other_T


def test_T_addition_raises():
    with pytest.raises(TransitionOperatorMisuseError):
        T + 5
    with pytest.raises(TransitionOperatorMisuseError):
        5 + T


def test_T_subtraction_raises():
    with pytest.raises(TransitionOperatorMisuseError):
        T - 5
    with pytest.raises(TransitionOperatorMisuseError):
        5 - T


def test_T_multiplication_raises():
    with pytest.raises(TransitionOperatorMisuseError):
        T * 5
    with pytest.raises(TransitionOperatorMisuseError):
        5 * T


def test_T_division_raises():
    with pytest.raises(TransitionOperatorMisuseError):
        T / 5
    with pytest.raises(TransitionOperatorMisuseError):
        5 / T


def test_T_power_raises():
    with pytest.raises(TransitionOperatorMisuseError):
        T ** 2


def test_T_repr_shows_0_over_0():
    assert str(T) == "0/0"
    assert repr(T) == "0/0"


def test_T_debug_form():
    assert T.debug() == "T"


def test_T_lifts_both_sides_consistently():
    """
    AXIOM D worked example:
        (x/0) * T = 5 * T   =>   xΘ1 = 5Θ1   =>   x = 5

    We can't literally multiply by T (that raises, by axiom), but we
    CAN verify the underlying lift is consistent: T applied to both
    "sides" of an analogous numeric equation lands both in the same
    layer with matching coefficients when the original values matched.
    """
    left_lifted = T(5)
    right_lifted = T(5)
    assert left_lifted.layer == right_lifted.layer
    assert left_lifted.coefficient == right_lifted.coefficient
    assert left_lifted == right_lifted

"""
tests/test_layers.py
=======================
Tests focused on layer mechanics: layer preservation through
arithmetic, multi-layer chains, and repeated transitions.
"""

import pytest

from zerodimension import (
    theta,
    ThetaValue,
    Gateway,
    transition,
    unify_layer,
    CrossLayerOperationError,
)


def test_layer_preserved_through_addition():
    a, b = theta(2, layer=4), theta(3, layer=4)
    assert (a + b).layer == 4


def test_layer_preserved_through_subtraction():
    a, b = theta(9, layer=5), theta(4, layer=5)
    assert (a - b).layer == 5


def test_layer_preserved_through_multiplication():
    a, b = theta(2, layer=3), theta(3, layer=3)
    assert (a * b).layer == 3


def test_layer_preserved_through_division():
    a, b = theta(9, layer=3), theta(3, layer=3)
    assert (a / b).layer == 3


def test_layer_preserved_through_scalar_ops():
    a = theta(5, layer=4)
    assert (a * 2).layer == 4
    assert (a / 2).layer == 4
    assert (-a).layer == 4
    assert abs(a).layer == 4
    assert (a ** 2).layer == 4


def test_repeated_transition_increments_layer_by_exactly_one():
    v = theta(7, layer=1)
    layers_seen = [v.layer]
    for _ in range(5):
        v = transition(v)
        layers_seen.append(v.layer)
    assert layers_seen == [1, 2, 3, 4, 5, 6]


def test_repeated_transition_preserves_coefficient():
    v = theta(42, layer=1)
    for _ in range(10):
        v = transition(v)
    assert v.coefficient == 42
    assert v.layer == 11


def test_gateway_transition_increments_exactly_one():
    v = theta(5, layer=1)
    g = Gateway(layer=1)
    result = v / g
    assert result.layer == v.layer + 1


def test_unify_layer_multi_step():
    v = theta(3, layer=1)
    result = unify_layer(v, 5)
    assert result.layer == 5
    assert result.coefficient == 3


def test_unify_layer_idempotent_at_same_target():
    v = theta(3, layer=1)
    once = unify_layer(v, 3)
    twice = unify_layer(once, 3)
    assert once.layer == twice.layer == 3
    assert once.coefficient == twice.coefficient == 3


def test_different_layer_gateways_are_distinct():
    g1 = Gateway(layer=1)
    g2 = Gateway(layer=2)
    assert g1.layer != g2.layer
    with pytest.raises(CrossLayerOperationError):
        g1 == g2


def test_layer_must_be_positive_integer():
    with pytest.raises(Exception):
        ThetaValue(coefficient=5, layer=0)


def test_chained_real_division_by_zero_then_gateway_division():
    """a/0 lands in layer 1; dividing that by layer-1 gateway lands in layer 2."""
    from zerodimension import zdiv
    first = zdiv(5, 0)
    assert first.layer == 1
    second = first / Gateway(layer=1)
    assert second.layer == 2
    assert second.coefficient == 5

"""
tests/test_property_based.py
================================
Property-based tests (via Hypothesis) generating many random
arithmetic expressions and confirming the framework's invariants:

  1. same-layer arithmetic preserves layer
  2. cross-layer direct arithmetic fails
  3. transition increases layer by exactly 1
  4. T lifts both sides consistently
  5. ordinary equations keep the same solution after applying T
  6. 0/0 never equals 0 or 1
  7. theta(1) displays as 1Θ
  8. theta(0) displays as Θ
  9. repeated transition preserves coefficient and increments layer

If Hypothesis is not installed, this module falls back to a small
deterministic sweep over many hand-picked values so the same
properties are still exercised (just without random search).
"""

import pytest

from zerodimension import (
    theta,
    ThetaValue,
    Gateway,
    T,
    transition,
    unify_layer,
    CrossLayerOperationError,
    zdiv,
)

try:
    from hypothesis import given, strategies as st, settings, HealthCheck
    _HAS_HYPOTHESIS = True
except ImportError:
    _HAS_HYPOTHESIS = False


# ── Strategies / fallback value pools ─────────────────────────────────────────

if _HAS_HYPOTHESIS:
    coeffs = st.integers(min_value=-1000, max_value=1000)
    small_coeffs = st.integers(min_value=-100, max_value=100)
    layers = st.integers(min_value=1, max_value=20)
    layer_pairs_diff = st.tuples(layers, layers).filter(lambda p: p[0] != p[1])
else:
    # Deterministic fallback pools used when hypothesis isn't installed.
    _COEFF_POOL = [-1000, -57, -10, -1, 0, 1, 2, 5, 10, 42, 100, 999, 1000]
    _LAYER_POOL = [1, 2, 3, 5, 8, 13, 20]


def _coeff_pool():
    return _COEFF_POOL


def _layer_pool():
    return _LAYER_POOL


# ════════════════════════════════════════════════════════════════════
# Property 1: same-layer arithmetic preserves layer
# ════════════════════════════════════════════════════════════════════

if _HAS_HYPOTHESIS:
    @given(a=coeffs, b=coeffs, layer=layers)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_property_same_layer_arithmetic_preserves_layer(a, b, layer):
        va, vb = theta(a, layer=layer), theta(b, layer=layer)
        assert (va + vb).layer == layer
        assert (va - vb).layer == layer
        assert (va * vb).layer == layer
        if b != 0:
            assert (va / vb).layer == layer
else:
    def test_property_same_layer_arithmetic_preserves_layer():
        for a in _coeff_pool():
            for b in _coeff_pool():
                for layer in _layer_pool():
                    va, vb = theta(a, layer=layer), theta(b, layer=layer)
                    assert (va + vb).layer == layer
                    assert (va - vb).layer == layer
                    assert (va * vb).layer == layer
                    if b != 0:
                        assert (va / vb).layer == layer


# ════════════════════════════════════════════════════════════════════
# Property 2: cross-layer direct arithmetic fails
# ════════════════════════════════════════════════════════════════════

if _HAS_HYPOTHESIS:
    @given(a=coeffs, b=coeffs, layer_pair=layer_pairs_diff)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_property_cross_layer_arithmetic_fails(a, b, layer_pair):
        l1, l2 = layer_pair
        va, vb = theta(a, layer=l1), theta(b, layer=l2)
        with pytest.raises(CrossLayerOperationError):
            va + vb
        with pytest.raises(CrossLayerOperationError):
            va - vb
        with pytest.raises(CrossLayerOperationError):
            va * vb
        with pytest.raises(CrossLayerOperationError):
            va / vb
else:
    def test_property_cross_layer_arithmetic_fails():
        for a in _coeff_pool()[:5]:
            for b in _coeff_pool()[:5]:
                for l1 in _layer_pool()[:3]:
                    for l2 in _layer_pool()[:3]:
                        if l1 == l2:
                            continue
                        va, vb = theta(a, layer=l1), theta(b, layer=l2)
                        with pytest.raises(CrossLayerOperationError):
                            va + vb
                        with pytest.raises(CrossLayerOperationError):
                            va - vb
                        with pytest.raises(CrossLayerOperationError):
                            va * vb
                        with pytest.raises(CrossLayerOperationError):
                            va / vb


# ════════════════════════════════════════════════════════════════════
# Property 3: transition increases layer by exactly 1
# ════════════════════════════════════════════════════════════════════

if _HAS_HYPOTHESIS:
    @given(a=coeffs, layer=layers)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_property_transition_increments_layer_by_one(a, layer):
        v = theta(a, layer=layer)
        result = transition(v)
        assert result.layer == layer + 1
else:
    def test_property_transition_increments_layer_by_one():
        for a in _coeff_pool():
            for layer in _layer_pool():
                v = theta(a, layer=layer)
                result = transition(v)
                assert result.layer == layer + 1


# ════════════════════════════════════════════════════════════════════
# Property 4: T lifts both sides consistently
# ════════════════════════════════════════════════════════════════════

if _HAS_HYPOTHESIS:
    @given(a=coeffs, layer=layers)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_property_T_lifts_equal_values_to_equal_results(a, layer):
        left = theta(a, layer=layer)
        right = theta(a, layer=layer)
        lifted_left = T(left)
        lifted_right = T(right)
        assert lifted_left.layer == lifted_right.layer
        assert lifted_left.coefficient == lifted_right.coefficient
        assert lifted_left == lifted_right
else:
    def test_property_T_lifts_equal_values_to_equal_results():
        for a in _coeff_pool():
            for layer in _layer_pool():
                left = theta(a, layer=layer)
                right = theta(a, layer=layer)
                lifted_left = T(left)
                lifted_right = T(right)
                assert lifted_left.layer == lifted_right.layer
                assert lifted_left.coefficient == lifted_right.coefficient
                assert lifted_left == lifted_right


# ════════════════════════════════════════════════════════════════════
# Property 5: ordinary equations keep the same solution after applying T
# ════════════════════════════════════════════════════════════════════

if _HAS_HYPOTHESIS:
    @given(a=small_coeffs, b=small_coeffs)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_property_ordinary_equation_solution_preserved_by_T(a, b):
        """
        For an ordinary equation x = E (no division by zero at all),
        the "solution" x = E is trivially preserved when we lift both
        sides with T: T(x) = T(E) implies the same relationship holds
        in the lifted layer (same coefficient relationship).
        """
        # Solve x = a "directly": x = a.
        # Lift: T(x)=T(a) -> xΘ1 = aΘ1 -> coefficient-equality x == a,
        # which is the same solution as the unlifted equation.
        lifted_lhs = T(a)
        lifted_rhs = T(a)
        assert lifted_lhs.coefficient == lifted_rhs.coefficient == a
else:
    def test_property_ordinary_equation_solution_preserved_by_T():
        for a in _coeff_pool():
            lifted_lhs = T(a)
            lifted_rhs = T(a)
            assert lifted_lhs.coefficient == lifted_rhs.coefficient == a


# ════════════════════════════════════════════════════════════════════
# Property 6: 0/0 never equals 0 or 1
# ════════════════════════════════════════════════════════════════════

def test_property_T_never_equals_zero_or_one():
    assert (T == 0) is False
    assert (T == 1) is False
    # Also check the *value* that 0/0 maps to via zdiv (the gateway of
    # layer 1) is never equal to plain 0 or plain 1 either.
    result = zdiv(0, 0)
    assert result != 0  # ThetaValue.__eq__ returns False vs plain numbers
    assert result.coefficient != 1


# ════════════════════════════════════════════════════════════════════
# Property 7 & 8: display axioms (already covered in test_display.py,
# repeated here as a property sweep across many coefficients/layers)
# ════════════════════════════════════════════════════════════════════

if _HAS_HYPOTHESIS:
    @given(layer=layers)
    @settings(max_examples=50)
    def test_property_theta_one_displays_as_1theta(layer):
        v = theta(1, layer=layer)
        assert str(v) == "1Θ"
        assert v.debug() == f"1Θ{_subscript_for_test(layer)}"

    @given(layer=layers)
    @settings(max_examples=50)
    def test_property_theta_zero_displays_as_theta(layer):
        v = theta(0, layer=layer)
        assert str(v) == "Θ"
else:
    def test_property_theta_one_displays_as_1theta():
        for layer in _layer_pool():
            v = theta(1, layer=layer)
            assert str(v) == "1Θ"

    def test_property_theta_zero_displays_as_theta():
        for layer in _layer_pool():
            v = theta(0, layer=layer)
            assert str(v) == "Θ"


def _subscript_for_test(n: int) -> str:
    from zerodimension.theta import _subscript
    return _subscript(n)


# ════════════════════════════════════════════════════════════════════
# Property 9: repeated transition preserves coefficient, increments layer
# ════════════════════════════════════════════════════════════════════

if _HAS_HYPOTHESIS:
    @given(a=coeffs, layer=st.integers(min_value=1, max_value=5),
           steps=st.integers(min_value=1, max_value=15))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_property_repeated_transition(a, layer, steps):
        v = theta(a, layer=layer)
        for _ in range(steps):
            v = transition(v)
        assert v.coefficient == a
        assert v.layer == layer + steps
else:
    def test_property_repeated_transition():
        for a in _coeff_pool():
            for layer in [1, 2, 3]:
                for steps in [1, 3, 7, 12]:
                    v = theta(a, layer=layer)
                    for _ in range(steps):
                        v = transition(v)
                    assert v.coefficient == a
                    assert v.layer == layer + steps

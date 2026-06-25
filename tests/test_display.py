"""
tests/test_display.py
========================
Tests for AXIOM F (display rules): coefficient 0/1/-1/n formatting,
debug-mode layer subscripts, and the global debug-mode toggle.
"""

import pytest

from zerodimension import (
    theta,
    ThetaValue,
    Gateway,
    set_debug_mode,
    is_debug_mode,
    render,
)


@pytest.fixture(autouse=True)
def _reset_debug_mode():
    """Ensure debug mode doesn't leak between tests."""
    set_debug_mode(False)
    yield
    set_debug_mode(False)


# ── AXIOM F: normal display ───────────────────────────────────────────────────

def test_coefficient_zero_displays_as_theta():
    assert str(theta(0)) == "Θ"


def test_coefficient_one_displays_as_1theta_not_bare_theta():
    assert str(theta(1)) == "1Θ"
    assert str(theta(1)) != "Θ"


def test_coefficient_negative_one_displays_as_minus1theta():
    assert str(theta(-1)) == "-1Θ"
    assert str(theta(-1)) != "-Θ"


def test_coefficient_n_displays_as_ntheta():
    assert str(theta(5)) == "5Θ"
    assert str(theta(100)) == "100Θ"
    assert str(theta(-7)) == "-7Θ"


def test_gateway_object_displays_as_theta():
    g = Gateway(layer=1)
    assert str(g) == "Θ"


# ── AXIOM F: debug display (layer subscripts) ─────────────────────────────────

def test_debug_shows_layer_subscript_for_gateway():
    assert theta(0, layer=2).debug() == "Θ₂"


def test_debug_shows_layer_subscript_for_value():
    assert theta(5, layer=2).debug() == "5Θ₂"
    assert theta(1, layer=1).debug() == "1Θ₁"
    assert theta(-1, layer=3).debug() == "-1Θ₃"


def test_normal_display_hides_layer():
    v = theta(5, layer=3)
    assert "₃" not in str(v)
    assert str(v) == "5Θ"


# ── Global debug-mode toggle ───────────────────────────────────────────────────

def test_debug_mode_default_off():
    assert is_debug_mode() is False


def test_debug_mode_toggle():
    set_debug_mode(True)
    assert is_debug_mode() is True
    set_debug_mode(False)
    assert is_debug_mode() is False


def test_render_honors_debug_mode():
    v = theta(5, layer=2)
    set_debug_mode(False)
    assert render(v) == "5Θ"
    set_debug_mode(True)
    assert render(v) == "5Θ₂"


def test_render_plain_number_passthrough():
    assert render(42) == "42"
    assert render(3.5) == "3.5"


# ── repr/str consistency ────────────────────────────────────────────────────

def test_repr_equals_str():
    v = theta(7, layer=2)
    assert repr(v) == str(v)

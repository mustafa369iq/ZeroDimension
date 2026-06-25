"""
tests/test_solver.py
=======================
Tests for the symbolic zero-division equation solver, covering all 5
required worked cases plus error handling.
"""

import pytest
import sympy

from zerodimension import solve_zero_division_equation, solve_equation_string
from zerodimension.exceptions import SolverError


def test_case_1_simple():
    """x/0 = 5  ->  x = 5"""
    result = solve_zero_division_equation("x/0", "5")
    assert result["solutions"] == [5]
    assert result["solve_for"] == "x"


def test_case_2_linear_rhs():
    """(x+3)/0 = 2*y - 5  ->  x = 2*y - 8"""
    result = solve_zero_division_equation("(x+3)/0", "2*y-5")
    y = sympy.Symbol("y")
    assert result["solutions"] == [2 * y - 8]
    assert result["solve_for"] == "x"


def test_case_3_both_sides_div_zero():
    """(x+3)/0 = (2*y-5)/0  ->  x = 2*y - 8"""
    result = solve_zero_division_equation("(x+3)/0", "(2*y-5)/0")
    y = sympy.Symbol("y")
    assert result["solutions"] == [2 * y - 8]
    assert result["solve_for"] == "x"


def test_case_4_two_symbols_both_div_zero():
    """x/0 = y/0  ->  x = y"""
    result = solve_zero_division_equation("x/0", "y/0")
    y = sympy.Symbol("y")
    assert result["solutions"] == [y]
    assert result["solve_for"] == "x"


def test_case_5_nested_division():
    """(x/2)/0 = 5  ->  x = 10"""
    result = solve_zero_division_equation("(x/2)/0", "5")
    assert result["solutions"] == [10]
    assert result["solve_for"] == "x"


# ── solve_equation_string convenience wrapper ─────────────────────────────────

def test_solve_equation_string_case_1():
    result = solve_equation_string("x/0 = 5")
    assert result["solutions"] == [5]


def test_solve_equation_string_case_2():
    result = solve_equation_string("(x+3)/0 = 2*y - 5")
    y = sympy.Symbol("y")
    assert result["solutions"] == [2 * y - 8]


def test_solve_equation_string_requires_equals_sign():
    with pytest.raises(SolverError):
        solve_equation_string("x/0 5")


# ── explicit solve_for override ───────────────────────────────────────────────

def test_explicit_solve_for():
    result = solve_zero_division_equation("(x+3)/0", "2*y-5", solve_for="y")
    x = sympy.Symbol("x")
    # x + 3 = 2y - 5  =>  y = (x+8)/2
    assert result["solve_for"] == "y"
    assert result["solutions"][0] == (x + 8) / 2


# ── error handling ───────────────────────────────────────────────────────────

def test_no_div_zero_on_either_side_raises():
    with pytest.raises(SolverError):
        solve_zero_division_equation("x + 1", "5")


def test_no_free_symbols_raises():
    with pytest.raises(SolverError):
        solve_zero_division_equation("5/0", "5")


def test_ambiguous_symbols_without_div_zero_hint_raises():
    """Both sides have no /0 marker to disambiguate -> should error
    if there truly are 2+ unrelated free symbols and no solve_for."""
    with pytest.raises(SolverError):
        solve_zero_division_equation("(x+y)/0", "z")

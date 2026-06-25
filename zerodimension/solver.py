"""
zerodimension.solver
=======================
Symbolic helpers for solving equations that contain division-by-zero
expressions, using the TransitionOperator (AXIOM D) to "lift" both
sides of the equation into the same Theta layer and then comparing
coefficients.

Core idea
---------
An expression like `(x + 3) / 0` is, under this framework, shorthand
for "lift (x+3) one Theta layer", i.e. T(x + 3) = (x+3)Θ1. If the
right-hand side of an equation is an ordinary expression `E`, applying
T to both sides gives:

    T((x+3)/0) = T(E)
    (x+3)Θ1    = EΘ1

Since both sides now live in the same layer, AXIOM A lets us equate
coefficients directly: x + 3 = E. We then use sympy to solve that
ordinary equation for the requested symbol.

If BOTH sides are division-by-zero expressions, e.g.
`(x+3)/0 = (2y-5)/0`, the same lift gives `(x+3)Θ1 = (2y-5)Θ1`, and
again the coefficients must be equal: x + 3 = 2y - 5.

This module deliberately works at the level of parsed sympy
expressions (the caller provides each side as a string like
"x/0 = 5" or "(x+3)/0 = 2*y - 5"), since the actual `/0` cannot be
evaluated by sympy directly (it has no concept of Theta-space).
"""

from __future__ import annotations

import re
from typing import Union, Dict, Any

try:
    import sympy
    from sympy import symbols, Eq, solve, sympify
    _HAS_SYMPY = True
except ImportError:  # pragma: no cover - sympy is a core dependency, but degrade gracefully
    _HAS_SYMPY = False

from .exceptions import SolverError


_DIV_ZERO_RE = re.compile(r"/\s*0(?!\.\d)(?!\d)")


def _strip_div_zero(expr_str: str) -> str:
    """
    Remove a trailing/embedded '/0' from an expression string, e.g.
    '(x+3)/0' -> '(x+3)', 'x/0' -> 'x', '(x/2)/0' -> '(x/2)'.

    This implements the "T-lift" symbolically: dividing by zero and
    then applying T cancels out, leaving the bare numerator — per
    AXIOM C/D, (E/0)*T = E*T => the /0 and the T-lift annihilate,
    leaving just E in the (now-shared) Theta layer.
    """
    if not _DIV_ZERO_RE.search(expr_str):
        return expr_str
    new_str = _DIV_ZERO_RE.sub("", expr_str)
    return new_str


def _has_div_zero(expr_str: str) -> bool:
    return bool(_DIV_ZERO_RE.search(expr_str))


def _require_sympy():
    if not _HAS_SYMPY:
        raise SolverError(
            "sympy is required for solve_zero_division_equation() but is "
            "not installed. Install it with: pip install sympy"
        )


def solve_zero_division_equation(
    left: str,
    right: str,
    solve_for: str = None,
) -> Dict[str, Any]:
    """
    Solve an equation where one or both sides may contain a literal
    '/0' division-by-zero expression, by lifting both sides into the
    same Theta layer (via the TransitionOperator, AXIOM D) and then
    solving the resulting ordinary equation with sympy.

    Parameters
    ----------
    left, right : str
        The two sides of the equation as strings, e.g. "x/0" and "5".
        At least one side must contain a literal '/0'.
    solve_for : str, optional
        The symbol to solve for. If omitted, the solver infers it as
        the only free symbol appearing in the lifted equation (raises
        SolverError if that's ambiguous).

    Returns
    -------
    dict with keys:
        "lifted_left"   : str  — the left side after the T-lift
        "lifted_right"  : str  — the right side after the T-lift
        "equation"      : str  — the resulting ordinary equation
        "solutions"     : list — sympy solution(s) for the requested symbol
        "solve_for"     : str  — the symbol that was solved for

    Examples
    --------
        solve_zero_division_equation("x/0", "5")
            -> x = 5

        solve_zero_division_equation("(x+3)/0", "2*y-5")
            -> x = 2*y - 8

        solve_zero_division_equation("(x+3)/0", "(2*y-5)/0")
            -> x = 2*y - 8

        solve_zero_division_equation("x/0", "y/0")
            -> x = y

        solve_zero_division_equation("(x/2)/0", "5")
            -> x = 10
    """
    _require_sympy()

    if not _has_div_zero(left) and not _has_div_zero(right):
        raise SolverError(
            "At least one side of the equation must contain a literal "
            "'/0' division-by-zero expression for the Theta-lift to apply. "
            f"Got left={left!r}, right={right!r}."
        )

    # AXIOM D / the T-lift: stripping '/0' on a side and leaving the
    # other side as-is is mathematically equivalent to applying T to
    # both sides and then equating coefficients in the shared layer
    # (see module docstring for the derivation).
    lifted_left  = _strip_div_zero(left)
    lifted_right = _strip_div_zero(right)

    try:
        left_expr  = sympify(lifted_left)
        right_expr = sympify(lifted_right)
    except (sympy.SympifyError, SyntaxError, TypeError) as e:
        raise SolverError(f"Could not parse equation sides as sympy expressions: {e}")

    equation = Eq(left_expr, right_expr)

    free_syms = sorted(equation.free_symbols, key=lambda s: s.name)

    if solve_for is not None:
        target = symbols(solve_for)
    else:
        if len(free_syms) == 0:
            raise SolverError(
                f"No free symbols found in equation '{lifted_left} = {lifted_right}'."
            )
        if len(free_syms) == 1:
            target = free_syms[0]
        else:
            # Multiple free symbols: prefer the symbol(s) that appeared
            # on a side which originally contained the '/0' expression
            # — that is the side the framework is "isolating", per the
            # worked examples (e.g. "(x+3)/0 = 2*y-5" solves for x,
            # the symbol behind the division-by-zero, not y).
            preferred_syms = set()
            left_has_div0  = _has_div_zero(left)
            right_has_div0 = _has_div_zero(right)

            if left_has_div0 and not right_has_div0:
                preferred_syms = left_expr.free_symbols
            elif right_has_div0 and not left_has_div0:
                preferred_syms = right_expr.free_symbols
            elif left_has_div0 and right_has_div0:
                # Both sides went through the Theta-lift (e.g.
                # "(x+3)/0 = (2*y-5)/0" or "x/0 = y/0"). By convention
                # we solve for the left-hand side's symbol(s), treating
                # the equation as "isolate the left side's unknown in
                # terms of the right side's expression".
                preferred_syms = left_expr.free_symbols

            preferred_syms = sorted(preferred_syms, key=lambda s: s.name)

            if len(preferred_syms) == 1:
                target = preferred_syms[0]
            else:
                raise SolverError(
                    f"Equation has multiple free symbols {free_syms} and the "
                    f"symbol to solve for is ambiguous; please specify "
                    f"solve_for=<symbol_name>."
                )

    solutions = solve(equation, target)

    return {
        "lifted_left":  str(left_expr),
        "lifted_right": str(right_expr),
        "equation":     f"{left_expr} = {right_expr}",
        "solutions":    solutions,
        "solve_for":    str(target),
    }


def solve_equation_string(equation_str: str, solve_for: str = None) -> Dict[str, Any]:
    """
    Convenience wrapper: parse a full equation string like
    "x/0 = 5" or "(x+3)/0 = 2*y - 5" and solve it.

    Splits on the first top-level '=' sign.
    """
    if "=" not in equation_str:
        raise SolverError(f"Equation string must contain '=': {equation_str!r}")
    left, right = equation_str.split("=", 1)
    return solve_zero_division_equation(left.strip(), right.strip(), solve_for=solve_for)

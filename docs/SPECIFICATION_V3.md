# ZeroDimension V3 — Technical Specification

This document specifies the package structure, public API, object
model, and error model of ZeroDimension V3. For the *why*, see
[`AXIOMS_V3.md`](./AXIOMS_V3.md). For the *how to use it*, see the
project [`README.md`](../README.md).

---

## 1. Package layout

```
zerodimension/
  __init__.py      Public API surface (re-exports everything below)
  theta.py          ThetaValue, Gateway, unify_layer, display formatting
  operators.py       TransitionOperator (T), zdiv/zadd/zsub/zmul, transition()
  exceptions.py       ZeroDimensionError and all subclasses
  solver.py           solve_zero_division_equation, solve_equation_string
  display.py          debug-mode toggle, render(), show(), theta_table()
  cli.py               interactive shell + console-script entry point
tests/
  conftest.py
  test_core.py
  test_display.py
  test_layers.py
  test_transition_operator.py
  test_solver.py
  test_property_based.py
docs/
  AXIOMS_V3.md
  SPECIFICATION_V3.md
README.md
setup.py
pytest.ini
```

---

## 2. Object model

### 2.1 `ThetaValue`

```python
class ThetaValue:
    coefficient: int | float | sympy expression
    layer: int          # >= 1
    state: str          # "value" | "gateway"
```

Construction:

```python
ThetaValue(coefficient=5, layer=1)             # 5Θ, state="value"
ThetaValue(coefficient=0, layer=1)             # Θ,  state="gateway" (forced)
ThetaValue(coefficient=0, layer=1, state="value")  # still normalizes to "gateway"
```

A coefficient of exactly `0` **always** forces `state = "gateway"`,
regardless of what `state` argument was passed — there is no other
valid interpretation of a zero-coefficient Theta value (Axiom A tail).

Invalid layers (`layer < 1` or non-integer) raise `InvalidLayerError`
at construction time.

Key properties / methods:

| Member | Type | Meaning |
|---|---|---|
| `.coefficient` | numeric | the `a` in `aΘn` |
| `.layer` | int | which Theta layer this value lives in |
| `.state` | str | `"value"` or `"gateway"` |
| `.is_gateway` | bool | `state == "gateway"` |
| `.trace` | list[str] | derivation history (for debugging/explanation) |
| `.debug()` | str | layer-subscript display, e.g. `"5Θ₂"` |
| `.show()` | None | pretty-prints a full diagnostic block |
| `.to_gateway()` | `Gateway` | the Gateway object for this value's layer |
| `.equals_after_unify(other)` | bool | cross-layer-safe equality (Axiom E) |

Operators: `+`, `-`, `*`, `/`, `**`, unary `-`, `abs()`, `==`. See
[`AXIOMS_V3.md`](./AXIOMS_V3.md) Axioms A/B/C/E for their exact
semantics.

### 2.2 `Gateway`

```python
class Gateway(ThetaValue):
    def __init__(self, layer: int = 1): ...
```

A thin, semantically-named subclass: `Gateway(layer=n)` is exactly
`ThetaValue(coefficient=0, layer=n, state="gateway")`. Provided so
code reads naturally (`Gateway(layer=2)` vs.
`ThetaValue(0, layer=2)`).

### 2.3 `TransitionOperator` (and the `T` singleton-style instance)

```python
class TransitionOperator:
    def __call__(self, value): ...   # lifts value one Theta layer
```

`T = TransitionOperator()` is provided as a ready-to-use module-level
instance. See Axiom D. All arithmetic dunder methods other than
`__call__` raise `TransitionOperatorMisuseError`.

---

## 3. Functional API (Section G helpers)

| Function | Signature | Behavior |
|---|---|---|
| `zdiv(a, b)` | `(Number\|ThetaValue, Number\|ThetaValue) -> Number\|ThetaValue` | Safe division; `a/0 -> aΘ1`; never raises `ZeroDivisionError` |
| `zadd(a, b)` | same | Safe addition; cross-layer mixes raise `CrossLayerOperationError` |
| `zsub(a, b)` | same | Safe subtraction; same cross-layer rule |
| `zmul(a, b)` | same | Safe multiplication; scalar scaling always allowed |
| `unify_layer(a, target_layer)` | `(ThetaValue, int) -> ThetaValue` | Repeatedly applies the gateway transition until `a.layer == target_layer` |
| `transition(a)` | `(Number\|ThetaValue) -> ThetaValue` | Functional alias for `T(a)` |
| `solve_zero_division_equation(left, right, solve_for=None)` | `(str, str, str\|None) -> dict` | Lifts both sides via `T`, solves with sympy |
| `solve_equation_string(eq_str, solve_for=None)` | `(str, str\|None) -> dict` | Convenience wrapper splitting on `"="` |

`theta(coefficient=0, layer=1)` (exported from the package root) is
the primary user-facing constructor and is what most examples use.

---

## 4. Exception hierarchy

```
ZeroDimensionError
├── CrossLayerOperationError      (Axiom B / E violations)
├── TransitionOperatorMisuseError (Axiom D violations)
├── InvalidLayerError              (layer < 1 or non-integer)
├── GatewayDivisionError            (reserved for future Gateway-specific errors)
└── SolverError                      (solve_zero_division_equation failures)
```

All framework-specific errors derive from `ZeroDimensionError`, so
catching that single type is sufficient for code that wants to handle
"something about the Theta framework went wrong" generically, while
more specific `except` clauses remain available.

---

## 5. The equation solver

`solve_zero_division_equation(left, right, solve_for=None)`:

1. Confirms at least one side contains a literal `"/0"` substring
   (otherwise raises `SolverError` — there is nothing to lift).
2. Strips `"/0"` from each side that has it (symbolically equivalent
   to applying `T` to that side and cancelling the layer marker — see
   `AXIOMS_V3.md` Axiom D).
3. Parses both resulting strings with `sympy.sympify`.
4. Builds a `sympy.Eq` and determines the symbol to solve for:
   - explicit `solve_for=` argument, if given;
   - otherwise, if there's exactly one free symbol, use it;
   - otherwise, prefer symbol(s) from the side(s) that originally had
     `/0` (this matches the worked examples, where the division side
     is being "isolated").
5. Calls `sympy.solve(...)` and returns a dict:
   `{lifted_left, lifted_right, equation, solutions, solve_for}`.

This module requires `sympy`; if it isn't installed,
`solve_zero_division_equation` raises `SolverError` immediately rather
than failing with an `ImportError` deep in the call stack.

---

## 6. Display formatting (Axiom F implementation note)

All Theta formatting funnels through one function:
`zerodimension.theta._format_theta(coefficient, layer, debug=False)`.
`ThetaValue.__repr__`, `ThetaValue.__str__`, and `ThetaValue.debug()`
all call it; `zerodimension.display.render()` is a higher-level
wrapper that additionally consults the global debug-mode flag for
CLI/shell convenience. No other code path should construct a Theta
display string by hand.

---

## 7. Versioning

This is **V3** of the ZeroDimension framework. It is not
backward-compatible with V1/V2's flat (single-layer) `ThetaValue`
model — V3 introduces layers, the Gateway/state distinction, the
TransitionOperator, and cross-layer error enforcement, none of which
existed in earlier versions.

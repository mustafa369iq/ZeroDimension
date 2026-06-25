# ZeroDimension V3 — Axioms

This document is the formal, authoritative list of axioms the
ZeroDimension V3 framework is built on. Every behavior in the code
should be traceable back to one of these axioms; if it isn't, it's a
bug.

---

## Core Philosophy

1. **Ordinary mathematics is never modified.** Arithmetic on plain
   Python numbers (real space — informally "layer 0") behaves exactly
   as standard Python/math always has.
2. **Division by zero never crashes.** `a / 0` does not raise
   `ZeroDivisionError`. It produces a `ThetaValue` in the next
   Theta-layer instead.
3. **Theta stores value, layer, and state.** Every `ThetaValue` carries
   a `coefficient`, a `layer` (an integer ≥ 1), and a `state`
   (`"value"` or `"gateway"`).
4. **Layer metadata may be hidden in display but must exist
   internally.** `str(theta(5, layer=3))` shows `"5Θ"` with no visible
   layer, but `.layer == 3` is still there, and `.debug()` reveals it
   as `"5Θ₃"`.

---

## Axiom A — Same-layer arithmetic

For `ThetaValue` objects on the **same** layer `n`:

```
aΘn + bΘn = (a+b)Θn
aΘn - bΘn = (a-b)Θn
aΘn * bΘn = (a*b)Θn
aΘn / bΘn = (a/b)Θn      (if b != 0)
```

If a coefficient becomes `0` as a result of an operation (e.g.
cancellation: `5Θ3 - 5Θ3`), the result displays as `Θ` but the layer
(`3`, in this example) is preserved internally, and the resulting
value's `state` becomes `"gateway"`.

Scalar multiplication by a plain number (`aΘn * k`) is always allowed
and does not change the layer — a bare scalar carries no layer of its
own to conflict with.

---

## Axiom B — Cross-layer arithmetic is forbidden

Direct arithmetic between `ThetaValue`s on **different** layers is not
allowed and raises `CrossLayerOperationError`.

```
5Θ1 + 3Θ2   # raises CrossLayerOperationError
```

Mixing a plain real number with a `ThetaValue` directly (e.g.
`theta(5, layer=1) + 3`) is likewise a cross-layer operation (real
numbers belong to "layer 0") and also raises
`CrossLayerOperationError`.

To combine values across layers, you must **explicitly unify** them
first — see `unify_layer()`.

---

## Axiom C — Gateway transition

Dividing a value by the **gateway of its own layer** moves the result
to the **next** layer:

```
aΘn / Θn = aΘ(n+1)
```

From ordinary real space:

```
a / 0 = aΘ1
0 / 0 = Θ1
```

In general:

```
0Θn / Θn = Θ(n+1)
```

**The transition is one-way by default.** There is no automatic
"return" or "lower layer" operation; once a value has transitioned to
layer `n+1`, getting back to layer `n` is not part of this framework's
defined behavior (and no method is provided for it).

---

## Axiom D — The TransitionOperator (`0/0`)

`0/0` is **not a number**. It is the **TransitionOperator** — a
unification/transition operator, instantiated as `T`.

* `T` is the only operator that simultaneously:
  - has zero in the numerator, which can cancel a zero denominator on
    the other side of an equation, and
  - has zero in the denominator, which lifts the opposite side into
    the same Theta layer.
* `T` is never equal to `0`, never equal to `1`, and arithmetic
  operators on `T` (`+`, `-`, `*`, `/`, `**`) raise
  `TransitionOperatorMisuseError` rather than silently coercing `T`
  into a number.
* `T` is **callable**. Calling it lifts a value one layer:

```
T(a)           = aΘ1        if a is an ordinary (layer-0) number
T(aΘn)         = aΘ(n+1)
T(0)           = Θ1
T(Θn gateway)  = Θ(n+1)
```

* `T` is used to **solve equations** that contain a literal `/0`:

```
x/0 = 5
(x/0) * T = 5 * T
xΘ1 = 5Θ1
x = 5
```

The `solve_zero_division_equation()` / `solve_equation_string()`
helpers automate this lift-and-compare process using `sympy`.

---

## Axiom E — Equality

* `aΘn == bΘn` iff `a == b` (same layer, same coefficient, same
  state).
* `aΘn == bΘm` (different layers) raises `CrossLayerOperationError` —
  layer mismatch is a meaningful condition the framework wants
  surfaced, not silently swallowed into `False`.
* `ThetaValue.equals_after_unify(other)` is the **explicit, opt-in**
  way to compare values across layers: it lifts both operands to
  `max(layer_a, layer_b)` via `unify_layer()` and then compares
  coefficients.
* A `ThetaValue` (layer ≥ 1) is **never** equal to a plain real number
  (layer 0) under `==`.

---

## Axiom F — Display rules

Normal display **hides** the layer:

```
theta(0)   -> "Θ"
theta(1)   -> "1Θ"     (never bare "Θ")
theta(-1)  -> "-1Θ"    (never bare "-Θ")
theta(5)   -> "5Θ"
```

Debug display (`.debug()`, or global `set_debug_mode(True)`) **shows**
the layer as a unicode subscript:

```
theta(0, layer=1)   -> "Θ₁"
theta(1, layer=1)   -> "1Θ₁"
theta(5, layer=2)   -> "5Θ₂"
```

These rules are implemented in exactly one place
(`zerodimension.theta._format_theta`) so there is a single source of
truth; no other code path is permitted to hand-roll Theta formatting.

---

## Summary table

| Axiom | Subject | Key rule |
|---|---|---|
| A | Same-layer arithmetic | `aΘn op bΘn = (a op b)Θn` |
| B | Cross-layer arithmetic | Forbidden — raises `CrossLayerOperationError` |
| C | Gateway transition | `aΘn / Θn = aΘ(n+1)`; one-way |
| D | TransitionOperator (`0/0`) | Not a number; `T(x)` lifts one layer |
| E | Equality | Same-layer only, unless explicitly unified |
| F | Display | `0→Θ`, `1→1Θ`, `-1→-1Θ`, `n→nΘ`; layer hidden unless debug |

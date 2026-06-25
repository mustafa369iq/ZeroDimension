# Known Limitations — ZeroDimension V3

## 1. Multiplication of multiple zero-division expressions

### Example

```text
(x/0) * (y/0) = 10

Current solver lifting:

x*y = 10
Concern

According to layer semantics:

x/0 -> xΘ₁
y/0 -> yΘ₁

Then:

(xΘ₁) * (yΘ₁) = xyΘ₁

The current solver treats this as a simplified lifted equation, not a full layer-aware expression simulation.

Status

Known limitation of V3.

Action

Review in V4 before changing behavior.

2. Powers of zero-division expressions
Example
(x/0)^2 = 25

Current solver lifting:

x^2 = 25
Concern

Need to define whether repeated /0 inside powers represents one transition, repeated transition, or expression-level unification.

Status

Known limitation of V3.

Action

Review in V4.

---

## Verified Property — Layer unification preserves same-layer arithmetic

During scientific review, the following behavior was experimentally verified for same-layer values:

```text
U(a+b)=U(a)+U(b)
U(a-b)=U(a)-U(b)
U(ab)=U(a)U(b)
U(a/b)=U(a)/U(b), b ≠ 0

Where U denotes unify_layer(value, target_layer).

Interpretation

Layer unification in V3 preserves the basic algebraic structure of same-layer arithmetic.

Status

Verified experimentally in V3.

---

## Known Numerical Artifact — Fractional powers of negative coefficients

### Example

```text
sqrt(-4Θ₂)

Current result:

(1.2246467991473532e-16+2j)Θ₂
Interpretation

The expected mathematical result is approximately:

2jΘ₂

The small real component is a floating-point artifact from Python numeric evaluation, not a Theta-layer inconsistency.

Status

Known numerical artifact in V3.

Action

Review symbolic/complex simplification in future versions.

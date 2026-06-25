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

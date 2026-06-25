# ZeroDimension Framework V3
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20840182.svg)](https://doi.org/10.5281/zenodo.20840182)
[![Tests](https://github.com/mustafa369iq/ZeroDimension/actions/workflows/tests.yml/badge.svg)](https://github.com/mustafa369iq/ZeroDimension/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-v3.0.2-purple)

[![Tests](https://github.com/mustafa369iq/ZeroDimension/actions/workflows/tests.yml/badge.svg)](https://github.com/mustafa369iq/ZeroDimension/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-v3.0.0-purple)
![License](https://img.shields.io/badge/license-MIT-green)
**ZeroDimension** is an experimental symbolic computation framework that represents expressions produced by division-by-zero transitions using layered Theta states.

It does **not** claim to replace classical mathematics. Instead, it defines a self-contained symbolic system for tracking division-by-zero events without collapsing them into `NaN`, `Infinity`, or runtime exceptions.

---

## Why ZeroDimension?

In ordinary software, division by zero usually causes one of three outcomes:

- Exception
- NaN
- Infinity

ZeroDimension takes a different approach:


5 / 0 → 5Θ₁


The value is not discarded. It is represented symbolically as a Theta value with internal layer metadata.

---

## Core Idea


Real Space

5
│
│ divide by zero
▼
5Θ₁
│
│ transition
▼
5Θ₂
│
▼
5Θ₃


Each transition preserves the coefficient while increasing the internal layer by exactly one.

Normal display hides the layer:


5Θ


Debug display reveals it:


5Θ₃


---

## Current Status

- Version: V3
- Status: Stable Experimental Prototype
- Tests Passed: 97
- CLI: Working
- Equation Solver: Working

---

## Quick Example

```python
from zerodimension import theta, zdiv, transition

print(zdiv(5,0))
print(zdiv(0,0))

x = zdiv(5,0)
print(x.layer)

y = transition(x)
print(y.layer)
print(y.debug())
Installation
pip install -e .

Testing:

pip install -e ".[test]"
pytest
Main Concepts
ThetaValue

Stores:

coefficient
layer
state

Examples:

theta(0)
theta(1)
theta(-1)
theta(5)
theta(5, layer=2)
Gateway

Represents the zero-coefficient Theta value of a layer.

TransitionOperator (T)

Represents symbolic 0/0.

It is:

NOT a number
NOT equal to 0
NOT equal to 1

Examples:

T(5)
T(0)
Rule Summary
Operation	Result
5 / 2	2.5
5 / 0	5Θ₁
0 / 0	Θ₁
transition(5)	5Θ₁
transition(5Θ₁)	5Θ₂
5Θ₁ + 3Θ₁	8Θ₁
5Θ₁ + 3Θ₂	Error
theta(0)	Θ
theta(1)	1Θ
Axioms
Ordinary arithmetic remains unchanged unless a division-by-zero transition occurs.
Every Theta value stores coefficient, layer and state.
Arithmetic is allowed only inside the same layer.
Cross-layer arithmetic is forbidden.
Dividing by a gateway moves the value to the next layer.
TransitionOperator (0/0) is not a number.
Display hides layer metadata unless debug mode is enabled.
No automatic downward transition exists.

Full details:

docs/AXIOMS_V3.md

Solving Equations
solve("x/0","5")
solve("(x+3)/0","2*y-5")
solve("(x+3)/0","(2*y-5)/0")
solve("x/0","y/0")
Interactive Shell
python -m zerodimension.cli shell

Examples:

theta(5)
zdiv(5,0)
transition(5)
solve "x/0 = 5"
Running Tests
pytest

Current coverage:

Core arithmetic
Display
Layers
TransitionOperator
Solver
Property-based tests
Project Structure
zerodimension/
tests/
docs/
Limitations

ZeroDimension is an experimental symbolic framework.

It does not redefine classical arithmetic.

It introduces symbolic behavior only after division-by-zero transitions.

Documentation

See:

docs/AXIOMS_V3.md
docs/SPECIFICATION_V3.md


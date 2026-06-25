# ZeroDimension Framework V3

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20840182.svg)](https://doi.org/10.5281/zenodo.20840182)
[![Tests](https://github.com/mustafa369iq/ZeroDimension/actions/workflows/tests.yml/badge.svg)](https://github.com/mustafa369iq/ZeroDimension/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-v3.0.2-purple)

**ZeroDimension** is an experimental symbolic computation framework that represents expressions produced by division-by-zero transitions using layered Theta states.

It does **not** replace classical mathematics. It defines a self-contained symbolic system for tracking division-by-zero events without collapsing them into `NaN`, `Infinity`, or runtime exceptions.

## Why ZeroDimension?

In ordinary software, division by zero usually causes:

- Exception
- NaN
- Infinity

ZeroDimension represents the event symbolically:

```text
5 / 0  →  5Θ₁

The value is preserved with internal layer metadata.

Core Idea
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

Normal display hides the layer:

5Θ

Debug display reveals it:

5Θ₃
Current Status
Version: V3.0.2
Status: Stable experimental prototype
Tests: 97 passing
CLI: Working
Equation solver: Working
DOI: 10.5281/zenodo.20840182
Quick Example
from zerodimension import theta, zdiv, transition

print(zdiv(5, 0))      # 5Θ
print(zdiv(0, 0))      # Θ

x = zdiv(5, 0)
print(x.layer)         # 1

y = transition(x)
print(y.layer)         # 2
print(y.debug())       # 5Θ₂
Installation
pip install -e .

For tests:

pip install -e ".[test]"
pytest
Main Concepts
ThetaValue

A symbolic value storing:

coefficient
layer
state

Examples:

theta(0)              # Θ
theta(1)              # 1Θ
theta(-1)             # -1Θ
theta(5)              # 5Θ
theta(5, layer=2)     # 5Θ
theta(5, layer=2).debug()  # 5Θ₂
Gateway

A zero-coefficient Theta value of a specific layer. It represents the transition boundary of that layer.

TransitionOperator

0/0 is represented by T.

It is:

not a number
not equal to 0
not equal to 1
used as a transition/unification operator
from zerodimension import T

T(5)   # 5Θ
T(0)   # Θ
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
Axioms in Brief
Ordinary arithmetic remains unchanged unless a division-by-zero transition occurs.
Every Theta value stores coefficient, layer, and state.
Arithmetic is allowed only inside the same layer.
Cross-layer arithmetic is forbidden.
Dividing by a gateway moves the value to the next layer.
0/0 is a TransitionOperator, not a number.
Display hides layer metadata unless debug mode is enabled.
No automatic downward transition exists.

Full details:

Axioms V3
Specification V3
Solving Equations
from zerodimension import solve_zero_division_equation as solve

solve("x/0", "5")
solve("(x+3)/0", "2*y-5")
solve("(x+3)/0", "(2*y-5)/0")
solve("x/0", "y/0")
Interactive Shell
python -m zerodimension.cli shell

Examples:

Θ> theta(5)
  5Θ

Θ> zdiv(5,0)
  5Θ

Θ> debug(theta(5, layer=2))
  5Θ₂

Θ> solve "x/0 = 5"
  x = 5
Running Tests
pytest

Test coverage includes:

core arithmetic
display
layers
TransitionOperator
solver
property-based tests
Project Structure
zerodimension/
tests/
docs/
Limitations

ZeroDimension is an experimental symbolic framework.

It does not redefine classical arithmetic. It introduces symbolic behavior only after division-by-zero transitions.

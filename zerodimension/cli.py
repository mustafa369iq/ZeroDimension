"""
zerodimension.cli
====================
Interactive shell and console-script entry point for ZeroDimension V3.

Usage (after `pip install -e .`):

    zerodimension shell

Or directly:

    python -m zerodimension.cli shell

Shell commands (see Section CLI requirements):
    theta(5)                  -> 5Θ
    theta(5, layer=2)         -> 5Θ   (debug: 5Θ2)
    zdiv(5, 0)                -> 5Θ
    transition(5)             -> 5Θ
    debug(theta(5, layer=2))  -> toggles a one-off debug-form print
    solve "x/0 = 5"           -> solves the equation
    debugmode on|off          -> toggles persistent debug display
    help                      -> show command list
    exit / quit                -> leave the shell
"""

from __future__ import annotations

import re
import sys
from typing import Any

from .theta import ThetaValue, Gateway, unify_layer
from .operators import T, transition, zdiv, zadd, zsub, zmul
from .display import set_debug_mode, is_debug_mode, render
from .solver import solve_equation_string
from .exceptions import ZeroDimensionError


def theta(coefficient=0, layer: int = 1) -> ThetaValue:
    """Shell/CLI convenience constructor: theta(5), theta(5, layer=2)."""
    return ThetaValue(coefficient=coefficient, layer=layer)


HELP_TEXT = """
  ZeroDimension V3 Shell — Commands
  ──────────────────────────────────────────────────────────
  Construction:
    theta(5)               -> 5Θ
    theta(5, layer=2)      -> 5Θ   (use debug(...) to see the layer)
    theta(0)               -> Θ
    theta(1)               -> 1Θ
    theta(-1)              -> -1Θ

  Safe arithmetic:
    zdiv(5, 0)              -> 5Θ
    zdiv(0, 0)               -> Θ
    zadd(theta(2), theta(3)) -> 5Θ
    zsub(theta(5), theta(2)) -> 3Θ
    zmul(theta(5), 3)         -> 15Θ

  Transition operator (0/0):
    transition(5)            -> 5Θ   (lifts 5 into layer 1)
    transition(theta(5,layer=1)) -> 5Θ (now layer 2; see debug())

  Debug / inspection:
    debug(theta(5, layer=2)) -> 5Θ₂   (one-off debug-form display)
    debugmode on              -> all subsequent output shows layers
    debugmode off              -> hide layers again (default)

  Solving zero-division equations:
    solve "x/0 = 5"                  -> x = 5
    solve "(x+3)/0 = 2*y - 5"         -> x = 2*y - 8
    solve "(x+3)/0 = (2*y-5)/0"       -> x = 2*y - 8
    solve "x/0 = y/0"                 -> x = y
    solve "(x/2)/0 = 5"               -> x = 10

  Other:
    help                       -> show this message
    exit / quit                 -> leave the shell
  ──────────────────────────────────────────────────────────
"""

BANNER = r"""
  ╔════════════════════════════════════════════════╗
  ║   ZeroDimension V3 Shell                        ║
  ║   Theta-space division-by-zero framework        ║
  ║   type 'help' for commands, 'exit' to quit      ║
  ╚════════════════════════════════════════════════╝
"""


_COMMAND_PATTERN = re.compile(r"^(\w+)\((.*)\)$", re.DOTALL)

_NAMESPACE = {
    "theta": theta,
    "zdiv": zdiv,
    "zadd": zadd,
    "zsub": zsub,
    "zmul": zmul,
    "transition": transition,
    "T": T,
    "unify_layer": unify_layer,
    "Gateway": Gateway,
    "ThetaValue": ThetaValue,
}


def _eval_call(line: str) -> Any:
    """Evaluate a function-call-shaped line in a restricted namespace."""
    return eval(line, {"__builtins__": {}}, _NAMESPACE)


def evaluate_line(line: str) -> str:
    """
    Evaluate a single shell line and return its display text.
    Mirrors the structure used by the V2 shell, adapted for V3's
    layer-aware objects and the solve command.
    """
    line = line.strip()
    if not line:
        return ""

    if line.startswith("debugmode"):
        rest = line[len("debugmode"):].strip().lower()
        if rest == "on":
            set_debug_mode(True)
            return "debug mode: ON"
        if rest == "off":
            set_debug_mode(False)
            return "debug mode: OFF"
        return f"debug mode is currently {'ON' if is_debug_mode() else 'OFF'}"

    if line.startswith("debug(") and line.endswith(")"):
        inner = line[len("debug("):-1]
        value = _eval_call(inner)
        if isinstance(value, ThetaValue):
            return value.debug()
        return render(value)

    if line.startswith("solve"):
        eq_str = line[len("solve"):].strip()
        if not eq_str:
            return 'Usage: solve "x/0 = 5"'

        # Accept both:
        #   solve "x/0 = 5"
        #   solve x/0 = 5
        if (eq_str.startswith('"') and eq_str.endswith('"')) or (eq_str.startswith("'") and eq_str.endswith("'")):
            eq_str = eq_str[1:-1].strip()

        if "=" not in eq_str:
            return 'Usage: solve "x/0 = 5"'

        result = solve_equation_string(eq_str)
        sols = result["solutions"]
        sol_str = ", ".join(str(s) for s in sols) if isinstance(sols, list) else str(sols)
        return f"{result['solve_for']} = {sol_str}"

    value = _eval_call(line)
    return render(value)


def run_shell() -> None:
    print(BANNER)
    while True:
        try:
            line = input("Θ> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  goodbye.\n")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            print("  goodbye.\n")
            break
        if line.lower() == "help":
            print(HELP_TEXT)
            continue

        try:
            output = evaluate_line(line)
            if output:
                print(f"  {output}")
        except ZeroDimensionError as e:
            print(f"  [ZeroDimension error] {e}")
        except Exception as e:
            print(f"  error: {e}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: zerodimension <command>")
        print("Commands:")
        print("  shell   - launch the interactive Theta shell")
        return
    if args[0] == "shell":
        run_shell()
    else:
        print(f"Unknown command: {args[0]}")
        print("Run 'zerodimension --help' for usage.")


if __name__ == "__main__":
    main()

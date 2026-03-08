"""
tools/python_tool.py
--------------------
A restricted Python execution sandbox for the SolverAgent.

Gives the agent access to numeric computation (math, statistics, combinatorics)
without allowing dangerous operations (file I/O, network, subprocess, etc.).

Safe imports allowed: math, statistics, itertools, fractions, decimal, cmath
Also provides: a small set of helper functions (nCr, nPr, gcd, lcm, prime check)
"""
import math
import statistics
import itertools
import fractions
import decimal
import cmath
import traceback
from typing import Any, Dict

from langchain_core.tools import tool


# ── Allowed builtins ──────────────────────────────────────────────────────────
_SAFE_BUILTINS = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sum": sum, "len": len, "range": range, "enumerate": enumerate,
    "zip": zip, "map": map, "filter": filter, "sorted": sorted,
    "list": list, "tuple": tuple, "dict": dict, "set": set,
    "int": int, "float": float, "str": str, "bool": bool,
    "print": print,   # captured via exec stdout redirect
    "True": True, "False": False, "None": None,
}

# ── Helper functions always available in sandbox ──────────────────────────────
def _ncr(n: int, r: int) -> int:
    return math.comb(n, r)

def _npr(n: int, r: int) -> int:
    return math.perm(n, r)

def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def _primes_up_to(n: int):
    return [i for i in range(2, n + 1) if _is_prime(i)]


_SANDBOX_GLOBALS: Dict[str, Any] = {
    "__builtins__": _SAFE_BUILTINS,
    # Standard library modules
    "math": math,
    "statistics": statistics,
    "itertools": itertools,
    "fractions": fractions,
    "Fraction": fractions.Fraction,
    "decimal": decimal,
    "Decimal": decimal.Decimal,
    "cmath": cmath,
    # Helper functions
    "nCr": _ncr,
    "nPr": _npr,
    "C": _ncr,      # shorthand
    "P": _npr,      # shorthand
    "is_prime": _is_prime,
    "primes_up_to": _primes_up_to,
    "gcd": math.gcd,
    "lcm": math.lcm,
    "factorial": math.factorial,
    "pi": math.pi,
    "e": math.e,
    "inf": math.inf,
    "sqrt": math.sqrt,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "degrees": math.degrees,
    "radians": math.radians,
    "floor": math.floor,
    "ceil": math.ceil,
    "comb": math.comb,
    "perm": math.perm,
}


# ── Blocked patterns (security) ───────────────────────────────────────────────
_BLOCKED_KEYWORDS = [
    "import", "open(", "exec(", "eval(", "compile(",
    "__import__", "subprocess", "os.", "sys.",
    "socket", "urllib", "http", "requests",
    "builtins", "__class__", "__bases__", "__mro__",
    "globals(", "locals(", "vars(",
]


def _is_safe(code: str) -> tuple[bool, str]:
    """Quick static check for obviously dangerous patterns."""
    code_lower = code.lower()
    for keyword in _BLOCKED_KEYWORDS:
        if keyword in code_lower:
            return False, f"Blocked keyword detected: '{keyword}'"
    return True, ""


@tool
def execute_python(code: str) -> str:
    """
    Execute Python code in a safe numeric sandbox and return the output.

    Available: math, statistics, fractions, itertools, decimal, cmath modules.
    Helper functions: nCr(n,r), nPr(n,r), gcd(a,b), lcm(a,b), factorial(n),
                      is_prime(n), primes_up_to(n), C(n,r), P(n,r)
    Constants: pi, e, inf, sqrt, sin, cos, tan, log, exp, etc.

    Use for:
    - Numerical verification of symbolic results
    - Combinatorics (nCr, nPr, factorial)
    - Probability calculations
    - Iterating over cases / checking constraints
    - Any arithmetic too complex to do mentally

    Args:
        code: Python code to execute. Use print() to output results.
              Example: "print(nCr(10, 3))"
              Example: "x = sqrt(2); print(round(x, 6))"
              Example: "print(sum(i**2 for i in range(1, 11)))"

    Returns:
        Everything printed to stdout, or an error message.

    Restrictions:
        - No file I/O, no network, no subprocess, no imports
        - Max execution time: 5 seconds
        - Max output: 2000 characters
    """
    import io
    import sys
    import signal

    # Static safety check
    safe, reason = _is_safe(code)
    if not safe:
        return f"[BLOCKED] {reason}"

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    result_output = ""
    try:
        # Run in sandbox with 5-second timeout (Unix only; on Windows falls back)
        local_vars: Dict[str, Any] = {}

        try:
            # signal-based timeout only works on Unix
            def _timeout_handler(signum, frame):
                raise TimeoutError("Execution exceeded 5 seconds.")

            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(5)
        except (AttributeError, OSError):
            pass  # Windows — no SIGALRM

        exec(code, dict(_SANDBOX_GLOBALS), local_vars)  # noqa: S102

        try:
            signal.alarm(0)
        except (AttributeError, OSError):
            pass

        result_output = buffer.getvalue()

        # If code produced no print output, check if last expression has a value
        if not result_output.strip() and local_vars:
            # Show the last assigned variable
            last_key = list(local_vars.keys())[-1]
            last_val = local_vars[last_key]
            result_output = f"{last_key} = {last_val}"

    except TimeoutError as e:
        result_output = f"[TIMEOUT] {e}"
    except Exception:
        result_output = f"[ERROR]\n{traceback.format_exc(limit=3)}"
    finally:
        sys.stdout = old_stdout

    # Truncate very long output
    if len(result_output) > 2000:
        result_output = result_output[:2000] + "\n...[truncated]"

    return result_output.strip() or "(no output)"
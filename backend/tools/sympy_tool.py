"""
tools/sympy_tool.py
-------------------
LangChain tools that wrap SymPy for symbolic mathematics.
Used by the SolverAgent for exact algebraic / calculus operations.

Tools exposed:
  - solve_equation   : solve one or more equations for a variable
  - derivative       : differentiate an expression
  - integrate_expr   : definite or indefinite integration
  - simplify_expr    : algebraic simplification
"""
import traceback

from langchain_core.tools import tool


def _safe_sympify(expr_str: str):
    """Parse a string into a SymPy expression with common math symbols available."""
    from sympy import symbols, sympify, sqrt, pi, E, oo, sin, cos, tan, exp, log, Abs
    import sympy as sp

    # Make a rich namespace so the LLM can write natural expressions
    ns = {name: getattr(sp, name) for name in dir(sp) if not name.startswith("_")}
    ns.update({"sqrt": sqrt, "pi": pi, "e": E, "oo": oo, "inf": oo})
    return sympify(expr_str, locals=ns)


@tool
def solve_equation(equation: str, variable: str = "x") -> str:
    """
    Solve one or more equations symbolically using SymPy.

    Args:
        equation: Equation(s) to solve. Use '=' to separate LHS and RHS.
                  For a system, separate equations with a semicolon.
                  Examples:
                    "x^2 - 5*x + 6 = 0"
                    "2*x + y = 5; x - y = 1"
        variable: Variable(s) to solve for, comma-separated if multiple.
                  Examples: "x", "x,y"

    Returns:
        The solution set as a string.
    """
    try:
        from sympy import solve, Eq, symbols

        var_names = [v.strip() for v in variable.split(",")]
        sym_vars = symbols(" ".join(var_names))
        if not isinstance(sym_vars, (list, tuple)):
            sym_vars = [sym_vars]

        # Parse equations
        eqs = []
        for eq_str in equation.split(";"):
            eq_str = eq_str.strip()
            if "=" in eq_str:
                lhs_str, rhs_str = eq_str.split("=", 1)
                lhs = _safe_sympify(lhs_str.strip())
                rhs = _safe_sympify(rhs_str.strip())
                eqs.append(Eq(lhs, rhs))
            else:
                # Treat as expression = 0
                eqs.append(Eq(_safe_sympify(eq_str), 0))

        solution = solve(eqs, sym_vars, dict=True)

        if not solution:
            return "No solution found."

        # Format nicely
        lines = []
        for sol in solution:
            if isinstance(sol, dict):
                lines.append(", ".join(f"{k} = {v}" for k, v in sol.items()))
            else:
                lines.append(str(sol))
        return "Solutions: " + " | ".join(lines)

    except Exception as e:
        return f"SymPy solve error: {e}\n{traceback.format_exc(limit=2)}"


@tool
def derivative(expression: str, variable: str = "x", order: int = 1) -> str:
    """
    Differentiate a mathematical expression symbolically.

    Args:
        expression: The expression to differentiate.
                    Examples: "x^3 + 2*x^2 - 5", "sin(x)*exp(x)", "x^2 * log(x)"
        variable:   Variable to differentiate with respect to (default: "x").
        order:      Order of differentiation (default: 1 for first derivative).

    Returns:
        The derivative as a simplified string.
    """
    try:
        from sympy import diff, Symbol, simplify

        var = Symbol(variable.strip())
        expr = _safe_sympify(expression)
        result = diff(expr, var, order)
        simplified = simplify(result)
        return f"d^{order}/d{variable}^{order} ({expression}) = {simplified}"

    except Exception as e:
        return f"SymPy derivative error: {e}"


@tool
def integrate_expr(
    expression: str,
    variable: str = "x",
    lower_bound: str = "",
    upper_bound: str = "",
) -> str:
    """
    Integrate a mathematical expression symbolically (indefinite or definite).

    Args:
        expression:   The integrand expression. Example: "x^2 + 3*x"
        variable:     Integration variable (default: "x").
        lower_bound:  Lower limit for definite integral (leave empty for indefinite).
        upper_bound:  Upper limit for definite integral (leave empty for indefinite).

    Returns:
        The integral result as a string.
    """
    try:
        from sympy import integrate, Symbol, simplify, oo

        var = Symbol(variable.strip())
        expr = _safe_sympify(expression)

        if lower_bound and upper_bound:
            a = _safe_sympify(lower_bound)
            b = _safe_sympify(upper_bound)
            result = integrate(expr, (var, a, b))
            label = f"∫[{lower_bound} to {upper_bound}] ({expression}) d{variable}"
        else:
            result = integrate(expr, var)
            label = f"∫ ({expression}) d{variable}"

        return f"{label} = {simplify(result)}"

    except Exception as e:
        return f"SymPy integrate error: {e}"


@tool
def simplify_expr(expression: str) -> str:
    """
    Simplify an algebraic or trigonometric expression using SymPy.

    Args:
        expression: The expression to simplify.
                    Examples: "(x^2 - 1)/(x - 1)", "sin(x)^2 + cos(x)^2"

    Returns:
        The simplified expression as a string.
    """
    try:
        from sympy import simplify, trigsimp, factor, expand

        expr = _safe_sympify(expression)
        # Try multiple simplification strategies
        candidates = [
            simplify(expr),
            trigsimp(expr),
            factor(expr),
            expand(expr),
        ]
        # Pick the shortest string representation (usually the most simplified)
        best = min(candidates, key=lambda e: len(str(e)))
        return f"simplify({expression}) = {best}"

    except Exception as e:
        return f"SymPy simplify error: {e}"
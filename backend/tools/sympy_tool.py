import sympy as sp
from langchain_core.tools import tool

@tool
def solve_equation(equation: str) -> str:
    """Solves algebraic equations. Pass the equation as a string (e.g., 'x**2 - 4')."""
    try:
        x = sp.symbols("x")
        expr = sp.sympify(equation)
        result = sp.solve(expr, x)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def derivative(expression: str) -> str:
    """Calculates the derivative of a mathematical expression with respect to x."""
    try:
        x = sp.symbols("x")
        expr = sp.sympify(expression)
        result = sp.diff(expr, x)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

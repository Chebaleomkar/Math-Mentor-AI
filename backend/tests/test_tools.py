"""
tests/test_tools.py
--------------------
Unit tests for tools/sympy_tool.py and tools/python_tool.py.
These tools have no external dependencies — tests run fully offline.
"""
import pytest


# ── SymPy tools ───────────────────────────────────────────────────────────────

class TestSolveEquation:
    def _run(self, eq, var="x"):
        from tools.sympy_tool import solve_equation
        return solve_equation.invoke({"equation": eq, "variable": var})

    def test_linear(self):
        result = self._run("2*x + 4 = 0")
        assert "x = -2" in result or "-2" in result

    def test_quadratic_two_roots(self):
        result = self._run("x^2 - 5*x + 6 = 0")
        assert "2" in result and "3" in result

    def test_quadratic_repeated_root(self):
        result = self._run("x^2 - 2*x + 1 = 0")
        assert "1" in result

    def test_no_solution_expression(self):
        # x^2 + 1 = 0 has no real solutions but SymPy returns complex
        result = self._run("x^2 + 1 = 0")
        assert "I" in result or "i" in result or "solution" in result.lower()

    def test_system_of_equations(self):
        result = self._run("2*x + y = 5; x - y = 1", var="x,y")
        assert "2" in result and "1" in result

    def test_cubic(self):
        result = self._run("x^3 - 6*x^2 + 11*x - 6 = 0")
        # Roots are 1, 2, 3
        assert "1" in result and "2" in result and "3" in result


class TestDerivative:
    def _run(self, expr, var="x", order=1):
        from tools.sympy_tool import derivative
        return derivative.invoke({"expression": expr, "variable": var, "order": order})

    def test_polynomial(self):
        result = self._run("x^3")
        assert "3" in result and "x**2" in result or "3*x" in result

    def test_trig(self):
        result = self._run("sin(x)")
        assert "cos" in result.lower()

    def test_second_derivative(self):
        result = self._run("x^4", order=2)
        assert "12" in result or "x**2" in result

    def test_constant(self):
        result = self._run("42")
        assert "0" in result

    def test_product_rule(self):
        result = self._run("x*sin(x)")
        assert "cos" in result.lower() or "sin" in result.lower()


class TestIntegrateExpr:
    def _run(self, expr, var="x", lo="", hi=""):
        from tools.sympy_tool import integrate_expr
        return integrate_expr.invoke({
            "expression": expr, "variable": var,
            "lower_bound": lo, "upper_bound": hi,
        })

    def test_indefinite_polynomial(self):
        result = self._run("x^2")
        assert "x**3" in result or "x^3" in result or "3" in result

    def test_definite_integral(self):
        result = self._run("x", lo="0", hi="1")
        # ∫₀¹ x dx = 1/2
        assert "1/2" in result or "0.5" in result

    def test_trig_indefinite(self):
        result = self._run("cos(x)")
        assert "sin" in result.lower()


class TestSimplifyExpr:
    def _run(self, expr):
        from tools.sympy_tool import simplify_expr
        return simplify_expr.invoke({"expression": expr})

    def test_rational(self):
        result = self._run("(x^2 - 1)/(x - 1)")
        assert "x + 1" in result or "(x + 1)" in result

    def test_trig_identity(self):
        result = self._run("sin(x)^2 + cos(x)^2")
        assert "1" in result

    def test_already_simple(self):
        result = self._run("x + 1")
        assert "x + 1" in result or "x+1" in result


# ── Python sandbox tool ───────────────────────────────────────────────────────

class TestExecutePython:
    def _run(self, code):
        from tools.python_tool import execute_python
        return execute_python.invoke({"code": code})

    def test_basic_arithmetic(self):
        result = self._run("print(2 + 3)")
        assert "5" in result

    def test_factorial(self):
        result = self._run("print(factorial(6))")
        assert "720" in result

    def test_ncr(self):
        result = self._run("print(nCr(10, 3))")
        assert "120" in result

    def test_npr(self):
        result = self._run("print(nPr(5, 2))")
        assert "20" in result

    def test_math_sqrt(self):
        result = self._run("print(round(sqrt(2), 4))")
        assert "1.4142" in result

    def test_statistics(self):
        result = self._run("data=[1,2,3,4,5]; print(statistics.mean(data))")
        assert "3" in result

    def test_list_comprehension(self):
        result = self._run("print(sum(i**2 for i in range(1, 6)))")
        assert "55" in result

    def test_is_prime(self):
        result = self._run("print(is_prime(17))")
        assert "True" in result

    def test_primes_up_to(self):
        result = self._run("print(primes_up_to(10))")
        assert "2" in result and "7" in result

    def test_probability_calculation(self):
        result = self._run("print(round(nCr(52,5), 0))")
        assert "2598960" in result

    # Security tests
    def test_blocks_import(self):
        result = self._run("import os; print(os.getcwd())")
        assert "[BLOCKED]" in result

    def test_blocks_open(self):
        result = self._run("open('/etc/passwd').read()")
        assert "[BLOCKED]" in result

    def test_blocks_exec(self):
        result = self._run("exec('print(1)')")
        assert "[BLOCKED]" in result

    def test_no_output_returns_placeholder(self):
        result = self._run("x = 42")
        assert "42" in result or "x" in result

    def test_error_is_captured(self):
        result = self._run("print(1/0)")
        assert "[ERROR]" in result or "ZeroDivisionError" in result
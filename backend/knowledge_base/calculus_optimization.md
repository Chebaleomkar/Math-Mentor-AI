# Optimization and Applications of Derivatives

## Core Concepts
- **Critical Points**: Points on the graph $f(x)$ where the first derivative is zero ($f'(c) = 0$) or the first derivative is undefined. These are candidates for local maximums or minimums.
- **Absolute Extrema**: The highest or lowest value a function reaches on a given interval $[a, b]$.

## The First Derivative Test (Finding Local Extrema)
1. Find all critical points $c$ where $f'(c) = 0$ or $f'(c)$ is undefined.
2. Test points on the intervals around $c$ by plugging them into $f'(x)$.
3. Interpret signs:
   - If $f'(x)$ changes from **positive to negative** at $c$, then $f(c)$ is a **Local Maximum**.
   - If $f'(x)$ changes from **negative to positive** at $c$, then $f(c)$ is a **Local Minimum**.
   - If $f'(x)$ does not change sign, it is neither.

## The Second Derivative Test (Alternative)
Let $c$ be a critical point where $f'(c) = 0$. Evaluate the second derivative $f''(c)$:
- If $f''(c) > 0$ (Concave up), then $f(c)$ is a **Local Minimum**.
- If $f''(c) < 0$ (Concave down), then $f(c)$ is a **Local Maximum**.
- If $f''(c) = 0$, the test is inconclusive; use the First Derivative Test.

## Finding Absolute Extrema on a Closed Interval $[a, b]$ (Extreme Value Theorem)
1. Find all critical numbers $c$ of $f(x)$ inside the open interval $(a, b)$.
2. Evaluate $f(x)$ at these critical points (calculate $f(c)$).
3. Evaluate $f(x)$ at the endpoints of the interval (calculate $f(a)$ and $f(b)$).
4. **Compare**: The largest value from steps 2 & 3 is the absolute maximum. The smallest value is the absolute minimum.

## Approach for Word Problems (Optimization)
1. **Draw a Picture** (if applicable) and label variables.
2. **Identify Primary equation**: Write an equation for the quantity to be maximized or minimized (e.g., Area $A = x \cdot y$).
3. **Identify Constraint equation(s)**: Find other relations between the variables given in the problem constraints (e.g., Perimeter $= 2x + 2y = 100$).
4. **Substitute**: Use the constraint to rewrite the primary equation in terms of a **single** variable.
5. **Find Domain**: Determine the practical interval $[a, b]$ for your single variable.
6. **Find Extrema**: Differentiate the single-variable equation, set it to zero, and find absolute extrema.

## Common Mistakes
- **Forgetting Endpoints**: Forgetting to check the endpoints $a$ and $b$ when looking for absolute extrema on a closed interval.
- **Testing the wrong equation**: Plugging critical points back into $f'(x)$ instead of the original function $f(x)$ when trying to find the $y$-coordinate of the maximum/minimum.

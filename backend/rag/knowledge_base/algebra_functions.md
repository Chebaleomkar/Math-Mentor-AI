# Functions and Graphs (Algebra)

## What is a Function?
A function is a relation between a set of inputs (Domain) and a set of permissible outputs (Range) with the property that each input is related to exactly one output. 
- **Vertical Line Test**: A graph represents a function if any vertical line intersects the graph at most once.

## Function Notation and Evaluation
For $f(x) = 2x^2 - 3x + 1$:
- To evaluate $f(2)$, substitute 2 for *every* instance of $x$: $f(2) = 2(2)^2 - 3(2) + 1 = 8 - 6 + 1 = 3$.
- To evaluate $f(a+h)$, substitute $(a+h)$ entirely for $x$: $f(a+h) = 2(a+h)^2 - 3(a+h) + 1$. (Be careful to expand $(a+h)^2$ correctly!).

## Function Composition
Composition $f(g(x))$ or $(f \circ g)(x)$ means plugging the entire output of function $g$ into the input of function $f$.
1. Start from the "inside out". Find $g(x)$.
2. Substitute the expression for $g(x)$ into the independent variable for $f(x)$.

## Inverse Functions ($f^{-1}(x)$)
An inverse function reverses the effect of the original function. $f(f^{-1}(x)) = x$ and $f^{-1}(f(x)) = x$.
### How to find an inverse:
1. Replace $f(x)$ with $y$.
2. Swap $x$ and $y$ in the equation.
3. Solve algebraically for the new $y$.
4. Replace $y$ with $f^{-1}(x)$.
*Note: A function only has an inverse if it is one-to-one (passes the Horizontal Line Test).*

## Function Transformations
Given a base graph $y = f(x)$ and constants $c > 0, d > 0$:
- **Vertical Shifts**: $y = f(x) + c$ shifts UP by $c$. $y = f(x) - c$ shifts DOWN by $c$.
- **Horizontal Shifts**: $y = f(x-d)$ shifts RIGHT by $d$. $y = f(x+d)$ shifts LEFT by $d$. (Note the counter-intuitive signs!).
- **Reflections**: 
  - $y = -f(x)$ reflects vertically over the x-axis.
  - $y = f(-x)$ reflects horizontally over the y-axis.
- **Scaling / Stretching**:
  - $y = a f(x)$: Vertical stretch by $a$ (if $a>1$) or compression (if $0<a<1$).
  - $y = f(bx)$: Horizontal compression by $b$ (if $b>1$) or stretch (if $0<b<1$).

## Common Mistakes
- **Confusing notation**: $f^{-1}(x)$ means the *inverse function*, NOT $\frac{1}{f(x)}$ (which is the reciprocal).
- **Evaluating composed functions**: Simply multiplying $f(x)$ times $g(x)$ instead of plugging one completely into the other for $(f \circ g)(x)$.
- **Horizontal shifts**: Thinking $f(x+2)$ means shift right by 2. It actually means shift left by 2.

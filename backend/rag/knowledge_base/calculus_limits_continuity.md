# Limits and Continuity (Calculus)

## Core Concept: The Limit
The notation $\lim_{x \to c} f(x) = L$ means that as $x$ gets arbitrarily close to $c$ (from both sides), the value of the function $f(x)$ gets arbitrarily close to $L$.

## Properties of Limits
Assuming $\lim_{x \to c} f(x)$ and $\lim_{x \to c} g(x)$ both exist:
1. **Sum Rule**: $\lim_{x \to c} (f(x) + g(x)) = (\lim_{x \to c} f(x)) + (\lim_{x \to c} g(x))$
2. **Product Rule**: $\lim_{x \to c} (f(x) \cdot g(x)) = (\lim_{x \to c} f(x)) \cdot (\lim_{x \to c} g(x))$
3. **Quotient Rule**: $\lim_{x \to c} \frac{f(x)}{g(x)} = \frac{\lim_{x \to c} f(x)}{\lim_{x \to c} g(x)}$ (provided the denominator limit is non-zero).

## Continuity
A function $f(x)$ is continuous at a point $x = c$ if and only if **all three** of these conditions are met:
1. $f(c)$ is defined.
2. The limit $\lim_{x \to c} f(x)$ exists.
3. $\lim_{x \to c} f(x) = f(c)$.

## L'Hopital's Rule
Used for evaluating indeterminate forms like $\frac{0}{0}$ or $\frac{\infty}{\infty}$.
If $\lim_{x \to c} \frac{f(x)}{g(x)}$ yields an indeterminate form, and both $f$ and $g$ are differentiable near $c$, then:
$$ \lim_{x \to c} \frac{f(x)}{g(x)} = \lim_{x \to c} \frac{f'(x)}{g'(x)} $$
(Note: You only take the derivative of the numerator and the derivative of the denominator separately. Do **not** use the quotient rule.)

## Solution Strategy for Limit Problems
1. **Direct Substitution Attempt**: Try plugging $c$ directly into $f(x)$.
2. **If Indeterminate (e.g., $0/0$)**:
   - Try algebraic manipulation first (factoring, multiplying by conjugate, common denominator).
   - If that doesn't work or is too complex, check if conditions for L'Hopital's Rule are met and apply it.
3. **Evaluate at Infinity**: For $\lim_{x \to \infty} \frac{P(x)}{Q(x)}$ where P and Q are polynomials, compare the highest degree terms.

## Common Mistakes
- **Applying L'Hopital's without verifying indeterminate form**: L'Hopital's rule only works if the initial direct substitution yields $\frac{0}{0}$ or $\frac{\pm \infty}{\pm \infty}$. It cannot be used if the limit is, say, $\frac{3}{0}$ (this is a vertical asymptote) or $\frac{0}{3}$.
- **Taking the derivative of the entire fraction**: Using the quotient rule on the entire function instead of taking the derivative of the top and bottom separately when applying L'Hopital's rule.

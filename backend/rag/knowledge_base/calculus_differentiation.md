# Differentiation Rules and Derivatives

## What is a Derivative?
The derivative $f'(x)$ or $\frac{dy}{dx}$ represents the instantaneous rate of change of the function $f$ at point $x$. Geometrically, this is the slope of the tangent line to the curve at $x$.

## Basic Differentiation Rules
Let $c$, $n$ be constants, and $u, v$ be differentiable functions of $x$:
1. **Power Rule**: $\frac{d}{dx} (x^n) = n x^{n-1}$
2. **Constant Rule**: $\frac{d}{dx} (c) = 0$
3. **Constant Multiple Rule**: $\frac{d}{dx} [c \cdot f(x)] = c \cdot f'(x)$
4. **Sum/Difference Rule**: $\frac{d}{dx} [u \pm v] = u' \pm v'$
5. **Product Rule**: $\frac{d}{dx} [u \cdot v] = u'v + uv'$
6. **Quotient Rule**: $\frac{d}{dx} \left[ \frac{u}{v} \right] = \frac{u'v - uv'}{v^2}$
7. **Chain Rule**: For a composite function $f(g(x))$, the derivative is:
   $\frac{d}{dx} [f(g(x))] = f'(g(x)) \cdot g'(x)$

## Important Explicit Derivatives
- $\frac{d}{dx} (\sin x) = \cos x$
- $\frac{d}{dx} (\cos x) = -\sin x$
- $\frac{d}{dx} (e^x) = e^x$
- $\frac{d}{dx} (\ln x) = \frac{1}{x} \quad (x>0)$

## Solution Strategy for Complex Derivatives
1. **Identify the Outermost Structure**: Does the overall function look like a product, a quotient, or a composition of functions (chain rule)?
2. **Apply Rules Outside-In**: Start with the overarching rule, then work your way inward.
3. **Write Down In-between Steps**: Calculate $u, u', v, v'$ individually instead of doing all the mental math at once.
4. **Simplify Result**: Combine like terms after applying the rules.

## Common Mistakes
- **Forgetting the Chain Rule**: (e.g., differentiating $e^{3x}$ as just $e^{3x}$ instead of $3e^{3x}$).
- **Messing up signs in the Quotient Rule**: The quotient rule has a Minus sign in the numerator ($u'v - uv'$); order matters!

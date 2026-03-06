# Basic Integration (Calculus)

## What is an Integral?
An indefinite integral (anti-derivative) reverses the process of differentiation. The result is a family of functions, represented by $+ C$ (the constant of integration).
A definite integral calculates the signed area under a curve between two limits $x=a$ and $x=b$.

## Basic Integration Rules
Let $C$, $k$, and $n$ be constants.
1. **Power Rule**: $\int x^n \, dx = \frac{x^{n+1}}{n+1} + C \quad$ (for $n \neq -1$)
2. **$1/x$ Rule**: $\int \frac{1}{x} \, dx = \ln|x| + C \quad$ (Notice the absolute value bars!)
3. **Exponential Rule**: $\int e^x \, dx = e^x + C$
4. **Constant Multiple Rule**: $\int k \cdot f(x) \, dx = k \int f(x) \, dx$
5. **Sum/Difference Rule**: $\int (f(x) \pm g(x)) \, dx = \int f(x) \, dx \pm \int g(x) \, dx$

## Trigonometric Integrals
- $\int \sin(x) \, dx = -\cos(x) + C$
- $\int \cos(x) \, dx = \sin(x) + C$
- $\int \sec^2(x) \, dx = \tan(x) + C$

## The Fundamental Theorem of Calculus (Definite Integrals)
If $F(x)$ is the anti-derivative of $f(x)$ (meaning $F'(x) = f(x)$), then:
$$ \int_a^b f(x) \, dx = F(b) - F(a) $$

## Method of Substitution (U-Substitution)
Used for reversing the Chain Rule. It is useful when you have an integrand containing both a function and its derivative.
1. Choose $u$. Set $u$ equal to the 'inner' function or the function whose derivative is also present in the integrand.
2. Find $du$. Take the derivative of $u$ with respect to $x$, so $du = u' \, dx$.
3. Substitute. Replace $x$ and $dx$ entirely with $u$ and $du$.
4. Integrate with respect to $u$.
5. Back-substitute. Replace $u$ with the original $x$ expression. (Don't forget $+ C$ for indefinite integrals!).

## Common Mistakes
- **Forgetting the $+ C$**: Every indefinite integral requires a constant of integration.
- **Using the power rule incorrectly for $n=-1$**: $\int x^{-1} dx$ is NOT $\frac{x^0}{0}$, it is $\ln|x| + C$.
- **Not changing bounds during U-Sub**: If evaluating a definite integral using u-substitution, you must either change the bounds $a$ and $b$ from $x$-values to $u$-values, or wait until you back-substitute $x$ before applying the original bounds.

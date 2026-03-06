# Universal Common Math Pitfalls 

This guide outlines errors that frequently trip up students across multiple domains of mathematics. As a Solver/Verifier, actively check the solution steps against these common mistakes.

## 1. The Phantom Distribution (Algebraic Misconceptions)
Students often try to "distribute" operations over addition/subtraction where it's mathematically illegal.
- **Squaring a Binomial**: $(x + y)^2 \neq x^2 + y^2$. The correct expansion is $(x + y)^2 = x^2 + 2xy + y^2$.
- **Square Roots**: $\sqrt{x^2 + y^2} \neq x + y$.
- **Fractions**: $\frac{a}{b + c} \neq \frac{a}{b} + \frac{a}{c}$.

## 2. Division by Zero
- Never divide by a variable without stipulating that the variable cannot be zero.
- e.g., Solving $x^2 = x$ by dividing by $x$ to get $x = 1$. This *loses* the solution $x = 0$. You must factor instead: $x^2 - x = 0 \Rightarrow x(x - 1) = 0$.

## 3. Extraneous Solutions in Equations
Equations involving square roots, logarithms, or absolute values often produce "false" solutions that don't satisfy the original equation.
- **Square Roots**: Squaring both sides of an equation (e.g., $\sqrt{x} = -2 \Rightarrow x = 4$) introduces answers that fail the original check. The principle square root function $\sqrt{x}$ only produces non-negative numbers.
- **Always verify all final solutions by plugging them back into the original, unmodified problem statement.**

## 4. Inequality Flipping
- If you multiply or divide both sides of an inequality by a **negative** number, you MUST flip the direction of the inequality sign.
- e.g., $-2x > 4 \Rightarrow x < -2$

## 5. Domain Restrictions
- **Square Roots**: The argument under an even root must be $\ge 0$. (Unless working in complex numbers).
- **Logarithms**: The argument of a logarithm must be strictly $> 0$.
- **Fractions**: Denominators cannot equal zero.

## 6. Parentheses and Order of Operations (PEMDAS)
- $-3^2 \neq (-3)^2$. The first evaluates to $-9$ (the negative is applied *after* squaring). The second evaluates to $9$.
- Be explicit about parentheses when applying functions. $f(x+h)$ means substituting $(x+h)$ entirely wherever $x$ appeared in $f(x)$.

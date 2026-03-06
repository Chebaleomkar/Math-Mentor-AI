# Unit and Domain Constraints in Mathematics

## 1. Mathematical Domain Constraints
When solving equations, always check if the final answers fall within the permissible domain of the original functions involved.
- **Fractions / Rational Functions**: The denominator can never be equal to 0. If a solution causes a denominator in the original equation to be 0, it is an extraneous solution and must be discarded.
- **Even Roots (Square Root, 4th Root)**: The expression under the radical (the radicand) must be greater than or equal to 0 for the output to be a real number. If a solution makes the radicand negative, it is an extraneous real solution.
- **Logarithms**: The argument of any logarithmic function $\log_b(x)$ must be strictly positive ($x > 0$). Furthermore, the base $b$ must be $b > 0$ and $b \neq 1$.
- **Trigonometric Functions**: 
  - $\tan(x)$ and $\sec(x)$ are undefined for $x = \frac{\pi}{2} + k\pi$ (where $k$ is an integer).
  - Inverse sine ($\arcsin x$) and inverse cosine ($\arccos x$) ONLY accept inputs in the range $[-1, 1]$.

## 2. Physical Unit Constraints (Word Problems)
When a math problem represents a real-world physical scenario, ensure the final answers make logical sense given the context.
- **Time ($t$)**: Usually strictly non-negative ($t \ge 0$). A solution of $t = -5$ seconds when a ball hits the ground should be discarded.
- **Distance / Length / Area / Volume**: Must be non-negative. You cannot have a triangle with a side length of -3 cm.
- **Objects / People**: Counts of discrete physical objects (coins, people, cars) must be non-negative integers. If an expected value or equation yields 2.5 people, the problem either demands rounding or indicates an error in setup.
- **Probability**: Any calculated probability must ALWAYS satisfy $0 \le P(A) \le 1$. A probability of 1.2 or -0.5 is mathematically impossible and indicates a calculation error.

## 3. Verifier Checklist for Constraints
1. Does the answer trigger a division by zero in the initial prompt?
2. Does the answer result in taking the log or even root of a negative baseline?
3. Does the physical unit logically permit negative numbers?
4. Are the units consistent throughout the equation? (e.g., don't add meters to centimeters without converting first).

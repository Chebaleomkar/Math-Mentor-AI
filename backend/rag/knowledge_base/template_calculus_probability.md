# Solution Template: Calculus and Probability

This template defines the structured path an AI Solver Agent should follow to reliably produce step-by-step solutions for calculus optimization, limits, derivatives, and complex probability scenarios.

## Step 1: Theoretical Framework Identification
- **Action**: Identify exactly what mathematical theorem or rule governs the problem.
- **Calculus Example**: "This is a limit of the form 0/0. We must use L'Hopital's Rule."
- **Probability Example**: "This asks for the probability of A given B. We will use Bayes' Theorem."

## Step 2: Given Values Extraction
- **Action**: List out the given scalar values or base functions explicitly before touching them.
- **Calculus Example**: "$f(x) = \frac{\sin(x)}{x}$, evaluating at $c = 0$."
- **Probability Example**: "$P(\text{Disease}) = 0.01$, $P(\text{Positive}|\text{Disease}) = 0.99$."

## Step 3: Formula Setup
- **Action**: Write the abstract mathematical formula *before* plugging in any contextual numbers.
- **Calculus Example**: "L'Hopital's Rule states $\lim \frac{f(x)}{g(x)} = \lim \frac{f'(x)}{g'(x)}$"
- **Probability Example**: "$P(D|Pos) = \frac{P(Pos|D) \cdot P(D)}{P(Pos)}$"

## Step 4: Step-by-Step Calculation
- **Action**: Perform the derivatives, integrations, or arithmetic operations line by line.
- **Line 1 (Numerator Derivative)**: $f'(x) = \cos(x)$
- **Line 2 (Denominator Derivative)**: $g'(x) = 1$
- **Line 3 (Substitution)**: $P(Pos) = (0.99 \cdot 0.01) + (0.05 \cdot 0.99)$ -> requires Law of Total Probability expansion.

## Step 5: Simplification
- **Action**: Reduce fractions, exact radical forms, or standard decimal formats (depending on what the problem asks).
- **Calculation**: $\cos(0) / 1 = 1$.

## Step 6: Final Answer and Interpretation
- **Action**: State the final answer. If it is probability, make sure it is $0 \le p \le 1$. If it is a derivative, specify the units (e.g., "meters per second").
- **Output**: "The limit is 1." OR "The probability of having the disease given a positive test is 16.5%."

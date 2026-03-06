# Basic Probability and Expected Value

## Standard Definitions
- **Sample Space (S)**: The set of all possible outcomes.
- **Event (E)**: A clearly defined set of outcomes (a subset of S).
- **Probability of Event E ($P(E)$)**: 
  $$P(E) = \frac{\text{Number of favorable outcomes}}{\text{Total number of possible outcomes}}$$

## Core Axioms
1. For any event A, $0 \le P(A) \le 1$.
2. The probability of the sample space S is $1$ ($P(S) = 1$).
3. If events A and B are mutually exclusive (they cannot happen at exactly the same time), then $P(A \cup B) = P(A) + P(B)$.

## Random Variables and Expected Value ($E(X)$)
A discrete random variable ($X$) has a set of possible values ($x_1, x_2, ... x_n$) with corresponding probabilities ($P(x_1), P(x_2), ... P(x_n)$).

The **Expected Value**, $E(X)$, is the long-run average of the random variable:
$$E(X) = \Sigma [x_i \cdot P(x_i)] = (x_1 \cdot P(x_1)) + (x_2 \cdot P(x_2)) + ... + (x_n \cdot P(x_n))$$

## Variance ($Var(X)$)
The Variance measures how much the values are spread out from the expected value.
$$Var(X) = E((X - E[X])^2) = E(X^2) - (E(X))^2$$

## Solution Strategy for Expected Value Problems
1. **Identify the Random Variable**: Define what numerical value $X$ represents (e.g., amount of money won, number of heads).
2. **List All Possible Outcomes ($x_i$)**: Determine exactly what values $X$ can take.
3. **Determine Probabilities ($P(x_i)$)**: Calculate the probability of each outcome occurring.
4. **Verify Total Probability**: Ensure that $\Sigma P(x_i) = 1$.
5. **Calculate Expected Value**: Multiply each outcome ($x_i$) by its probability ($P(x_i)$) and sum the results.

## Common Mistakes
- **Failing to check $\Sigma P(x_i) = 1$**: This is the best way to catch mathematical errors in probabilities early on.
- **Confusing discrete vs continuous random variables**: In continuous problems, you integrate a probability density function rather than sum a probability mass function.

# Conditional Probability and Bayes' Theorem

## Definitions
- **$P(A|B)$**: The probability of event A happening *given* that event B has already happened.
- **$P(A \cap B)$**: The probability of both A and B happening simultaneously.

## Conditional Probability Formula
$$P(A|B) = \frac{P(A \cap B)}{P(B)}$$  (where $P(B) > 0$)

## Multiplication Rule
$$P(A \cap B) = P(A|B) \cdot P(B) = P(B|A) \cdot P(A)$$

## Bayes' Theorem
Used to reverse the direction of conditionality:
$$P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$$

### Law of Total Probability (Often needed for the denominator $P(B)$)
If $A_1, A_2, ..., A_n$ form a mutually exclusive and exhaustive partition of the sample space:
$$P(B) = P(B|A_1)P(A_1) + P(B|A_2)P(A_2) + ... + P(B|A_n)P(A_n)$$

## Solution Strategy for Bayes Theorem Word Problems
1. **Define Events**: Clearly label what event A, event B, etc. represent.
2. **Identify Given Probabilities**: Extract $P(A)$, $P(B|A)$, etc. from the problem text.
3. **Determine the Goal**: What conditional probability are you trying to find? (e.g., $P(A|B)$).
4. **Calculate Total Probability**: Calculate the denominator $P(B)$ using the Law of Total Probability if it's not given directly.
5. **Apply Bayes' Formula**: Plug in the values and solve.

## Common Mistakes
- **Confusing $P(A|B)$ with $P(B|A)$**: Pay close attention to the wording "given that", "if", or "knowing that".
- **Assuming Independence**: Assuming $P(A \cap B) = P(A)P(B)$ when the events are actually dependent. Only true if A and B are independent.

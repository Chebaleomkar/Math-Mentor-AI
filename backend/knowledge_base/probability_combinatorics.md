# Combinatorics: Permutations and Combinations

## Core Concepts
- **Permutations ($P$)**: Ordered arrangements. The order matters (e.g., arranging letters, picking a President and VP).
- **Combinations ($C$)**: Unordered selections. The order does NOT matter (e.g., picking a committee of 3 people from 10).

## Formulas
Let $n$ be the total number of items, and $r$ be the number of items chosen.
- **Factorial**: $n! = n \times (n-1) \times (n-2) \times ... \times 1$ (Note: $0! = 1$)
- **Permutations Formula**: $$^nP_r = \frac{n!}{(n-r)!}$$
- **Combinations Formula**: $$^nC_r = \binom{n}{r} = \frac{n!}{r!(n-r)!}$$

## Special Cases
- **Arrangements with Repetition**: Total arrangements of $n$ items where $p$ are of one type, $q$ of another, etc., is $\frac{n!}{p!q!...}$
- **Circular Permutations**: Arranging $n$ distinct items in a circle is $(n-1)!$

## Solution Strategy for Word Problems
1. **Determine if Order Matters**: Ask "Does $AB$ count as a different outcome than $BA$?". If yes $\rightarrow$ Permutation. If no $\rightarrow$ Combination.
2. **Identify $n$ and $r$**: What is the total pool, and how many are being selected?
3. **Check for "AND/OR" limits**: 
   - Operations linked by "AND" usually mean you multiply the outcomes.
   - Operations linked by "OR" (mutually exclusive) usually mean you add the outcomes.
   
## Common Mistakes
- **Wrong Formula**: Using Permutations for a Combination problem or vice-versa.
- **Overcounting**: Forgetting to divide by redundancies in arrangements with repeating identical items (like arranging the letters in MISSISSIPPI).

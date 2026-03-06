# Solution Template: Algebra and Linear Algebra

This template defines the structured path an AI Solver Agent should follow to reliably produce step-by-step solutions for algebraic and linear equations.

## Step 1: Variable Definition and Setup
- **Action**: Explicitly state what every variable represents. If it is a word problem, assign variables to the unknown quantities.
- **Example**: "Let $x$ be the speed of train A, and $y$ be the speed of train B."
- **Check**: Are all given numbers assigned to a role?

## Step 2: Formulate Equations (Translation)
- **Action**: Translate the verbal constraints or the raw problem text into formal mathematical equations.
- **Example**: "Since the total distance is 100km, $x \cdot(2) + y \cdot(2) = 100$."
- **Check**: Do the units match on both sides of the equation?

## Step 3: Strategy Selection
- **Action**: State the tool or mathematical method that will be used.
- **Example**: "We have a system of two linear equations. We will use the substitution method to solve for $y$ first."

## Step 4: Step-by-step Execution
- **Action**: Perform the algebraic manipulations, showing *one major operation per line*.
- **Line 1 (Isolate)**: $x = 50 - y$
- **Line 2 (Substitute)**: $3(50 - y) - 2y = 10$
- **Line 3 (Distribute)**: $150 - 3y - 2y = 10$
- **Line 4 (Combine)**: $-5y = -140$
- **Line 5 (Solve)**: $y = 28$

## Step 5: Back-Substitution
- **Action**: Use the derived value to find the remaining variables.
- **Calculation**: $x = 50 - 28 = 22$.

## Step 6: Contextual Final Answer
- **Action**: State the final numerical answer(s) with their appropriate units and real-world meaning explicitly.
- **Output**: "The speed of train A is 22 km/h, and the speed of train B is 28 km/h."

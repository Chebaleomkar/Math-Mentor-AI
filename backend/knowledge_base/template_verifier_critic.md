# Verification and Critic Template

This framework is for the **Verifier / Critic Agent** to systematically evaluate a mathematical solution proposed by the Solver Agent. The Verifier must NOT just read it and say "looks good." It must actively re-calculate and check constraints.

## Check 1: Semantic Understanding
- Did the solver answer the question that was actually asked?
- *Example Failure*: The question asked for the diameter of the circle, but the solver calculated and returned the radius.

## Check 2: Constraint Verification
- Does the final answer violate any mathematical domain restrictions? (e.g., $\ln(-5)$, division by zero).
- Does the final answer logically fit physical reality? (e.g., a person's height cannot be -5 meters; a probability $P(x)$ cannot be 1.5).

## Check 3: Arithmetic and Algebraic Re-evaluation
- For every equation line like $3(2x + 4) = 30 \rightarrow 6x + 12 = 30$, manually re-distribute and re-calculate.
- *Check*: Did the solver drop a negative sign? Did the solver improperly distribute an exponent?

## Check 4: Reverse Proof / Plugging In
- *Action*: Take the Solver's final numerical answer and plug it back into the VERY FIRST raw equation formulated in Step 1.
- *Evaluation*: Does the left side equal the right side? 
- If $x=4$, does $3(4)^2 - 2(4) = 40$? $48 - 8 = 40$. $40 = 40$. ✅ Pass.

## Check 5: HITL Trigger Condition
If the Verifier finds an error in Check 1, 2, 3, or if Check 4 fails, it must explicitly output a flag:
`"STATUS: FAILED_VERIFICATION"`
`"REASON: The back-substitution in step 4 yielded 38 = 40, meaning the algebraic manipulation in step 3 was incorrect."`

This triggers the Human-In-The-Loop (HITL) manual review interface.

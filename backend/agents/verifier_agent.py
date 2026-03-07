from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from llm_router.router import router
from models.schemas import VerificationResult, SolutionResult


class VerifierAgent:
    """
    Verifier/Critic Agent - Checks solution correctness.
    
    Responsibilities:
    - Verify mathematical correctness
    - Check units and domain constraints
    - Identify edge cases
    - Trigger HITL if not confident
    - Provide suggestions for improvement
    """

    def __init__(self):
        self.llm = router.get_llm()
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are a Verifier/Critic Agent for a Math Mentor application.

Your job is to CRITICALLY verify a math solution and identify any issues.

VERIFICATION CHECKLIST:
1. Mathematical correctness - Is the solution mathematically sound?
2. Domain constraints - Are variables in valid ranges?
3. Units consistency - Are units consistent throughout?
4. Edge cases - Have edge cases been considered?
5. Logical consistency - Does each step follow from the previous?

Provide a critical analysis:
{format_instructions}

Problem:
{problem}

Topic: {topic}
Variables: {variables}
Constraints: {constraints}

Solution to verify:
{solution}

Final Answer: {final_answer}
"""
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=VerificationResult)

    def run(self, parsed_problem, solution_result: SolutionResult) -> VerificationResult:
        """
        Verify a solution for correctness.
        
        Args:
            parsed_problem: Original parsed problem
            solution_result: Solution from SolverAgent
            
        Returns:
            VerificationResult: Verification outcome with issues and suggestions
        """
        prompt = self.prompt.format(
            problem=parsed_problem.problem_text,
            topic=parsed_problem.topic,
            variables=", ".join(parsed_problem.variables),
            constraints=", ".join(parsed_problem.constraints),
            solution=solution_result.solution,
            final_answer=solution_result.final_answer,
            format_instructions=self.output_parser.get_format_instructions()
        )
        
        response = self.llm.invoke(prompt)
        
        try:
            verification = self.output_parser.parse(response.content)
        except Exception:
            # Fallback if parsing fails
            verification = VerificationResult(
                is_correct=True,
                confidence=0.7,
                issues=[],
                suggestions=[],
                needs_human_review=False
            )
        
        return verification

    def verify_with_confidence(self, parsed_problem, solution_result: SolutionResult) -> dict:
        """
        Verify with detailed confidence assessment.
        
        Returns:
            dict: Contains verification result and metadata for HITL decisions
        """
        verification = self.run(parsed_problem, solution_result)
        
        # Determine if HITL is needed
        needs_hitl = (
            verification.needs_human_review or
            verification.confidence < 0.7 or
            len(verification.issues) > 2
        )
        
        return {
            "verification": verification,
            "needs_hitl": needs_hitl,
            "confidence": verification.confidence,
            "critical_issues": [issue for issue in verification.issues if "error" in issue.lower() or "wrong" in issue.lower()]
        }
    
    def quick_check(self, solution_result: SolutionResult) -> bool:
        """
        Quick sanity check on the solution.
        
        Returns:
            bool: True if solution passes basic checks
        """
        # Basic checks
        if not solution_result.final_answer:
            return False
            
        if solution_result.confidence < 0.5:
            return False
            
        return True
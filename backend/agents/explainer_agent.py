from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from llm_router.router import router
from models.schemas import ExplanationResult, SolutionResult


class ExplainerAgent:
    """
    Explainer/Tutor Agent - Produces student-friendly step-by-step explanations.
    
    Responsibilities:
    - Generate clear, step-by-step explanations
    - Identify key concepts being used
    - Provide tips and tricks for similar problems
    - Make the solution accessible to students
    """

    def __init__(self):
        self.llm = router.get_llm()
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are an Explainer/Tutor Agent for a Math Mentor application.

Your job is to provide a STUDENT-FRIENDLY explanation of a math solution.

STYLE REQUIREMENTS:
- Use clear, simple language
- Explain the "why" behind each step
- Break down complex concepts into smaller pieces
- Use analogies where helpful
- Highlight key formulas and concepts

CONTENT REQUIRED:
1. Key concepts involved
2. Step-by-step explanation (numbered)
3. Tips for similar problems

{format_instructions}

Problem:
{problem}

Solution:
{solution}

Final Answer: {final_answer}

Topic: {topic}
"""
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=ExplanationResult)

    def run(self, parsed_problem, solution_result: SolutionResult) -> ExplanationResult:
        """
        Generate a student-friendly explanation.
        
        Args:
            parsed_problem: Original parsed problem
            solution_result: Solution from SolverAgent
            
        Returns:
            ExplanationResult: Student-friendly explanation
        """
        prompt = self.prompt.format(
            problem=parsed_problem.problem_text,
            solution=solution_result.solution,
            final_answer=solution_result.final_answer,
            topic=parsed_problem.topic,
            format_instructions=self.output_parser.get_format_instructions()
        )
        
        response = self.llm.invoke(prompt)
        
        try:
            explanation = self.output_parser.parse(response.content)
        except Exception:
            # Fallback if parsing fails - create basic explanation
            explanation = ExplanationResult(
                explanation=solution_result.solution,
                key_concepts=[parsed_problem.topic],
                step_by_step=solution_result.steps,
                tips=["Practice similar problems to improve.", "Review the underlying concepts."]
            )
        
        return explanation

    def explain_with_context(self, parsed_problem, solution_result: SolutionResult, retrieved_context: list = None) -> ExplanationResult:
        """
        Generate explanation with additional context from RAG.
        
        Args:
            parsed_problem: Original parsed problem
            solution_result: Solution from SolverAgent
            retrieved_context: Optional context from RAG retrieval
            
        Returns:
            ExplanationResult: Enhanced explanation with context
        """
        # Add context to the prompt if available
        context_info = ""
        if retrieved_context:
            context_info = "\n\nAdditional Reference Material:\n" + "\n".join(retrieved_context[:2])
        
        prompt = self.prompt.format(
            problem=parsed_problem.problem_text,
            solution=solution_result.solution + context_info,
            final_answer=solution_result.final_answer,
            topic=parsed_problem.topic,
            format_instructions=self.output_parser.get_format_instructions()
        )
        
        response = self.llm.invoke(prompt)
        
        try:
            explanation = self.output_parser.parse(response.content)
        except Exception:
            explanation = ExplanationResult(
                explanation=solution_result.solution,
                key_concepts=[parsed_problem.topic],
                step_by_step=solution_result.steps,
                tips=["Review the reference material for more context."]
            )
        
        return explanation

    def generate_tips(self, topic: str) -> list:
        """
        Generate tips for a specific topic.
        
        Args:
            topic: The math topic (algebra, calculus, etc.)
            
        Returns:
            list: Tips for the topic
        """
        tip_prompt = f"""Give me 5 helpful tips for solving {topic} problems. 
        Keep each tip concise (one line)."""
        
        response = self.llm.invoke(tip_prompt)
        
        # Parse tips from response
        tips = [line.strip() for line in response.content.split('\n') if line.strip()]
        
        return tips[:5]
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from llm_router.router import router
from models.schemas import WorkflowPlan


class IntentRouterAgent:
    """
    Intent Router Agent - Classifies problem type and routes workflow.
    
    Responsibilities:
    - Classify the problem type (algebra, calculus, probability, etc.)
    - Determine complexity level (simple, medium, complex)
    - Plan the solution strategy
    - Route to appropriate sub-agents/tools
    """

    def __init__(self):
        self.llm = router.get_llm()
        
        self.prompt = ChatPromptTemplate.from_template(
            """You are an Intent Router for a Math Mentor application.
            
Your job is to analyze a math problem and create an optimal solution plan.

ANALYSIS REQUIRED:
1. Classify the problem topic: algebra, calculus, probability, linear_algebra, geometry, trigonometry
2. Determine complexity: simple (one-step), medium (multi-step), complex (requires multiple tools/techniques)
3. Identify required techniques/formulas
4. Plan the solution approach

Respond with JSON:
{format_instructions}

Problem:
{problem_text}

Topic: {topic}
Variables: {variables}
Constraints: {constraints}
"""
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=WorkflowPlan)

    def run(self, parsed_problem) -> WorkflowPlan:
        """
        Route the problem to determine the best solution strategy.
        
        Args:
            parsed_problem: ParsedProblem from ParserAgent
            
        Returns:
            WorkflowPlan: Complete routing and plan information
        """
        prompt = self.prompt.format(
            problem_text=parsed_problem.problem_text,
            topic=parsed_problem.topic,
            variables=", ".join(parsed_problem.variables),
            constraints=", ".join(parsed_problem.constraints),
            format_instructions=self.output_parser.get_format_instructions()
        )
        
        response = self.llm.invoke(prompt)
        workflow_plan = self.output_parser.parse(response.content)
        
        return workflow_plan

    def get_routing(self, parsed_problem) -> dict:
        """
        Get routing decision with metadata for the agent system.
        
        Returns:
            dict: Contains routing decision and metadata
        """
        workflow = self.run(parsed_problem)
        
        return {
            "workflow": workflow,
            "routing": {
                "primary_topic": workflow.primary_topic,
                "complexity": workflow.complexity,
                "requires_tools": workflow.requires_tools,
                "estimated_steps": workflow.estimated_steps
            },
            "agent_sequence": self._determine_agent_sequence(workflow)
        }
    
    def _determine_agent_sequence(self, workflow: WorkflowPlan) -> list:
        """
        Determine which agents should be invoked and in what order.
        """
        sequence = ["parser"]  # Already done
        
        if workflow.complexity in ["medium", "complex"]:
            sequence.append("solver")  # Main solver
            
            if workflow.requires_verification:
                sequence.append("verifier")  # Verify solution
            else:
                sequence.append("explainer")  # Direct to explanation
        else:
            sequence.append("solver")
            sequence.append("explainer")  # Simple problems go straight to explanation
            
        return sequence

        
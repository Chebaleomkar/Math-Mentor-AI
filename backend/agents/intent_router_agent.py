from langchain_core.prompts import ChatPromptTemplate
from llm_router.router import router


class IntentRouterAgent:
    """
    Intent Router Agent - Classifies problem type and routes workflow.
    """

    def __init__(self):
        self.llm = router.get_llm()

        self.prompt = ChatPromptTemplate.from_template(
            """You are an Intent Router for a Math Mentor application.

Analyze the math problem and determine routing.

Return JSON with:
primary_topic
complexity
requires_tools
estimated_steps
requires_verification

Problem:
{problem_text}

Topic: {topic}
Variables: {variables}
Constraints: {constraints}
"""
        )

    def run(self, parsed_problem):

        prompt = self.prompt.format(
            problem_text=parsed_problem.problem_text,
            topic=parsed_problem.topic,
            variables=", ".join(parsed_problem.variables),
            constraints=", ".join(parsed_problem.constraints),
        )

        response = self.llm.invoke(prompt)

        # simple JSON parsing
        import json
        workflow = json.loads(response.content)

        return workflow

    def get_routing(self, parsed_problem) -> dict:

        workflow = self.run(parsed_problem)

        return {
            "routing": {
                "primary_topic": workflow.get("primary_topic"),
                "complexity": workflow.get("complexity"),
                "requires_tools": workflow.get("requires_tools"),
                "estimated_steps": workflow.get("estimated_steps")
            },
            "agent_sequence": self._determine_agent_sequence(workflow)
        }

    def _determine_agent_sequence(self, workflow) -> list:

        sequence = ["parser"]

        complexity = workflow.get("complexity", "simple")
        verify = workflow.get("requires_verification", False)

        sequence.append("solver")

        if complexity in ["medium", "complex"] and verify:
            sequence.append("verifier")

        sequence.append("explainer")

        return sequence
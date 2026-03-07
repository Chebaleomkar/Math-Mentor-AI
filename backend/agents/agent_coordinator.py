"""Agent Coordinator - Orchestrates the multi-agent workflow for Math Mentor.

Flow: Parser → Intent Router → Solver → Verifier → Explainer
Includes Memory & Self-Learning integration.
"""

from .parser_agent import ParserAgent
from .intent_router_agent import IntentRouterAgent
from .solver_agent import SolverAgent
from .verifier_agent import VerifierAgent
from .explainer_agent import ExplainerAgent

from memory import MemoryStore, MemoryRetriever, MemoryEntry
from memory.pattern_matcher import PatternMatcher

from models.schemas import ParsedProblem, WorkflowPlan, SolutionResult, VerificationResult, ExplanationResult


class AgentCoordinator:
    """
    Orchestrates the multi-agent system.
    
    Coordinates the flow: Parser → Router → Solver → Verifier → Explainer
    Handles HITL triggers and error handling.
    Integrates Memory & Self-Learning.
    """

    def __init__(self):
        self.parser = ParserAgent()
        self.router = IntentRouterAgent()
        self.solver = SolverAgent()
        self.verifier = VerifierAgent()
        self.explainer = ExplainerAgent()
        
        # Initialize memory components
        self.memory_store = MemoryStore()
        self.memory_retriever = MemoryRetriever()
        self.pattern_matcher = PatternMatcher()

    def _get_verification_result(self, verification) -> dict:
        """Extract verification result dict from various formats."""
        if isinstance(verification, dict):
            return {
                "is_correct": verification.get("is_correct", True),
                "confidence": verification.get("confidence", 0.5),
            }
        elif hasattr(verification, "is_correct"):
            return {
                "is_correct": verification.is_correct,
                "confidence": verification.confidence,
            }
        return {"is_correct": True, "confidence": 0.5}

    def solve_problem(self, question: str) -> dict:
        """
        Main entry point - solve a math problem through the full agent pipeline.
        
        Args:
            question: Raw question from user (text/OCR/ASR)
            
        Returns:
            dict: Complete result with all agent outputs
        """
        result = {
            "status": "pending",
            "question": question,
            "hits": []
        }
        
        # Step 1: Parse the question
        try:
            parsed = self.parser.run(question)
            result["parsed"] = parsed
            result["hits"].append("parser")
            
            # Check if we need HITL after parsing
            if parsed.needs_clarification:
                result["status"] = "needs_clarification"
                result["message"] = "Parser detected ambiguous content. Human review needed."
                return result
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = f"Parser error: {str(e)}"
            return result
        
        # Step 1.5: Query memory for similar problems (NEW)
        try:
            memory_context = self.memory_retriever.get_memory_context(
                problem_text=question,
                topic=parsed.topic,
                n_similar=3
            )
            result["memory"] = memory_context
            result["hits"].append("memory_lookup")
        except Exception as e:
            result["memory"] = {"has_memory": False, "context": "", "error": str(e)}
        
        # Step 2: Route the problem
        try:
            routing = self.router.get_routing(parsed)
            result["routing"] = routing
            result["hits"].append("router")
        except Exception as e:
            # Continue without routing - use defaults
            result["routing"] = {"routing": {"complexity": "medium", "requires_verification": True}}
        
        # Step 3: Solve the problem (with memory context)
        try:
            solution = self.solver.run(parsed, memory_context=result.get("memory", {}))
            result["solution"] = solution
            result["hits"].append("solver")
        except Exception as e:
            result["status"] = "error"
            result["error"] = f"Solver error: {str(e)}"
            return result
        
        # Step 4: Verify the solution (if complexity requires it)
        routing_info = result.get("routing", {}).get("routing", {})
        if routing_info.get("requires_verification", True):
            try:
                verification = self.verifier.run(parsed, solution)
                result["verification"] = verification
                result["hits"].append("verifier")
                
                # Check if verification failed - might need HITL
                if verification.needs_human_review or verification.confidence < 0.6:
                    result["status"] = "needs_review"
                    result["message"] = "Verification flagged for human review."
            except Exception as e:
                result["verification"] = {"is_correct": True, "confidence": 0.5, "issues": [str(e)]}
        
        # Step 5: Generate explanation
        try:
            explanation = self.explainer.run(parsed, solution)
            result["explanation"] = explanation
            result["hits"].append("explainer")
        except Exception as e:
            sol = result.get("solution", {})
            result["explanation"] = {"explanation": sol.get("solution", "Error generating explanation")}
        
        # Step 6: Save to memory (NEW)
        try:
            # Get verification result properly
            verification = result.get("verification")
            ver_result = self._get_verification_result(verification)
            
            memory_entry = MemoryEntry(
                original_input=question,
                parsed_question={
                    "topic": parsed.topic,
                    "variables": parsed.variables,
                    "constraints": parsed.constraints,
                },
                retrieved_context=memory_context.get("context", ""),
                final_answer=solution.get("final_answer", ""),
                verifier_outcome=ver_result,
                topic=parsed.topic,
                complexity=routing_info.get("complexity", "medium"),
            )
            memory_id = self.memory_store.add_entry(memory_entry)
            result["memory_id"] = memory_id
            result["hits"].append("memory_save")
        except Exception as e:
            result["memory_save_error"] = str(e)
        
        # Final status
        if result["status"] == "pending":
            result["status"] = "success"
            
        return result
    
    def solve_simple(self, question: str) -> dict:
        """
        Fast path for simple problems - skip verification.
        
        Args:
            question: Raw question from user
            
        Returns:
            dict: Result with parser, solver, and explainer
        """
        result = {"question": question}
        
        # Parse
        parsed = self.parser.run(question)
        result["parsed"] = parsed
        
        # Query memory
        memory_context = self.memory_retriever.get_memory_context(
            problem_text=question,
            topic=parsed.topic,
            n_similar=2
        )
        result["memory"] = memory_context
        
        # Solve
        solution = self.solver.run(parsed, memory_context=memory_context)
        result["solution"] = solution
        
        # Explain
        explanation = self.explainer.run(parsed, solution)
        result["explanation"] = explanation
        
        result["status"] = "success"
        return result
    
    def verify_only(self, question: str, solution_text: str) -> dict:
        """
        Verify an existing solution (for HITL review).
        
        Args:
            question: The original problem
            solution_text: The solution to verify
            
        Returns:
            dict: Verification result
        """
        parsed = self.parser.run(question)
        
        # Create a moc

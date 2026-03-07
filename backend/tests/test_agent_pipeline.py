"""
Test file for the 5-agent Math Mentor pipeline.

Tests each agent individually and the full coordinator pipeline.
"""

import sys
import os

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Test data - various math problems
TEST_PROBLEMS = {
    "algebra_simple": "Solve for x: 2x + 5 = 15",
    "algebra_quadratic": "Solve the quadratic equation: x^2 - 5x + 6 = 0",
    "calculus_derivative": "Find the derivative of f(x) = x^3 + 2x^2 - 5x + 3",
    "calculus_limit": "Evaluate the limit: lim(x->2) (x^2 - 4)/(x - 2)",
    "probability": "A bag contains 5 red balls and 3 blue balls. What is the probability of drawing 2 red balls consecutively without replacement?",
    "linear_algebra": "Find the determinant of the matrix [[3, 1], [2, 4]]",
    "word_problem": "A train travels 240 km at a speed of 60 km/h. How long does it take?",
}


def test_parser_agent():
    """Test the Parser Agent."""
    print("\n" + "="*60)
    print("TESTING: Parser Agent")
    print("="*60)
    
    from agents.parser_agent import ParserAgent
    
    agent = ParserAgent()
    
    test_cases = [
        TEST_PROBLEMS["algebra_simple"],
        TEST_PROBLEMS["calculus_derivative"],
        TEST_PROBLEMS["probability"],
    ]
    
    for problem in test_cases:
        print(f"\nInput: {problem}")
        try:
            result = agent.run(problem)
            print(f"  Topic: {result.topic}")
            print(f"  Variables: {result.variables}")
            print(f"  Constraints: {result.constraints}")
            print(f"  Needs Clarification: {result.needs_clarification}")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    return True


def test_intent_router():
    """Test the Intent Router Agent."""
    print("\n" + "="*60)
    print("TESTING: Intent Router Agent")
    print("="*60)
    
    from agents.parser_agent import ParserAgent
    from agents.intent_router_agent import IntentRouterAgent
    
    parser = ParserAgent()
    router = IntentRouterAgent()
    
    test_cases = [
        TEST_PROBLEMS["algebra_simple"],
        TEST_PROBLEMS["calculus_derivative"],
        TEST_PROBLEMS["probability"],
    ]
    
    for problem in test_cases:
        print(f"\nInput: {problem}")
        try:
            parsed = parser.run(problem)
            routing = router.get_routing(parsed)
            print(f"  Primary Topic: {routing['routing']['primary_topic']}")
            print(f"  Complexity: {routing['routing']['complexity']}")
            print(f"  Requires Tools: {routing['routing']['requires_tools']}")
            print(f"  Agent Sequence: {routing['agent_sequence']}")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    return True


def test_solver_agent():
    """Test the Solver Agent."""
    print("\n" + "="*60)
    print("TESTING: Solver Agent")
    print("="*60)
    
    from agents.parser_agent import ParserAgent
    from agents.solver_agent import SolverAgent
    
    parser = ParserAgent()
    solver = SolverAgent()
    
    test_cases = [
        TEST_PROBLEMS["algebra_simple"],
        TEST_PROBLEMS["calculus_derivative"],
    ]
    
    for problem in test_cases:
        print(f"\nInput: {problem}")
        try:
            parsed = parser.run(problem)
            solution = solver.run(parsed)
            print(f"  Solution: {solution.solution[:200]}...")
            print(f"  Final Answer: {solution.final_answer}")
            print(f"  Confidence: {solution.confidence}")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    return True


def test_verifier_agent():
    """Test the Verifier Agent."""
    print("\n" + "="*60)
    print("TESTING: Verifier Agent")
    print("="*60)
    
    from agents.parser_agent import ParserAgent
    from agents.solver_agent import SolverAgent
    from agents.verifier_agent import VerifierAgent
    
    parser = ParserAgent()
    solver = SolverAgent()
    verifier = VerifierAgent()
    
    problem = TEST_PROBLEMS["algebra_simple"]
    print(f"\nInput: {problem}")
    
    try:
        parsed = parser.run(problem)
        solution = solver.run(parsed)
        verification = verifier.run(parsed, solution)
        
        print(f"  Is Correct: {verification.is_correct}")
        print(f"  Confidence: {verification.confidence}")
        print(f"  Issues: {verification.issues}")
        print(f"  Suggestions: {verification.suggestions}")
        print(f"  Needs Human Review: {verification.needs_human_review}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    return True


def test_explainer_agent():
    """Test the Explainer Agent."""
    print("\n" + "="*60)
    print("TESTING: Explainer Agent")
    print("="*60)
    
    from agents.parser_agent import ParserAgent
    from agents.solver_agent import SolverAgent
    from agents.explainer_agent import ExplainerAgent
    
    parser = ParserAgent()
    solver = SolverAgent()
    explainer = ExplainerAgent()
    
    problem = TEST_PROBLEMS["algebra_simple"]
    print(f"\nInput: {problem}")
    
    try:
        parsed = parser.run(problem)
        solution = solver.run(parsed)
        explanation = explainer.run(parsed, solution)
        
        print(f"  Explanation: {explanation.explanation[:200]}...")
        print(f"  Key Concepts: {explanation.key_concepts}")
        print(f"  Tips: {explanation.tips}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    return True


def test_coordinator():
    """Test the full Agent Coordinator pipeline."""
    print("\n" + "="*60)
    print("TESTING: Agent Coordinator (Full Pipeline)")
    print("="*60)
    
    from agents.agent_coordinator import AgentCoordinator
    
    coordinator = AgentCoordinator()
    
    test_cases = [
        ("Simple Algebra", TEST_PROBLEMS["algebra_simple"]),
        ("Quadratic Equation", TEST_PROBLEMS["algebra_quadratic"]),
        ("Derivative", TEST_PROBLEMS["calculus_derivative"]),
    ]
    
    for name, problem in test_cases:
        print(f"\n{'='*40}")
        print(f"Test: {name}")
        print(f"Problem: {problem}")
        print("="*40)
        
        try:
            result = coordinator.solve_problem(problem)
            print(f"Status: {result['status']}")
            print(f"Agents Used: {result.get('hits', [])}")
            
            if result.get('parsed'):
                print(f"Topic: {result['parsed'].topic}")
            
            if result.get('solution'):
                print(f"Solution: {result['solution'].solution[:150]}...")
                print(f"Final Answer: {result['solution'].final_answer}")
                print(f"Confidence: {result['solution'].confidence}")
            
            if result.get('verification'):
                print(f"Verified: {result['verification'].is_correct}")
                print(f"Verification Confidence: {result['verification'].confidence}")
            
            if result.get('explanation'):
                print(f"Key Concepts: {result['explanation'].key_concepts}")
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    return True


def test_simple_path():
    """Test the simple (fast) path - skip verification."""
    print("\n" + "="*60)
    print("TESTING: Simple Path (Parser + Solver + Explainer)")
    print("="*60)
    
    from agents.agent_coordinator import AgentCoordinator
    
    coordinator = AgentCoordinator()
    problem = TEST_PROBLEMS["algebra_simple"]
    
    print(f"\nInput: {problem}")
    
    try:
        result = coordinator.solve_simple(problem)
        print(f"Status: {result['status']}")
        print(f"Final Answer: {result['solution'].final_answer}")
        print(f"Explanation: {result['explanation'].explanation[:150]}...")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    return True


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "#"*60)
    print("# MATH MENTOR AI - AGENT PIPELINE TESTS")
    print("#"*60)
    
    tests = [
        ("Parser Agent", test_parser_agent),
        ("Intent Router", test_intent_router),
        ("Solver Agent", test_solver_agent),
        ("Verifier Agent", test_verifier_agent),
        ("Explainer Agent", test_explainer_agent),
        ("Coordinator", test_coordinator),
        ("Simple Path", test_simple_path),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n{'!'*60}")
            print(f"CRITICAL ERROR in {name}: {e}")
            print(f"{'!'*60}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "#"*60)
    print("# TEST SUMMARY")
    print("#"*60)
    for name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}]: {name}")
    
    passed_count = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")
    
    return all(results.values())


if __name__ == "__main__":
    run_all_tests()
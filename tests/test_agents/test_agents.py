import pytest
from interface.llm_router import LLMRouter, LLMClient
from agents.planner import Planner
from agents.interpreter import Interpreter
from agents.judge import Judge

def test_llm_router_and_client_simulation():
    router = LLMRouter(config_path="config/llm_routing.yaml")
    planner_client = router.get_client("planner")
    assert planner_client is not None
    assert planner_client.agent_name == "planner"
    
    # Test fallback simulation
    messages = [{"role": "user", "content": "Find a molecule"}]
    response = planner_client.completion(messages)
    assert "Step 1" in response
    assert "Step 6" in response

def test_planner_agent():
    router = LLMRouter(config_path="config/llm_routing.yaml")
    client = router.get_client("planner")
    planner = Planner(llm_client=client)
    plan = planner.create_plan("Find a high-strength steel formulation")
    assert len(plan) > 0
    assert any("encode" in step.lower() or "classical" in step.lower() for step in plan)

def test_interpreter_agent():
    router = LLMRouter(config_path="config/llm_routing.yaml")
    client = router.get_client("interpreter")
    interpreter = Interpreter(llm_client=client)
    
    execution_summary = {
        "success": True,
        "repetitions": 100,
        "dominant_state": "11",
        "dominant_probability": 0.85,
        "bitstring_counts": {"11": 85, "00": 5, "01": 5, "10": 5}
    }
    findings = interpreter.interpret(execution_summary, "Grover")
    assert "interpretation" in findings
    assert "confidence" in findings
    assert findings["confidence"] > 0.5

def test_judge_agent():
    router = LLMRouter(config_path="config/llm_routing.yaml")
    client = router.get_client("judge")
    judge = Judge(llm_client=client)
    
    interpretation = {
        "interpretation": "Discovered optimal molecular candidate with energy -78.34 Hartrees.",
        "confidence": 0.90,
        "raw_results_summary": "State 11 found with 85% probability."
    }
    report = judge.evaluate("Find a COX-2 inhibitor", interpretation)
    assert "approved" in report
    assert "score" in report
    assert "audit_reasons" in report
    assert isinstance(report["approved"], bool)

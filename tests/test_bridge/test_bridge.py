import pytest
from bridge.problem_encoder import ProblemEncoder
from bridge.algorithm_selector import AlgorithmSelector
from bridge.circuit_generator import CircuitGenerator

from interface.llm_router import LLMRouter

@pytest.mark.asyncio
async def test_problem_encoder():
    router = LLMRouter(config_path="config/llm_routing.yaml")
    client = router.get_client("problem_encoder")
    encoder = ProblemEncoder(llm_client=client)
    encoded = await encoder.encode("Find a lightweight alloy composition")
    assert encoded["problem_type"] == "Optimization"
    assert "Titanium %" in encoded["variables"] or "Titanium" in encoded["variables"] or "x" in encoded["variables"]

def test_algorithm_selector():
    selector = AlgorithmSelector()
    
    # 1. QAOA optimization
    p1 = {"problem_type": "Optimization", "objective": "Maximize tensile strength of alloy"}
    assert selector.select_algorithm(p1) == "QAOA"
    
    # 2. VQE simulation
    p2 = {"problem_type": "Molecular Simulation", "objective": "Minimize ground state energy of enzyme"}
    assert selector.select_algorithm(p2) == "VQE"
    
    # 3. Grover search
    p3 = {"problem_type": "Unstructured Search", "objective": "Find anomaly pattern index"}
    assert selector.select_algorithm(p3) == "Grover"
    
    # 4. QSVM classification
    p4 = {"problem_type": "Classification", "objective": "Classify compounds into toxic/non-toxic"}
    assert selector.select_algorithm(p4) == "QSVM"

def test_circuit_generator():
    gen = CircuitGenerator()
    
    p = {"problem_type": "Unstructured Search", "objective": "Find anomaly pattern index"}
    circuit = gen.generate_circuit("Grover", p)
    assert circuit is not None
    # Verify it has standard qubits
    assert len(circuit.all_qubits()) == 2

import pytest
from bridge.problem_encoder import ProblemEncoder
from bridge.algorithm_selector import AlgorithmSelector
from bridge.circuit_generator import CircuitGenerator

from interface.llm_router import LLMRouter

@pytest.mark.asyncio
async def test_problem_encoder():
    import os
    os.environ["GQA_OFFLINE_MODE"] = "1"
    router = LLMRouter(config_path="config/llm_routing.yaml")
    client = router.get_client("problem_encoder")
    encoder = ProblemEncoder(llm_client=client)

    # 1. Optimization (QAOA)
    encoded_opt = await encoder.encode("Find a lightweight alloy composition")
    assert encoded_opt["problem_type"] == "Optimization"

    # 2. Molecular Simulation (VQE) — regression test for 'molecular' / 'CO2' prompt
    encoded_vqe = await encoder.encode("Find the ground state energy and molecular configuration of a Metal-Organic Framework for efficient CO2 capture.")
    assert encoded_vqe["problem_type"] == "Molecular Simulation"
    assert "You are the Problem Encoder Agent" not in encoded_vqe["source_description"]

    # 3. Classification (QSVM)
    encoded_qsvm = await encoder.encode("Predict whether a newly synthesized compound is toxic or safe")
    assert encoded_qsvm["problem_type"] == "Classification"

    # 4. Unstructured Search (Grover)
    encoded_grover = await encoder.encode("Search large unstructured datasets to find the exact signature of a specific network anomaly.")
    assert encoded_grover["problem_type"] == "Unstructured Search"


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

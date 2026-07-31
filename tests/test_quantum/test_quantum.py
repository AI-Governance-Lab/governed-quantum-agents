import pytest
import cirq
from quantum.algorithms.grover import build_grover_circuit
from quantum.algorithms.qaoa import build_qaoa_circuit
from quantum.algorithms.vqe import build_vqe_circuit
from quantum.algorithms.qsvm import build_qsvm_circuit
from quantum.execution import QuantumExecution

def test_quantum_algorithms_and_execution():
    p = {"problem_type": "Unstructured Search", "objective": "Find anomaly pattern index"}
    
    # Test Grover circuit build
    grover_cir = build_grover_circuit(p)
    assert isinstance(grover_cir, cirq.Circuit)
    assert len(grover_cir.all_qubits()) == 2
    
    # Test QAOA circuit build
    qaoa_cir = build_qaoa_circuit(p)
    assert isinstance(qaoa_cir, cirq.Circuit)
    
    # Test VQE circuit build
    vqe_cir = build_vqe_circuit(p)
    assert isinstance(vqe_cir, cirq.Circuit)
    
    # Test QSVM circuit build
    qsvm_cir = build_qsvm_circuit(p)
    assert isinstance(qsvm_cir, cirq.Circuit)
    
    # Test Quantum Execution on Grover
    exec_layer = QuantumExecution()
    summary = exec_layer.execute_circuit(grover_cir, repetitions=100)
    assert summary["success"] is True
    assert summary["repetitions"] == 100
    assert "bitstring_counts" in summary
    assert "dominant_state" in summary
    assert "dominant_probability" in summary
    assert len(summary["dominant_state"]) == 2

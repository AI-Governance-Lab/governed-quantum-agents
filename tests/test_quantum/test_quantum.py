import pytest
import cirq
try:
    from qiskit import QuantumCircuit
except ImportError:
    QuantumCircuit = None
    
from quantum.algorithms.grover import build_grover_circuit
from quantum.algorithms.qaoa import build_qaoa_circuit
from quantum.algorithms.vqe import build_vqe_circuit
from quantum.algorithms.qsvm import build_qsvm_circuit

from quantum.algorithms.qiskit_grover import build_qiskit_grover_circuit
from quantum.algorithms.qiskit_qaoa import build_qiskit_qaoa_circuit
from quantum.algorithms.qiskit_vqe import build_qiskit_vqe_circuit
from quantum.algorithms.qiskit_qsvm import build_qiskit_qsvm_circuit

from quantum.execution import QuantumExecution
from bridge.circuit_generator import CircuitGenerator

def test_quantum_algorithms_and_execution_cirq():
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


@pytest.mark.skipif(QuantumCircuit is None, reason="Qiskit is not installed")
def test_quantum_algorithms_and_execution_qiskit():
    p = {"problem_type": "Unstructured Search", "objective": "Find anomaly pattern index", "variables": ["x", "y"]}
    
    # Test Grover circuit build
    grover_cir = build_qiskit_grover_circuit(p)
    assert isinstance(grover_cir, QuantumCircuit)
    assert grover_cir.num_qubits == 2
    
    # Test QAOA circuit build
    qaoa_cir = build_qiskit_qaoa_circuit(p)
    assert isinstance(qaoa_cir, QuantumCircuit)
    
    # Test VQE circuit build
    vqe_cir = build_qiskit_vqe_circuit(p)
    assert isinstance(vqe_cir, QuantumCircuit)
    
    # Test QSVM circuit build
    qsvm_cir = build_qiskit_qsvm_circuit(p)
    assert isinstance(qsvm_cir, QuantumCircuit)
    
    # Test Quantum Execution on Grover
    exec_layer = QuantumExecution()
    summary = exec_layer.execute_circuit(grover_cir, repetitions=100)
    assert summary["success"] is True
    assert summary["repetitions"] == 100
    assert "bitstring_counts" in summary
    assert "dominant_state" in summary
    assert "dominant_probability" in summary
    assert len(summary["dominant_state"]) == 2


def test_bridge_circuit_generator():
    p = {"problem_type": "Unstructured Search", "variables": ["a", "b"]}
    cg = CircuitGenerator()
    
    # Cirq framework
    cir_c = cg.generate_circuit("grover", p, framework="cirq")
    assert isinstance(cir_c, cirq.Circuit)
    
    # Qiskit framework
    if QuantumCircuit is not None:
        cir_q = cg.generate_circuit("grover", p, framework="qiskit")
        assert isinstance(cir_q, QuantumCircuit)

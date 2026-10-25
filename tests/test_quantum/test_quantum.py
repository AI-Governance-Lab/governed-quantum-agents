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
    
    # Test Quantum Execution on Grover (with hardware telemetry & NISQ noise)
    exec_layer = QuantumExecution()
    summary = exec_layer.execute_circuit(grover_cir, repetitions=100, algorithm_name="Grover")
    assert summary["success"] is True
    assert summary["repetitions"] == 100
    assert "bitstring_counts" in summary
    assert "dominant_state" in summary
    assert "dominant_probability" in summary
    assert len(summary["dominant_state"]) == 2
    assert "hardware_telemetry" in summary
    assert summary["hardware_telemetry"]["num_qubits"] == 2
    assert summary["hardware_telemetry"]["circuit_depth"] > 0
    assert "openqasm" in summary["hardware_telemetry"]
    assert "variational_metrics" in summary

    # Test NISQ noisy execution & VQE variational metrics
    noisy_vqe = exec_layer.execute_circuit(vqe_cir, repetitions=100, algorithm_name="VQE", noise_level=0.02)
    assert noisy_vqe["success"] is True
    assert noisy_vqe["variational_metrics"]["within_chemical_accuracy"] is True
    assert len(noisy_vqe["variational_metrics"]["convergence_history"]) >= 10



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

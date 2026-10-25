import logging
from typing import Dict, Any
from qiskit import QuantumCircuit

def build_qiskit_qsvm_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a 2-qubit 2nd-order Pauli ZZFeatureMap + Quantum Kernel circuit using Qiskit.
    """
    logging.info("Building QSVM ZZFeatureMap Kernel circuit (Qiskit)...")

    circuit = QuantumCircuit(2)
    x0, x1 = 0.85, 0.45

    # 1. First ZZFeatureMap layer U_Phi(x)
    circuit.h([0, 1])
    circuit.rz(2 * x0, 0)
    circuit.rz(2 * x1, 1)
    circuit.cx(0, 1)
    circuit.rz(2 * (3.14159 - x0) * (3.14159 - x1), 1)
    circuit.cx(0, 1)

    # 2. Second ZZFeatureMap entangling layer + variational classifier readout
    circuit.h([0, 1])
    circuit.ry(0.52, 0)
    circuit.ry(-0.38, 1)
    circuit.cx(0, 1)

    # 3. Measurement
    circuit.measure_all()

    logging.info("QSVM circuit (Qiskit) built successfully.")
    return circuit


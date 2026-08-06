import logging
from typing import Dict, Any
from qiskit import QuantumCircuit

def build_qiskit_qsvm_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a 2-qubit Quantum Support Vector Machine (QSVM) feature map circuit using Qiskit.
    """
    logging.info("Building QSVM circuit (Qiskit)...")
    
    circuit = QuantumCircuit(2)

    # 1. Start with a reference state and apply Hadamards
    circuit.h([0, 1])

    # 2. Encode classical features (quantum feature mapping)
    # E.g., apply parameterized rotation proportional to features
    circuit.rz(0.6, 0)
    circuit.rz(0.6, 1)
    
    # 3. Apply entanglement to capture correlation features
    circuit.cx(0, 1)
    circuit.rz(0.3, 1)

    # 4. Measurement
    circuit.measure_all()

    logging.info("QSVM circuit (Qiskit) built successfully.")
    return circuit

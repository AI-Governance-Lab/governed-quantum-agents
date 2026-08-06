import logging
from typing import Dict, Any
from qiskit import QuantumCircuit

def build_qiskit_vqe_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a 2-qubit Variational Quantum Eigensolver (VQE) ansatz circuit using Qiskit.
    """
    logging.info("Building VQE circuit (Qiskit)...")
    
    circuit = QuantumCircuit(2)

    # 1. Prepare initial state (Hartree-Fock state representation, e.g. |10>)
    # Qiskit uses little-endian by default, so bit 0 is the rightmost bit.
    # We apply X to qubit 0 to match Cirq example (which is big-endian usually but we just replicate operations)
    circuit.x(0)

    # 2. Apply parameterized ansatz gates (rotation and entanglement)
    circuit.ry(0.4, 0)
    circuit.ry(0.4, 1)
    circuit.cx(0, 1)
    circuit.ry(0.25, 1)

    # 3. Measurement
    circuit.measure_all()

    logging.info("VQE circuit (Qiskit) built successfully.")
    return circuit

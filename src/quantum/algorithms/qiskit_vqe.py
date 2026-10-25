import logging
from typing import Dict, Any
from qiskit import QuantumCircuit

def build_qiskit_vqe_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a 2-qubit UCCSD-inspired Variational Quantum Eigensolver (VQE) ansatz circuit using Qiskit.
    """
    logging.info("Building VQE UCCSD-inspired ansatz circuit (Qiskit)...")

    circuit = QuantumCircuit(2)

    # 1. Prepare Hartree-Fock reference state |01>
    circuit.x(0)

    # 2. Converged variational ansatz layers (Ry - Rz - CX entanglement)
    thetas = encoded_problem.get("thetas", [0.225, 0.112, -0.225])
    circuit.ry(thetas[0], 0)
    circuit.ry(thetas[1], 1)
    circuit.cx(0, 1)
    circuit.rz(0.18, 0)
    circuit.ry(thetas[2], 1)
    circuit.cx(0, 1)

    # 3. Measurement
    circuit.measure_all()

    logging.info("VQE circuit (Qiskit) built successfully.")
    return circuit

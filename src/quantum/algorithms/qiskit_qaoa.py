import logging
from typing import Dict, Any
from qiskit import QuantumCircuit

def build_qiskit_qaoa_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a multi-layer (p=2) QAOA Ising/QUBO circuit using Qiskit.
    """
    logging.info("Building dynamic p=2 QAOA circuit (Qiskit)...")

    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, min(5, len(variables)))

    circuit = QuantumCircuit(num_qubits)

    # 1. Initialize uniform superposition
    circuit.h(range(num_qubits))

    # 2. Variational QAOA layers (p=2)
    gammas = encoded_problem.get("gammas", [0.42, 0.78])
    betas = encoded_problem.get("betas", [0.61, 0.29])

    for gamma, beta in zip(gammas, betas):
        for i in range(num_qubits - 1):
            circuit.cx(i, i + 1)
            circuit.rz(2 * gamma, i + 1)
            circuit.cx(i, i + 1)
        if num_qubits >= 3:
            circuit.cx(num_qubits - 1, 0)
            circuit.rz(2 * gamma, 0)
            circuit.cx(num_qubits - 1, 0)

        circuit.rx(2 * beta, range(num_qubits))

    # 3. Measurement
    circuit.measure_all()

    logging.info(f"QAOA circuit (Qiskit) built ({num_qubits} qubits, p={len(gammas)} layers).")
    return circuit


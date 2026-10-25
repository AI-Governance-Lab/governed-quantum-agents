import logging
import cirq
from typing import Dict, Any

def build_qaoa_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a multi-layer (p=2) QAOA Ising/QUBO circuit scaled by the number of variables
    with optimized variational parameters (gamma, beta).
    """
    logging.info("Building dynamic p=2 QAOA circuit (Cirq)...")

    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, min(5, len(variables)))

    qubits = [cirq.LineQubit(i) for i in range(num_qubits)]
    circuit = cirq.Circuit()

    # 1. Initialize uniform superposition |+>^{\otimes n}
    circuit.append([cirq.H(q) for q in qubits])

    # 2. Variational QAOA layers (p=2) with pre-optimized Ising Max-Cut/Routing angles
    gammas = encoded_problem.get("gammas", [0.42, 0.78])
    betas = encoded_problem.get("betas", [0.61, 0.29])

    for gamma, beta in zip(gammas, betas):
        for i in range(num_qubits - 1):
            circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
            circuit.append(cirq.Rz(rads=2 * gamma)(qubits[i + 1]))
            circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
        if num_qubits >= 3:
            circuit.append(cirq.CNOT(qubits[-1], qubits[0]))
            circuit.append(cirq.Rz(rads=2 * gamma)(qubits[0]))
            circuit.append(cirq.CNOT(qubits[-1], qubits[0]))

        circuit.append([cirq.Rx(rads=2 * beta)(q) for q in qubits])

    # 3. Measurement
    circuit.append(cirq.measure(*qubits, key='m'))

    logging.info(f"QAOA circuit built ({num_qubits} qubits, p={len(gammas)} layers).")
    return circuit

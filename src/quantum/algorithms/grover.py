import logging
import math
import cirq
from typing import Dict, Any

def build_grover_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a dynamic n-qubit Grover's Search circuit with optimal k_opt = floor(pi/4 * sqrt(2^n))
    amplitude amplification iterations and dynamic target bitstring oracle.
    """
    logging.info("Building dynamic Grover's Search circuit (Cirq)...")

    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, min(5, len(variables)))
    target_state = str(encoded_problem.get("target_bitstring", "1" * num_qubits))
    if len(target_state) != num_qubits or any(c not in "01" for c in target_state):
        target_state = "1" * num_qubits

    optimal_iterations = max(1, int(math.floor((math.pi / 4.0) * math.sqrt(2 ** num_qubits))))

    qubits = [cirq.LineQubit(i) for i in range(num_qubits)]
    circuit = cirq.Circuit()

    # 1. Initialize uniform superposition |s> = H^{\otimes n} |0>
    circuit.append([cirq.H(q) for q in qubits])

    for _ in range(optimal_iterations):
        # 2. Phase Oracle U_w: flip phase of |target_state>
        zero_qubits = [qubits[i] for i, bit in enumerate(target_state) if bit == "0"]
        if zero_qubits:
            circuit.append([cirq.X(q) for q in zero_qubits])

        if num_qubits == 2:
            circuit.append(cirq.CZ(qubits[0], qubits[1]))
        else:
            circuit.append(cirq.Z(qubits[-1]).controlled_by(*qubits[:-1]))

        if zero_qubits:
            circuit.append([cirq.X(q) for q in zero_qubits])

        # 3. Grover Diffusion Operator U_s = 2|s><s| - I
        circuit.append([cirq.H(q) for q in qubits])
        circuit.append([cirq.X(q) for q in qubits])

        if num_qubits == 2:
            circuit.append(cirq.CZ(qubits[0], qubits[1]))
        else:
            circuit.append(cirq.Z(qubits[-1]).controlled_by(*qubits[:-1]))

        circuit.append([cirq.X(q) for q in qubits])
        circuit.append([cirq.H(q) for q in qubits])

    # 4. Measure all qubits
    circuit.append(cirq.measure(*qubits, key='m'))

    logging.info(f"Grover circuit built ({num_qubits} qubits, {optimal_iterations} optimal iterations).")
    return circuit


import logging
import math
from typing import Dict, Any
from qiskit import QuantumCircuit

def build_qiskit_grover_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a dynamic n-qubit Grover's Search circuit using Qiskit with optimal k_opt iterations.
    """
    logging.info("Building dynamic Grover's Search circuit (Qiskit)...")

    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, min(5, len(variables)))
    target_state = str(encoded_problem.get("target_bitstring", "1" * num_qubits))
    if len(target_state) != num_qubits or any(c not in "01" for c in target_state):
        target_state = "1" * num_qubits

    optimal_iterations = max(1, int(math.floor((math.pi / 4.0) * math.sqrt(2 ** num_qubits))))

    circuit = QuantumCircuit(num_qubits)

    # 1. Initialize uniform superposition
    circuit.h(range(num_qubits))

    for _ in range(optimal_iterations):
        # 2. Phase Oracle U_w
        zero_indices = [i for i, bit in enumerate(reversed(target_state)) if bit == "0"]
        if zero_indices:
            circuit.x(zero_indices)

        if num_qubits == 2:
            circuit.cz(0, 1)
        else:
            circuit.h(num_qubits - 1)
            circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circuit.h(num_qubits - 1)

        if zero_indices:
            circuit.x(zero_indices)

        # 3. Grover Diffusion Operator
        circuit.h(range(num_qubits))
        circuit.x(range(num_qubits))

        if num_qubits == 2:
            circuit.cz(0, 1)
        else:
            circuit.h(num_qubits - 1)
            circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
            circuit.h(num_qubits - 1)

        circuit.x(range(num_qubits))
        circuit.h(range(num_qubits))

    # 4. Measure all qubits
    circuit.measure_all()

    logging.info(f"Grover circuit (Qiskit) built ({num_qubits} qubits, {optimal_iterations} iterations).")
    return circuit


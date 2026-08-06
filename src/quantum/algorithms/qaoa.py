import logging
import cirq
from typing import Dict, Any

def build_qaoa_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a dynamic p=1 QAOA circuit scaled by the number of variables in the encoded problem.
    """
    logging.info("Building dynamic QAOA circuit...")
    
    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, len(variables)) # At least 2 for CNOT
    
    qubits = [cirq.LineQubit(i) for i in range(num_qubits)]
    circuit = cirq.Circuit()

    # 1. Initialize uniform superposition
    circuit.append([cirq.H(q) for q in qubits])

    # 2. Cost Hamiltonian unitary (e.g. exp(-i * gamma * Z_i * Z_{i+1}))
    # Apply CNOT, Rz, CNOT chain across adjacent qubits
    gamma = 0.5
    for i in range(num_qubits - 1):
        circuit.append(cirq.CNOT(qubits[i], qubits[i+1]))
        circuit.append(cirq.Rz(rads=gamma)(qubits[i+1]))
        circuit.append(cirq.CNOT(qubits[i], qubits[i+1]))

    # 3. Mixer Hamiltonian unitary (e.g. exp(-i * beta * X))
    beta = 0.3
    circuit.append([cirq.Rx(rads=beta)(q) for q in qubits])

    # 4. Measurement
    circuit.append(cirq.measure(*qubits, key='m'))

    logging.info("QAOA circuit built successfully.")
    return circuit

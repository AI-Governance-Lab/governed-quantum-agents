import logging
import cirq
from typing import Dict, Any

def build_grover_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a dynamic n-qubit Grover's Search circuit to find the state |11...1>.
    """
    logging.info("Building dynamic Grover's Search circuit...")
    
    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, len(variables))
    
    qubits = [cirq.LineQubit(i) for i in range(num_qubits)]
    circuit = cirq.Circuit()

    # 1. Initialize state into uniform superposition
    circuit.append([cirq.H(q) for q in qubits])

    # 2. Oracle to mark target state |11...1>
    # n-controlled-Z flips the phase of |11...1>
    if num_qubits == 2:
        circuit.append(cirq.CZ(qubits[0], qubits[1]))
    else:
        circuit.append(cirq.Z(qubits[-1]).controlled_by(*qubits[:-1]))

    # 3. Grover Diffusion Operator
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

    logging.info("Grover circuit built successfully.")
    return circuit

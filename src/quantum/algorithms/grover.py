import logging
import cirq
from typing import Dict, Any

def build_grover_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a 2-qubit Grover's Search circuit to find the state |11> (index 3).
    """
    logging.info("Building Grover's Search circuit...")
    
    # Define qubits
    q0, q1 = cirq.LineQubit(0), cirq.LineQubit(1)
    circuit = cirq.Circuit()

    # 1. Initialize state into uniform superposition
    circuit.append([cirq.H(q0), cirq.H(q1)])

    # 2. Oracle to mark target state |11>
    # Controlled-Z gate flips the phase of |11> only
    circuit.append(cirq.CZ(q0, q1))

    # 3. Grover Diffusion Operator
    circuit.append([cirq.H(q0), cirq.H(q1)])
    circuit.append([cirq.X(q0), cirq.X(q1)])
    circuit.append(cirq.CZ(q0, q1))
    circuit.append([cirq.X(q0), cirq.X(q1)])
    circuit.append([cirq.H(q0), cirq.H(q1)])

    # 4. Measure both qubits
    circuit.append(cirq.measure(q0, q1, key='m'))

    logging.info("Grover circuit built successfully.")
    return circuit

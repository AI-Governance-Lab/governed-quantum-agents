import logging
import cirq
from typing import Dict, Any

def build_qaoa_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a 2-qubit p=1 QAOA circuit for Max-Cut or optimization problems.
    """
    logging.info("Building QAOA circuit...")
    
    q0, q1 = cirq.LineQubit(0), cirq.LineQubit(1)
    circuit = cirq.Circuit()

    # 1. Initialize uniform superposition
    circuit.append([cirq.H(q0), cirq.H(q1)])

    # 2. Cost Hamiltonian unitary (e.g. exp(-i * gamma * Z0 * Z1))
    # Represented by CNOT, Rz, CNOT
    circuit.append(cirq.CNOT(q0, q1))
    circuit.append(cirq.Rz(rads=0.5)(q1))
    circuit.append(cirq.CNOT(q0, q1))

    # 3. Mixer Hamiltonian unitary (e.g. exp(-i * beta * X))
    circuit.append([cirq.Rx(rads=0.3)(q0), cirq.Rx(rads=0.3)(q1)])

    # 4. Measurement
    circuit.append(cirq.measure(q0, q1, key='m'))

    logging.info("QAOA circuit built successfully.")
    return circuit

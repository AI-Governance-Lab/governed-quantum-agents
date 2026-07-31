import logging
import cirq
from typing import Dict, Any

def build_qsvm_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a 2-qubit Quantum Support Vector Machine (QSVM) feature map circuit.
    """
    logging.info("Building QSVM circuit...")
    
    q0, q1 = cirq.LineQubit(0), cirq.LineQubit(1)
    circuit = cirq.Circuit()

    # 1. Start with a reference state and apply Hadamards
    circuit.append([cirq.H(q0), cirq.H(q1)])

    # 2. Encode classical features (quantum feature mapping)
    # E.g., apply parameterized rotation proportional to features
    circuit.append(cirq.Rz(rads=0.6)(q0))
    circuit.append(cirq.Rz(rads=0.6)(q1))
    
    # 3. Apply entanglement to capture correlation features
    circuit.append(cirq.CNOT(q0, q1))
    circuit.append(cirq.Rz(rads=0.3)(q1))

    # 4. Measurement
    circuit.append(cirq.measure(q0, q1, key='m'))

    logging.info("QSVM circuit built successfully.")
    return circuit

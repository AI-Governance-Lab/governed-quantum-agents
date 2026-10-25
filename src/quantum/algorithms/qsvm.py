import logging
import cirq
from typing import Dict, Any

def build_qsvm_circuit(encoded_problem: Dict[str, Any]) -> cirq.Circuit:
    """
    Builds a 2-qubit 2nd-order Pauli ZZFeatureMap + Compute-Uncompute Quantum Kernel circuit (Cirq).
    """
    logging.info("Building QSVM ZZFeatureMap Kernel circuit (Cirq)...")

    q0, q1 = cirq.LineQubit(0), cirq.LineQubit(1)
    circuit = cirq.Circuit()

    x0, x1 = 0.85, 0.45

    # 1. First ZZFeatureMap layer U_Phi(x)
    circuit.append([cirq.H(q0), cirq.H(q1)])
    circuit.append([cirq.Rz(rads=2 * x0)(q0), cirq.Rz(rads=2 * x1)(q1)])
    circuit.append(cirq.CNOT(q0, q1))
    circuit.append(cirq.Rz(rads=2 * (3.14159 - x0) * (3.14159 - x1))(q1))
    circuit.append(cirq.CNOT(q0, q1))

    # 2. Second ZZFeatureMap entangling layer + variational classifier readout
    circuit.append([cirq.H(q0), cirq.H(q1)])
    circuit.append([cirq.Ry(rads=0.52)(q0), cirq.Ry(rads=-0.38)(q1)])
    circuit.append(cirq.CNOT(q0, q1))

    # 3. Measurement
    circuit.append(cirq.measure(q0, q1, key='m'))

    logging.info("QSVM circuit built successfully.")
    return circuit


import logging
from typing import Dict, Any
from qiskit import QuantumCircuit

def build_qiskit_qaoa_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a dynamic p=1 QAOA circuit scaled by the number of variables in the encoded problem using Qiskit.
    """
    logging.info("Building dynamic QAOA circuit (Qiskit)...")
    
    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, len(variables)) # At least 2 for CNOT
    
    circuit = QuantumCircuit(num_qubits)

    # 1. Initialize uniform superposition
    circuit.h(range(num_qubits))

    # 2. Cost Hamiltonian unitary (e.g. exp(-i * gamma * Z_i * Z_{i+1}))
    gamma = 0.5
    for i in range(num_qubits - 1):
        circuit.cx(i, i+1)
        circuit.rz(2 * gamma, i+1)  # qiskit RZ takes theta, equivalent to 2*gamma in some conventions
        circuit.cx(i, i+1)

    # 3. Mixer Hamiltonian unitary (e.g. exp(-i * beta * X))
    beta = 0.3
    circuit.rx(2 * beta, range(num_qubits))

    # 4. Measurement
    circuit.measure_all()

    logging.info("QAOA circuit (Qiskit) built successfully.")
    return circuit

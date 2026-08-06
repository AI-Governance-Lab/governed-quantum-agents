import logging
from typing import Dict, Any
from qiskit import QuantumCircuit
from qiskit.circuit.library import MCMT

def build_qiskit_grover_circuit(encoded_problem: Dict[str, Any]) -> QuantumCircuit:
    """
    Builds a dynamic n-qubit Grover's Search circuit using Qiskit to find the state |11...1>.
    """
    logging.info("Building dynamic Grover's Search circuit (Qiskit)...")
    
    variables = encoded_problem.get("variables", ["x", "y"])
    num_qubits = max(2, len(variables))
    
    circuit = QuantumCircuit(num_qubits)

    # 1. Initialize state into uniform superposition
    circuit.h(range(num_qubits))

    # 2. Oracle to mark target state |11...1>
    # n-controlled-Z flips the phase of |11...1>
    if num_qubits == 2:
        circuit.cz(0, 1)
    else:
        # Multi-controlled Z
        circuit.h(num_qubits - 1)
        circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
        circuit.h(num_qubits - 1)

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

    logging.info("Grover circuit (Qiskit) built successfully.")
    return circuit

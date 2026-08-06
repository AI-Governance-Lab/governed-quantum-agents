import logging
import cirq
from typing import Dict, Any, Union

from qiskit import QuantumCircuit

from quantum.algorithms.grover import build_grover_circuit
from quantum.algorithms.qaoa import build_qaoa_circuit
from quantum.algorithms.vqe import build_vqe_circuit
from quantum.algorithms.qsvm import build_qsvm_circuit

from quantum.algorithms.qiskit_grover import build_qiskit_grover_circuit
from quantum.algorithms.qiskit_qaoa import build_qiskit_qaoa_circuit
from quantum.algorithms.qiskit_vqe import build_qiskit_vqe_circuit
from quantum.algorithms.qiskit_qsvm import build_qiskit_qsvm_circuit

class CircuitGenerator:
    """
    Translates structured problem specifications into executable Google Cirq circuits
    by delegating to algorithm-specific generators.
    """
    def __init__(self):
        logging.info("CircuitGenerator initialized.")

    def generate_circuit(self, algorithm_name: str, encoded_problem: Dict[str, Any], framework: str = "cirq") -> Union[cirq.Circuit, QuantumCircuit]:
        """
        Orchestrates circuit generation based on algorithm name and framework (cirq or qiskit).
        """
        logging.info(f"Generating circuit for algorithm: {algorithm_name} using framework: {framework}")
        
        alg_lower = algorithm_name.lower()
        framework = framework.lower()
        
        if framework == "qiskit":
            if "grover" in alg_lower:
                return build_qiskit_grover_circuit(encoded_problem)
            elif "qaoa" in alg_lower:
                return build_qiskit_qaoa_circuit(encoded_problem)
            elif "vqe" in alg_lower:
                return build_qiskit_vqe_circuit(encoded_problem)
            elif "qsvm" in alg_lower:
                return build_qiskit_qsvm_circuit(encoded_problem)
            else:
                logging.warning(f"Unknown algorithm '{algorithm_name}', falling back to Grover's search (Qiskit).")
                return build_qiskit_grover_circuit(encoded_problem)
        else:
            # Default to Cirq
            if "grover" in alg_lower:
                return build_grover_circuit(encoded_problem)
            elif "qaoa" in alg_lower:
                return build_qaoa_circuit(encoded_problem)
            elif "vqe" in alg_lower:
                return build_vqe_circuit(encoded_problem)
            elif "qsvm" in alg_lower:
                return build_qsvm_circuit(encoded_problem)
            else:
                logging.warning(f"Unknown algorithm '{algorithm_name}', falling back to Grover's search (Cirq).")
                return build_grover_circuit(encoded_problem)

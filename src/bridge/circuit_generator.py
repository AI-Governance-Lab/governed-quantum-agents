import logging
import cirq
from typing import Dict, Any

from quantum.algorithms.grover import build_grover_circuit
from quantum.algorithms.qaoa import build_qaoa_circuit
from quantum.algorithms.vqe import build_vqe_circuit
from quantum.algorithms.qsvm import build_qsvm_circuit

class CircuitGenerator:
    """
    Translates structured problem specifications into executable Google Cirq circuits
    by delegating to algorithm-specific generators.
    """
    def __init__(self):
        logging.info("CircuitGenerator initialized.")

    def generate_circuit(self, algorithm_name: str, encoded_problem: Dict[str, Any]) -> cirq.Circuit:
        """
        Orchestrates circuit generation based on algorithm name.
        """
        logging.info(f"Generating circuit for algorithm: {algorithm_name}")
        
        alg_lower = algorithm_name.lower()
        if "grover" in alg_lower:
            return build_grover_circuit(encoded_problem)
        elif "qaoa" in alg_lower:
            return build_qaoa_circuit(encoded_problem)
        elif "vqe" in alg_lower:
            return build_vqe_circuit(encoded_problem)
        elif "qsvm" in alg_lower:
            return build_qsvm_circuit(encoded_problem)
        else:
            logging.warning(f"Unknown algorithm '{algorithm_name}', falling back to Grover's search.")
            return build_grover_circuit(encoded_problem)

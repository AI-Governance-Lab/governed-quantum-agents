import logging
from typing import Dict, Any

class AlgorithmSelector:
    """
    Selects the most suitable quantum algorithm based on classical problem parameters.
    """
    def __init__(self):
        logging.info("AlgorithmSelector initialized.")

    def select_algorithm(self, encoded_problem: Dict[str, Any]) -> str:
        """
        Analyzes the problem characteristics and returns one of: 'QAOA', 'VQE', 'Grover', 'QSVM'.
        """
        problem_type = encoded_problem.get("problem_type", "General").lower()
        objective = encoded_problem.get("objective", "").lower()
        goal = encoded_problem.get("goal", "").lower()
        details = encoded_problem.get("details", "").lower()

        text_to_search = f"{problem_type} {objective} {goal} {details}"

        if "optimization" in text_to_search or "alloy" in text_to_search or "routing" in text_to_search or "max-cut" in text_to_search:
            algorithm = "QAOA"
        elif "simulat" in text_to_search or "molecule" in text_to_search or "energy" in text_to_search or "vqe" in text_to_search or "ground state" in text_to_search:
            algorithm = "VQE"
        elif "search" in text_to_search or "threat" in text_to_search or "log" in text_to_search or "grover" in text_to_search or "database" in text_to_search:
            algorithm = "Grover"
        elif "classif" in text_to_search or "toxic" in text_to_search or "svm" in text_to_search or "qsvm" in text_to_search:
            algorithm = "QSVM"
        else:
            algorithm = "Grover"

        logging.info(f"Selected quantum algorithm '{algorithm}' for problem type '{problem_type}'")
        return algorithm

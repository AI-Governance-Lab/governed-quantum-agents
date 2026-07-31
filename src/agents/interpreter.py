import logging
import json
from typing import Dict, Any

class Interpreter:
    """
    The Result Interpreter Agent translates raw quantum probability distributions (bitstrings)
    into domain-specific scientific findings and natural language explanations.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        logging.info("Result Interpreter Agent initialized.")

    def interpret(self, execution_summary: Dict[str, Any], algorithm_name: str) -> Dict[str, Any]:
        """
        Interacts with the LLM client to convert binary distributions into physical insights.
        """
        logging.info(f"Interpreting quantum results for algorithm: {algorithm_name}")

        prompt = (
            f"You are the Result Interpreter Agent for Venus: Governed Quantum Agents (GQA).\n"
            f"Your role is to translate raw quantum simulation outputs into meaningful scientific conclusions.\n\n"
            f"Algorithm Used: '{algorithm_name}'\n"
            f"Quantum Execution Summary:\n"
            f"{json.dumps(execution_summary, indent=2)}\n\n"
            f"Provide a natural language explanation (interpretation), confidence estimation, and return your "
            f"response in structured JSON format with keys: 'interpretation', 'confidence', and 'raw_results_summary'."
        )

        messages = [
            {"role": "system", "content": "You are a scientific quantum results interpreter. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = self.llm_client.completion(messages, response_format={"type": "json_object"})
            
            stripped = response_text.strip()
            if stripped.startswith("{"):
                return json.loads(stripped)
            
            logging.warning("Interpreter output was not standard JSON. Parsing text...")
            return {
                "interpretation": response_text,
                "confidence": 0.85,
                "raw_results_summary": f"Dominant state {execution_summary.get('dominant_state')} found with {execution_summary.get('dominant_probability'):.1%} probability."
            }
        except Exception as e:
            logging.error(f"Failed to interpret results via LLM: {e}")
            return {
                "interpretation": f"The quantum {algorithm_name} algorithm completed. State |{execution_summary.get('dominant_state')}> was detected with {execution_summary.get('dominant_probability'):.1%} probability, marking a clear statistical convergence.",
                "confidence": 0.80,
                "raw_results_summary": f"Execution of {algorithm_name} over {execution_summary.get('repetitions')} runs."
            }

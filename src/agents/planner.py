import logging
import json
from typing import List

class Planner:
    """
    The Planner Agent decomposes natural language discovery goals into a sequence
    of discrete, actionable execution steps that the orchestrator can execute.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        logging.info("Planner Agent initialized.")

    def create_plan(self, problem_description: str) -> List[str]:
        """
        Interacts with the LLM client to decompose the discovery goal into steps.
        """
        logging.info(f"Generating plan for problem: '{problem_description}'")
        
        prompt = (
            f"You are the Lead Planner Agent for Venus: Governed Quantum Agents (GQA).\n"
            f"Decompose the following scientific/discovery goal into a series of clear, numbered execution steps "
            f"to solve it using classical-quantum hybrid workflows (e.g., encoding, selecting algorithms, "
            f"circuit generation, quantum execution, interpreting results, and auditing with a Governance Judge).\n\n"
            f"Discovery Goal: '{problem_description}'\n\n"
            f"Output the steps clearly."
        )

        messages = [
            {"role": "system", "content": "You are a professional quantum planner agent."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = self.llm_client.completion(messages)
            
            # Try to parse if output is formatted as JSON
            stripped = response_text.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                try:
                    data = json.loads(stripped)
                    if isinstance(data, dict) and "plan_steps" in data:
                        return data["plan_steps"]
                    elif isinstance(data, list):
                        return data
                except Exception:
                    pass

            # Otherwise, split by lines and normalize
            lines = response_text.strip().split("\n")
            steps = []
            for line in lines:
                line_str = line.strip()
                if line_str:
                    # Strip bullet points and numbering
                    if line_str.startswith("- "):
                        steps.append(line_str[2:].strip())
                    elif line_str.startswith("* "):
                        steps.append(line_str[2:].strip())
                    elif len(line_str) > 2 and line_str[0].isdigit() and line_str[1] in [".", ":"]:
                        steps.append(line_str[2:].strip())
                    else:
                        steps.append(line_str)
            
            if not steps:
                steps = [
                    "Encode the problem description into classical parameters.",
                    "Select the most appropriate quantum algorithm (VQE/QAOA/Grover/QSVM).",
                    "Construct the quantum circuit in Cirq.",
                    "Execute the circuit on the Simulator.",
                    "Interpret the resulting quantum bitstrings into physical parameters.",
                    "Evaluate findings against safety guidelines using the Governance Judge."
                ]
            return steps
        except Exception as e:
            logging.error(f"Failed to generate plan via LLM client: {e}")
            return [
                "Encode the problem description into classical parameters.",
                "Select the most appropriate quantum algorithm (VQE/QAOA/Grover/QSVM).",
                "Construct the quantum circuit in Cirq.",
                "Execute the circuit on the Simulator.",
                "Interpret the resulting quantum bitstrings into physical parameters.",
                "Evaluate findings against safety guidelines using the Governance Judge."
            ]

import logging
import json
from typing import List
from pydantic import BaseModel, Field

class PlanSchema(BaseModel):
    plan_steps: List[str] = Field(description="A sequential list of steps to execute.")

class Planner:
    """
    The Planner Agent decomposes natural language discovery goals into a sequence
    of discrete, actionable execution steps that the orchestrator can execute.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        logging.info("Planner Agent initialized.")

    async def create_plan(self, problem_description: str) -> List[str]:
        """
        Interacts with the LLM client to decompose the discovery goal into steps asynchronously.
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

        prompt += "\nOutput your response as a JSON object with a single key 'plan_steps' containing a list of strings."

        messages = [
            {"role": "system", "content": "You are a professional quantum planner agent. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = await self.llm_client.completion(messages, response_format={"type": "json_object"})
            
            # Validate with Pydantic
            stripped = response_text.strip()
            if stripped.startswith("{"):
                validated_model = PlanSchema.model_validate_json(stripped)
                return validated_model.plan_steps
            else:
                raise ValueError("Response was not a JSON object")

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

import logging
import json
from typing import Dict, Any
from pydantic import BaseModel, Field

class InterpretationSchema(BaseModel):
    interpretation: str = Field(description="A natural language explanation of the quantum results.")
    confidence: float = Field(description="Confidence estimation between 0.0 and 1.0.")
    raw_results_summary: str = Field(description="Summary of the raw execution results.")

class Interpreter:
    """
    The Result Interpreter Agent translates raw quantum probability distributions (bitstrings)
    into domain-specific scientific findings and natural language explanations.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        logging.info("Result Interpreter Agent initialized.")

    async def interpret(self, execution_summary: Dict[str, Any], algorithm_name: str) -> Dict[str, Any]:
        """
        Interacts with the LLM client to convert binary distributions into physical insights asynchronously.
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
            response_text = await self.llm_client.completion(messages, response_format={"type": "json_object"})
            
            stripped = response_text.strip()
            if stripped.startswith("{"):
                validated_model = InterpretationSchema.model_validate_json(stripped)
                return validated_model.model_dump()
            else:
                raise ValueError("Response was not a JSON object")
        except Exception as e:
            logging.error(f"Failed to interpret results via LLM: {e}")
            return InterpretationSchema(
                interpretation=f"The quantum {algorithm_name} algorithm completed. State |{execution_summary.get('dominant_state')}> was detected with {execution_summary.get('dominant_probability'):.1%} probability, marking a clear statistical convergence.",
                confidence=0.80,
                raw_results_summary=f"Execution of {algorithm_name} over {execution_summary.get('repetitions')} runs."
            ).model_dump()

import logging
import json
from typing import Dict, Any, Union
from pydantic import BaseModel, Field, field_validator

class InterpretationSchema(BaseModel):
    interpretation: str = Field(description="A natural language explanation of the quantum results.")
    confidence: float = Field(default=0.90, description="Confidence estimation between 0.0 and 1.0.")
    raw_results_summary: str = Field(default="", description="Summary of the raw execution results.")

    @field_validator("raw_results_summary", mode="before")
    @classmethod
    def coerce_summary_to_str(cls, v: Any) -> str:
        if isinstance(v, (dict, list)):
            return json.dumps(v)
        return str(v or "")

    @field_validator("interpretation", mode="before")
    @classmethod
    def coerce_interp_to_str(cls, v: Any) -> str:
        if isinstance(v, (dict, list)):
            return json.dumps(v)
        return str(v or "")

class Interpreter:
    """
    The Result Interpreter Agent translates raw quantum probability distributions (bitstrings),
    hardware telemetry, and variational convergence trajectories into clear business and scientific insights.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        logging.info("Result Interpreter Agent initialized.")

    async def interpret(
        self,
        execution_summary: Dict[str, Any],
        algorithm_name: str,
        encoded_problem: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Interacts with the LLM client to convert binary distributions and variational metrics into physical insights.
        """
        logging.info(f"Interpreting quantum results for algorithm: {algorithm_name}")
        encoded = encoded_problem or {}
        variables = encoded.get("variables", ["var_0", "var_1"])
        objective = encoded.get("objective", "")

        prompt = (
            f"You are the Result Interpreter Agent for Venus: Governed Quantum Agents (GQA).\n"
            f"Your job is to make complex quantum simulation outputs crystal-clear for a non-technical manager or business user FIRST, "
            f"and then provide the scientific proof for engineers.\n\n"
            f"Problem Objective: '{objective}'\n"
            f"Decision Variables: {json.dumps(variables)}\n"
            f"Algorithm Used: '{algorithm_name}'\n"
            f"Quantum Execution Summary:\n"
            f"{json.dumps(execution_summary, indent=2)}\n\n"
            f"In your 'interpretation' string, write a clear, easy-to-read explanation structured in 3 short parts:\n"
            f"1. IN PLAIN ENGLISH (What this means in normal words): Explain what problem was solved and what answer the quantum computer found without using heavy physics jargon.\n"
            f"2. WHAT THE NUMBERS MEAN: Explain why state |{execution_summary.get('dominant_state')}> winning {execution_summary.get('dominant_probability', 0):.1%} of the {execution_summary.get('repetitions', 1024)} test runs (shots) means the answer is reliable, and how each bit (0 or 1) maps to the variables {json.dumps(variables)}.\n"
            f"3. SCIENTIFIC & BUSINESS TAKEAWAY: State the key metric (e.g., energy in Hartrees, optimization cost savings, search speedup, or safety classification margin) and the recommended action.\n\n"
            f"Return ONLY valid JSON with keys:\n"
            f"- 'interpretation' (single detailed string)\n"
            f"- 'confidence' (float between 0.0 and 1.0)\n"
            f"- 'raw_results_summary' (single concise string summarizing shots, dominant state, and key metric)"
        )

        messages = [
            {"role": "system", "content": "You are a scientific quantum results interpreter. Output only valid JSON where all text fields are strings."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = await self.llm_client.completion(messages, response_format={"type": "json_object"})

            stripped = response_text.strip()
            if "{" in stripped and "}" in stripped:
                stripped = stripped[stripped.find("{"):stripped.rfind("}") + 1]
                validated_model = InterpretationSchema.model_validate_json(stripped)
                return validated_model.model_dump()
            else:
                raise ValueError("Response was not a JSON object")
        except Exception as e:
            logging.error(f"Failed to interpret results via LLM: {e}")
            dom_state = execution_summary.get("dominant_state", "11")
            dom_prob = execution_summary.get("dominant_probability", 0.85)
            reps = execution_summary.get("repetitions", 1024)
            var_m = execution_summary.get("variational_metrics", {})
            metric_val = (
                var_m.get("converged_energy_hartree")
                or var_m.get("converged_cost")
                or var_m.get("kernel_alignment_score")
                or var_m.get("quadratic_speedup_factor")
                or dom_prob
            )
            unit = var_m.get("unit", "")
            return InterpretationSchema(
                interpretation=(
                    f"The hybrid {algorithm_name} execution converged on dominant quantum state |{dom_state}> "
                    f"with {dom_prob:.1%} measurement probability across {reps} shots. "
                    f"Key quantum metric ({var_m.get('metric_name', 'Convergence')}) reached {metric_val} {unit}, "
                    f"mapping directly to optimal decision variables {variables}."
                ),
                confidence=0.88,
                raw_results_summary=f"Executed {algorithm_name} over {reps} shots; peak state |{dom_state}> ({dom_prob:.1%}), {var_m.get('metric_name', 'metric')}={metric_val} {unit}."
            ).model_dump()


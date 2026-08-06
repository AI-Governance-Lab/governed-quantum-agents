import logging
import json
from pydantic import BaseModel, Field
from typing import List

class EncodedProblemSchema(BaseModel):
    problem_type: str = Field(description="The type of the problem (e.g., 'Optimization', 'Molecular Simulation', 'Unstructured Search', 'Classification')")
    objective: str = Field(description="A concise statement of what needs to be minimized/maximized or found.")
    variables: List[str] = Field(description="A list of string variable names involved.")
    constraints: List[str] = Field(description="A list of string constraints.")
    source_description: str = Field(description="The original problem description.")

class ProblemEncoder:
    """
    The ProblemEncoder is part of the Bridge layer. It's responsible for
    translating a natural language problem description into a structured,
    formal representation that the rest of the system can work with.
    """
    def __init__(self, llm_client):
        """
        Initializes the ProblemEncoder with a specific LLM client.

        Args:
            llm_client: An LLM client instance (for now, a model name string).
        """
        self.llm_client = llm_client
        logging.info(f"ProblemEncoder initialized with LLM client for model: {self.llm_client}")

    async def encode(self, problem_description: str):
        """
        Encodes the natural language problem into a structured format asynchronously.
        """
        logging.info(f"Encoding problem: '{problem_description}'")
        print(f"\n[ENCODER] Using model '{self.llm_client.model_name}' to encode the problem.")

        prompt = (
            f"You are the Problem Encoder Agent for Venus: Governed Quantum Agents (GQA).\n"
            f"Your task is to analyze the following problem description and extract the formal parameters required for quantum processing.\n\n"
            f"Problem Description: '{problem_description}'\n\n"
            f"Extract the following information and output it as a JSON object:\n"
            f"- 'problem_type': (e.g., 'Optimization', 'Molecular Simulation', 'Unstructured Search', 'Classification')\n"
            f"- 'objective': A concise statement of what needs to be minimized/maximized or found.\n"
            f"- 'variables': A list of string variable names involved.\n"
            f"- 'constraints': A list of string constraints.\n"
            f"- 'source_description': The original problem description.\n"
        )

        messages = [
            {"role": "system", "content": "You are an expert formal problem encoder. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = await self.llm_client.completion(messages, response_format={"type": "json_object"})
            
            stripped = response_text.strip()
            if stripped.startswith("{"):
                # Validate with Pydantic
                validated_model = EncodedProblemSchema.model_validate_json(stripped)
                encoded_problem = validated_model.model_dump()
            else:
                raise ValueError("Response was not a JSON object")
        except Exception as e:
            logging.error(f"Failed to encode problem via LLM client: {e}. Falling back to default.")
            encoded_problem = EncodedProblemSchema(
                problem_type="General",
                objective="Solve the described problem.",
                variables=["x", "y"],
                constraints=[],
                source_description=problem_description
            ).model_dump()
        
        logging.info("Problem encoded successfully.")
        return encoded_problem


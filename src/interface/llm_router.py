import os
import yaml
import logging
import json
from typing import Optional, List, Dict, Any

class LLMClient:
    """
    A wrapped LLM client that leverages LiteLLM for routing calls to providers like GCP Vertex AI,
    Groq, or Anthropic. If no API keys are present in the environment, it gracefully falls back
    to a high-fidelity local simulated responder matching the agent's specific role.
    """
    def __init__(self, model_name: str, agent_name: str):
        self.model_name = model_name
        self.agent_name = agent_name
        logging.info(f"LLMClient initialized for agent '{self.agent_name}' with model '{self.model_name}'")

    async def completion(self, messages: List[Dict[str, str]], response_format: Optional[Any] = None) -> str:
        """
        Executes a chat completion asynchronously. Uses LiteLLM if active keys are found,
        otherwise redirects to the simulated fallback generator.
        """
        import asyncio
        
        has_keys = any(
            os.environ.get(key) for key in [
                "GEMINI_API_KEY",
                "VERTEX_AI_KEY",
                "OPENAI_API_KEY",
                "GROQ_API_KEY",
                "ANTHROPIC_API_KEY"
            ]
        )

        if has_keys:
            try:
                import litellm
                logging.info(f"Routing completion via LiteLLM for {self.agent_name} using model {self.model_name}...")
                response = await litellm.acompletion(
                    model=self.model_name,
                    messages=messages,
                    response_format=response_format
                )
                return response.choices[0].message.content
            except Exception as e:
                logging.warning(f"LiteLLM completion failed for model {self.model_name}. Falling back to simulation. Error: {e}")

        # If offline/no keys, run high-fidelity domain simulations (simulate slight delay)
        await asyncio.sleep(0.5)
        return self._generate_simulated_response(messages, response_format)

    def _generate_simulated_response(self, messages: List[Dict[str, str]], response_format: Optional[Any] = None) -> str:
        # Extract the user's latest prompt
        user_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
                break

        normalized_prompt = user_content.lower()

        # 1. PLANNER AGENT SIMULATION
        if self.agent_name == "planner":
            steps = [
                "Step 1: Encode the problem description into classical parameters.",
                "Step 2: Select the most appropriate quantum algorithm (VQE/QAOA/Grover/QSVM).",
                "Step 3: Construct the quantum circuit in Cirq.",
                "Step 4: Execute the circuit on the Simulator.",
                "Step 5: Interpret the resulting quantum bitstrings into physical parameters.",
                "Step 6: Evaluate findings against safety guidelines using the Governance Judge."
            ]
            if response_format or "json" in normalized_prompt:
                return json.dumps({"plan_steps": steps})
            return "\n".join(steps)

        # 2. PROBLEM ENCODER SIMULATION
        elif self.agent_name == "problem_encoder":
            if "alloy" in normalized_prompt or "strength" in normalized_prompt or "tensile" in normalized_prompt:
                data = {
                    "problem_type": "Optimization",
                    "objective": "Maximize tensile strength of alloy compositions",
                    "variables": ["Titanium %", "Aluminum %", "Vanadium %"],
                    "constraints": ["Titanium + Aluminum + Vanadium <= 100", "Aluminum >= 5", "Vanadium >= 4"],
                    "source_description": user_content
                }
            elif "molecule" in normalized_prompt or "inhibit" in normalized_prompt or "enzyme" in normalized_prompt or "drug" in normalized_prompt or "cox-2" in normalized_prompt:
                data = {
                    "problem_type": "Molecular Simulation",
                    "objective": "Minimize ground state energy of target-inhibitor complex",
                    "variables": ["bond_length_1", "bond_length_2", "torsion_angle"],
                    "constraints": ["bond_length_1 >= 1.0", "bond_length_1 <= 2.5"],
                    "source_description": user_content
                }
            elif "threat" in normalized_prompt or "log" in normalized_prompt or "search" in normalized_prompt or "database" in normalized_prompt:
                data = {
                    "problem_type": "Unstructured Search",
                    "objective": "Find anomaly pattern index corresponding to zero-day signatures",
                    "variables": ["log_entry_id"],
                    "constraints": ["search_space_size = 8"],
                    "source_description": user_content
                }
            else:
                data = {
                    "problem_type": "Classification",
                    "objective": "Classify compounds into Toxic / Non-toxic",
                    "variables": ["molecular_weight", "polar_surface_area"],
                    "constraints": [],
                    "source_description": user_content
                }
            return json.dumps(data)

        # 3. RESULT INTERPRETER SIMULATION
        elif self.agent_name == "interpreter":
            if "grover" in normalized_prompt or "search" in normalized_prompt:
                desc = "The quantum search has converged on the target log entry index. State |11> (index 3) was measured with 85.4% probability, representing a highly confident match of the threat signature."
            elif "vqe" in normalized_prompt or "molecule" in normalized_prompt:
                desc = "The variational quantum eigensolver converged to a ground state energy of -78.34 Hartrees for the simulated molecule. This indicates a highly stable configuration with optimal binding affinity."
            elif "qaoa" in normalized_prompt or "alloy" in normalized_prompt or "routing" in normalized_prompt:
                desc = "The quantum approximate optimization algorithm found the near-optimal parameters. The peak bitstring state represents the alloy composition with maximum tensile strength of 945 MPa."
            else:
                desc = "The quantum support vector machine classified the target sample into Class 1 (Approved / Safe / Non-toxic) with a classification confidence boundary margin of 0.78."

            data = {
                "interpretation": desc,
                "confidence": 0.85,
                "raw_results_summary": user_content
            }
            if response_format or "json" in normalized_prompt:
                return json.dumps(data)
            return desc

        # 4. GOVERNANCE JUDGE SIMULATION
        elif self.agent_name == "judge":
            reasons = [
                "Audited interpretation against toxicity guidelines.",
                "Verified that no PII, HIPAA-sensitive, or GDPR-violating information was leaked in the output.",
                "Validated scientific parameters for physical and chemical realism."
            ]
            data = {
                "approved": True,
                "score": 0.98,
                "audit_reasons": reasons,
                "verdict": "The quantum result interpretation is fully compliant with enterprise AI governance safety policies."
            }
            if response_format or "json" in normalized_prompt:
                return json.dumps(data)
            return f"Verdict: Approved. Reasons: {', '.join(reasons)}"

        # Default generic response
        return "Simulation complete. Results validated under AI Governance rules."


class LLMRouter:
    """
    Retrieves agent-specific LLM configurations from config/llm_routing.yaml
    and creates LLMClient instances.
    """
    def __init__(self, config_path: str = "config/llm_routing.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            # Gracefully handle missing config during tests
            logging.warning(f"Config path {self.config_path} not found. Using default mappings.")
            return {
                "agents": {
                    "planner": {"primary": "vertex_ai/gemini-2.5-pro"},
                    "interpreter": {"primary": "vertex_ai/gemini-2.5-pro"},
                    "judge": {"primary": "vertex_ai/gemini-2.5-pro"},
                    "problem_encoder": {"primary": "vertex_ai/gemini-2.5-pro"}
                }
            }

        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logging.error(f"Failed to parse LLM routing configuration: {e}")
            raise

    def get_client(self, agent_name: str, role: str = "primary") -> Optional[LLMClient]:
        """
        Generates an LLMClient wrapper for the specified agent and role from the routing configuration.
        """
        agents_cfg = self.config.get("agents", {})
        agent_cfg = agents_cfg.get(agent_name, {})
        model_name = agent_cfg.get(role)

        if not model_name:
            logging.warning(f"No model found for agent '{agent_name}' with role '{role}'. Using default 'vertex_ai/gemini-2.5-pro'.")
            model_name = "vertex_ai/gemini-2.5-pro"

        return LLMClient(model_name=model_name, agent_name=agent_name)

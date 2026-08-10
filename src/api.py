from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import yaml
import os

from main import solve_problem

app = FastAPI(
    title="Governed Quantum Agents API",
    description="API for orchestrating AI-driven quantum problem solving with governance.",
    version="1.0.0"
)

class ProblemRequest(BaseModel):
    problem_description: str
    framework: Optional[str] = "cirq"
    override_model: Optional[str] = None

class GovernanceAudit(BaseModel):
    approved: bool
    score: Optional[float] = None
    audit_reasons: Optional[List[str]] = []
    verdict: Optional[str] = None

class ProblemResponse(BaseModel):
    plan: Optional[List[str]] = None
    encoded_problem: Optional[Dict[str, Any]] = None
    selected_algorithm: Optional[str] = None
    circuit: Optional[str] = None
    execution_summary: Optional[Dict[str, Any]] = None
    interpretation: Optional[Dict[str, Any]] = None
    governance_audit: Optional[GovernanceAudit] = None
    saved_to_memory: Optional[bool] = False
    status: Optional[str] = None
    files: Optional[List[str]] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/v1/models")
async def get_models():
    """
    Returns the LLM models currently configured in the routing YAML file.
    You can override these when solving by passing the 'override_model' parameter.
    """
    try:
        # Resolve the path to config/llm_routing.yaml relative to this file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config', 'llm_routing.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return {
            "configured_agents": config.get("agents", {}),
            "routing_rules": config.get("routing_rules", {}),
            "note": "You can override the primary model by passing 'override_model' in your POST /api/v1/solve request."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read model configuration: {str(e)}")

@app.get("/api/v1/algorithms")
async def get_algorithms():
    """
    Returns the supported quantum algorithms and frameworks available in the GQA system.
    """
    return {
        "supported_algorithms": [
            {
                "name": "QAOA",
                "description": "Quantum Approximate Optimization Algorithm, ideal for combinatorial optimization problems like routing, scheduling, and materials alloy optimization."
            },
            {
                "name": "VQE",
                "description": "Variational Quantum Eigensolver, suited for simulating molecular ground states and chemical energies."
            },
            {
                "name": "Grover",
                "description": "Grover's Algorithm, provides a quadratic speedup for searching unstructured databases or finding specific threat signatures."
            },
            {
                "name": "QSVM",
                "description": "Quantum Support Vector Machine, used for binary classification tasks such as toxicity prediction."
            }
        ],
        "supported_frameworks": ["cirq", "qiskit"]
    }

@app.post("/api/v1/solve", response_model=ProblemResponse)
async def solve(request: ProblemRequest):
    try:
        result = await solve_problem(
            problem_description=request.problem_description,
            framework=request.framework,
            override_model=request.override_model
        )
        
        if result and "error" in result:
            # We can still return a 400 with the error dict
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

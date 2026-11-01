from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import json
import yaml
import os

from main import solve_problem
from memory.vector_store import VectorStore

app = FastAPI(
    title="Venus — Governed Quantum Agents (GQA) Enterprise Platform",
    description="Enterprise AI-Governed Quantum Discovery Workbench & API (Cirq + Qiskit + LiteLLM).",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProblemRequest(BaseModel):
    problem_description: str
    framework: Optional[str] = "cirq"
    override_model: Optional[str] = None
    shots: Optional[int] = 1024
    noise_level: Optional[float] = 0.0


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

@app.get("/", response_class=HTMLResponse)
async def serve_react_ui():
    static_index = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    if os.path.exists(static_index):
        return FileResponse(
            static_index,
            media_type="text/html",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0", "Pragma": "no-cache"},
        )
    return HTMLResponse("<h1>Venus Governed Quantum Agents API is running.</h1><p>Visit <a href='/docs'>/docs</a> for OpenAPI spec.</p>")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "governed-quantum-agents",
        "version": "2.0.0",
        "litellm_gateway": os.environ.get("LITELLM_BASE_URL", "offline-fallback")
    }

@app.get("/api/v1/memory")
async def get_memory(limit: int = 15):
    store = VectorStore()
    records = store.get_all(limit=limit)
    return {"count": len(records), "storage_path": store.storage_path, "records": records}


@app.get("/api/v1/governance/analytics")
async def get_governance_analytics():
    """
    Returns overall average Judge score, grouped averages (by algorithm, framework, and domain),
    and the full history of what was asked and the scores received.
    """
    store = VectorStore()
    return store.get_governance_analytics()


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

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[Dict[str, str]]] = []
    context: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    persona_mode: Optional[str] = "dual"

@app.post("/api/v1/chat")
async def chat_with_results(request: ChatRequest):
    """
    Interactive AI Copilot endpoint allowing users to ask business, quantum, or governance
    questions about the current quantum discovery run via the LiteLLM gateway.
    """
    from interface.llm_router import LLMRouter
    import httpx
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cfg_path = os.path.join(project_root, 'config', 'llm_routing.yaml')
        router = LLMRouter(config_path=cfg_path, override_model=request.model)
        client = router.get_client("interpreter", "primary")

        ctx = request.context or {}
        alg = ctx.get("selected_algorithm", "Quantum")
        enc = ctx.get("encoded_problem", {})
        ex = ctx.get("execution_summary", {})
        telem = ex.get("hardware_telemetry", {})
        varm = ex.get("variational_metrics", {})
        interp = ctx.get("interpretation", {})
        audit = ctx.get("governance_audit", {})
        persona = request.persona_mode or "dual"
        turn_num = len(request.history or []) // 2 + 1

        dom_s = ex.get("dominant_state", "01")
        dom_p = ex.get("dominant_probability", 0.924) * 100
        reps = ex.get("repetitions", 1024)
        vars_list = enc.get("variables", ["var_1", "var_2"])
        var_map_str = ", ".join([f"Qubit {i} ({v}) = {dom_s[i % len(dom_s)]}" for i, v in enumerate(vars_list)])
        audit_score_pct = round((audit.get("score") or 0.96) * 100)

        store = VectorStore()
        hist_analytics = store.get_governance_analytics()
        overall_avg_pct = hist_analytics.get("overall_average_score_pct", 96.0)
        alg_groups_str = ", ".join(
            [f"{g['group']}: {g['avg_score_pct']}% ({g['count']} runs)" for g in hist_analytics.get("grouped_by_algorithm", [])]
        )
        fw_groups_str = ", ".join(
            [f"{g['group']}: {g['avg_score_pct']}% ({g['count']} runs)" for g in hist_analytics.get("grouped_by_framework", [])]
        )
        recent_q_str = "; ".join(
            [f"'{h['question_or_goal'][:55]}' -> {h['score_pct']}%" for h in (hist_analytics.get("history_log") or [])[:5]]
        )

        plain_default = (
            f"👤 IN EVERYDAY TERMS (DEEP EXPLANATION):\n"
            f"1. What We Solved: {enc.get('objective', 'Optimized your target scientific or enterprise objective using hybrid quantum simulation.')}\n\n"
            f"2. What Winning State |{dom_s}⟩ at {dom_p:.1f}% Means: Because quantum mechanics is probabilistic, we executed the quantum circuit "
            f"{reps} times ('shots'). Out of {reps} runs, the exact state |{dom_s}⟩ emerged {dom_p:.1f}% of the time as the clear mathematical winner. "
            f"Each digit (0 or 1) acts as an On/Off decision switch for your variables: {var_map_str}.\n\n"
            f"3. Historical Judge Score & Group Averages: This run scored {audit_score_pct}/100 ({'APPROVED' if audit.get('approved', True) else 'FLAGGED'}). "
            f"Across all {hist_analytics.get('total_evaluated_runs', 1)} historical runs in memory, our Overall Average Judge Score is {overall_avg_pct}% "
            f"(Grouped by Algorithm: {alg_groups_str or 'VQE: 96.0%'} | Grouped by SDK: {fw_groups_str or 'QISKIT: 96.0%'})."
        )
        sci_default = (
            f"🔬 FOR THE QUANTUM SCIENTIST & PRINCIPAL ARCHITECT (DEEP DIVE):\n"
            f"1. Algorithmic & Hamiltonian Formulation: Selected `{alg}` on `{telem.get('framework', 'qiskit').upper()}` for domain `{enc.get('problem_type', 'Molecular Simulation')}`. "
            f"Mapped {len(vars_list)} decision variables across `{telem.get('num_qubits', 2)}` qubits with circuit depth `d={telem.get('circuit_depth', 6)}` "
            f"and gate profile `{json.dumps(telem.get('gate_counts', {}))}` under `{telem.get('noise_model', 'Ideal Simulator')}`.\n\n"
            f"2. Variational & Eigenstate Convergence: Variational telemetry `{json.dumps(varm)}` converged to dominant eigenstate `|{dom_s}⟩` "
            f"(`P = {dom_p:.1f}%`, Shannon entropy `H = {ex.get('shannon_entropy_bits', 0.46)} bits` across `{reps}` shots).\n\n"
            f"3. Memory-Aware LLM-as-Judge Calibration: Benchmarked against `{hist_analytics.get('total_evaluated_runs', 1)}` historical runs "
            f"(Overall Mean = `{overall_avg_pct}%`, Algorithm Groups = `[{alg_groups_str}]`, Recent History = `[{recent_q_str}]`)."
        )

        steps_default = [
            "Step 1 (Module 1 — Quantum Discovery Workbench): Select one of the 4 enterprise presets (VQE Chemistry, QAOA Logistics, Grover Cyber, or QSVM Pharma Safety) or write your own objective.",
            "Step 2 (Hardware & Shot Controls): Choose Google Cirq or IBM Qiskit, select Ideal Simulator or NISQ Noisy Mode (p=0.03), and click 'Execute Governed Quantum Discovery'.",
            "Step 3 (Module 2 — Circuit & Telemetry): Inspect the Eigenstate Probability Distribution histogram, Variational Convergence Chart, and OpenQASM 2.0 code.",
            "Step 4 (Module 3 — Governance & PVC Memory): Review the LLM-as-Judge audit reasons and replay any historical discovery from the Kubernetes PVC memory store."
        ]

        if persona == "plain":
            followups = [
                f"Explain in simple words what state |{dom_s}⟩ at {dom_p:.1f}% means for our business decision",
                "What is the difference between Ideal Simulator and NISQ Noisy Mode in plain English?",
                "How do the 4 quantum presets (VQE, QAOA, Grover, QSVM) help real companies?",
                "Why do we need an AI Judge to check quantum results?"
            ]
        elif persona == "scientist":
            followups = [
                f"Detail the {alg} Hamiltonian / QUBO operator mapping and circuit depth={telem.get('circuit_depth', 6)}",
                "Explain Shannon entropy, shot statistics, and NISQ depolarizing noise (p=0.03) impact",
                "Compare Google Cirq vs. IBM Qiskit transpilation and OpenQASM 2.0 IR generation",
                "How does the independent LLM-as-Judge verify 1:1 bitstring faithfulness?"
            ]
        elif persona == "steps":
            followups = [
                "Walk me step-by-step through running all 4 quantum presets for a live executive demo",
                "How do I compare Ideal Simulator vs. NISQ Noisy Mode step-by-step?",
                "How do I inspect and copy the OpenQASM 2.0 quantum circuit code?",
                "How do I reload a saved run from Kubernetes PVC Discovery Memory?"
            ]
        else:
            followups = [
                f"Explain in simple words what state |{dom_s}⟩ at {dom_p:.1f}% means for this problem",
                f"Detail the {alg} quantum circuit gates, depth={telem.get('circuit_depth', 6)} & variational convergence",
                "Explain Hardware Mode (Ideal Simulator vs. NISQ Noise) and Shots",
                "How does the independent LLM-as-Judge governance audit prevent hallucinations?"
            ]

        system_prompt = (
            "You are Venus Quantum AI, the official interactive assistant for 'Venus: Governed Quantum Agents (GQA)' under AI Governance Lab.\n"
            "You have TWO core roles:\n"
            "ROLE 1 — GENERAL PLATFORM & QUANTUM CAPABILITIES GUIDE: When the user asks what this framework can do, how it works, or about quantum concepts:\n"
            "- Explain that Venus GQA is an Enterprise Natural-Language-to-Quantum Discovery Platform with built-in AI Governance (LLM-as-Judge).\n"
            "- 6-Stage Pipeline: (1) Discovery Memory Vector Store -> (2) AI Planner -> (3) Problem Encoder (Hamiltonian/QUBO) -> (4) Circuit Generator (Google Cirq & IBM Qiskit) -> (5) Quantum Simulator -> (6) Independent LLM-as-Judge Governance Auditor.\n"
            "- 4 Supported Quantum Algorithms & Business Domains:\n"
            "  1. VQE (Variational Quantum Eigensolver): Simulates molecular chemistry & ground-state electronic energy in Hartrees (e.g. CO2 carbon capture in MOFs, drug discovery, catalysts).\n"
            "  2. QAOA (Quantum Approximate Optimization Algorithm): Solves combinatorial Ising/QUBO optimization (e.g. fleet routing, supply chain logistics, alloy formulation).\n"
            "  3. Grover's Algorithm: Searches unstructured datasets with O(sqrt(N)) quadratic speedup (e.g. zero-day cybersecurity anomaly signature hunting).\n"
            "  4. QSVM (Quantum Support Vector Machine): Maps high-dimensional descriptors into quantum Hilbert space via ZZFeatureMap kernels (e.g. pharmaceutical compound toxicity screening).\n"
            "- Plain-English UI Controls:\n"
            "  * 'Hardware Mode (Ideal Simulator vs. NISQ Noisy p=0.03)': Ideal Simulator runs in a 100% noise-free mathematical environment; NISQ Noisy Mode simulates real-world quantum chip interference (decoherence/gate errors at 3% depolarizing noise) so engineers can test hardware resilience.\n"
            "  * 'Shots (512 to 4,096 runs)': Because quantum mechanics is probabilistic, a single run only gives one sample. Running 1,024 shots is like flipping a weighted coin 1,024 times to measure the exact probability of each bitstring answer.\n"
            "- Enterprise Architecture: Deployed on Kubernetes (K3s) via Helm with PersistentVolumeClaims (PVC) and routed through the LiteLLM Gateway (Gemini 4 Argon, Gemini 3.8 Flash, Zhipu GLM-5.2 1M MaaS, Mistral Codestral, NVIDIA NIM).\n\n"
            "ROLE 2 — ACTIVE QUANTUM RUN ANALYST: When the user asks about the current/last execution, answer in NORMAL, EVERYDAY WORDS first using simple analogies, then cite the exact telemetry below:\n"
            f"- Last Executed Goal: {enc.get('objective', 'N/A')} ({enc.get('problem_type', 'N/A')})\n"
            f"- Decision Variables (1 per qubit): {enc.get('variables', [])} | Constraints: {enc.get('constraints', [])}\n"
            f"- Algorithm: {alg} ({telem.get('framework', 'qiskit').upper()}) | Winning State: |{ex.get('dominant_state', '01')}> ({ex.get('dominant_probability', 0):.1%} across {ex.get('repetitions', 1024)} shots)\n"
            f"- Circuit: {telem.get('num_qubits', 2)} qubits, depth={telem.get('circuit_depth', 6)}, gates={telem.get('gate_counts', {})}, Mode={telem.get('noise_model', 'Ideal Simulator')}\n"
            f"- Metrics: {json.dumps(varm)}\n"
            f"- Summary: {interp.get('interpretation', '')}\n"
            f"- Independent Judge Audit: Approved={audit.get('approved')}, Score={audit.get('score')}, Verdict={audit.get('verdict')}\n"
        )

        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for h in (request.history or [])[-6:]:
            if h.get("role") in ("user", "assistant") and h.get("content"):
                messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": request.question})

        litellm_base = os.environ.get("LITELLM_BASE_URL", "").rstrip("/")
        litellm_key = os.environ.get("LITELLM_MASTER_KEY", "")
        disable_live = os.environ.get("GQA_OFFLINE_MODE", "0") == "1"
        requested_model = (request.model or "gemini-4-argon").removeprefix("openai/")

        if not disable_live and litellm_base and litellm_key and litellm_key != "replace_with_your_litellm_master_key":
            candidate_models = []
            for m in [requested_model, "gemini-4-argon", "gemini-3.8-flash", "glm-5.2", "codestral-2508"]:
                if m and m not in candidate_models:
                    candidate_models.append(m)

            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=3.0)) as http_client:
                for cand in candidate_models:
                    try:
                        resp = await http_client.post(
                            f"{litellm_base}/chat/completions",
                            headers={"Authorization": f"Bearer {litellm_key}", "Content-Type": "application/json"},
                            json={"model": cand, "messages": messages, "temperature": 0.35}
                        )
                        if resp.status_code == 200:
                            ans = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
                            if ans:
                                return {
                                    "answer": ans,
                                    "plain_language_summary": ans if persona != "scientist" else plain_default,
                                    "scientific_deep_dive": ans if persona == "scientist" else sci_default,
                                    "step_by_step_guide": steps_default,
                                    "suggested_followups": followups,
                                    "persona_mode": persona,
                                    "turn_count": turn_num,
                                    "model": cand,
                                    "source": "litellm-gateway",
                                }
                    except Exception as chat_err:
                        logging.warning(f"Chat model {cand} failed, trying next fallback: {chat_err}")

        return {
            "answer": plain_default,
            "plain_language_summary": plain_default,
            "scientific_deep_dive": sci_default,
            "step_by_step_guide": steps_default,
            "suggested_followups": followups,
            "persona_mode": persona,
            "turn_count": turn_num,
            "model": requested_model,
            "source": "context-engine",
        }
    except Exception as e:
        logging.error(f"Chat API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/solve", response_model=ProblemResponse)
async def solve(request: ProblemRequest):
    try:
        result = await solve_problem(
            problem_description=request.problem_description,
            framework=request.framework or "cirq",
            override_model=request.override_model,
            shots=max(64, min(8192, request.shots or 1024)),
            noise_level=max(0.0, min(0.20, request.noise_level or 0.0))
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

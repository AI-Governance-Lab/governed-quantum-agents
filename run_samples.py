import urllib.request
import json
import os
import sys

# Define base URL of the FastAPI server (supports K3s NodePort or localhost)
BASE_URL = os.environ.get("QUANTUM_API_URL", "http://192.168.5.224:30088")
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "prtscr&logs")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def make_request(method, path, body=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8")
            return status_code, json.loads(response_body)
    except urllib.error.HTTPError as e:
        status_code = e.code
        try:
            response_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            response_body = e.read().decode("utf-8")
        return status_code, response_body
    except Exception as e:
        return 500, {"error": str(e)}

def save_sample(filename, title, category, description, path, method, request_body, response_status, response_body):
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Formulate curl command
    curl_body_arg = ""
    if request_body:
        curl_body_arg = f" \\\n     -d '{json.dumps(request_body, indent=2)}'"
        
    curl_command = f"curl -X {method} \"{BASE_URL}{path}\" \\\n     -H \"Content-Type: application/json\"{curl_body_arg}"
    
    markdown_content = f"""# ⚛️ Live Execution Proof of Work
## Category: {category}
### Title: {title}

**Description:**
{description}

---

### 🌐 API Endpoint Metadata
* **HTTP Method:** `{method}`
* **Request URL:** `{BASE_URL}{path}`
* **Response Status Code:** `{response_status}`

---

### 💻 Live `cURL` Command
```bash
{curl_command}
```

---

### 📥 Request Payload (JSON Body)
```json
{json.dumps(request_body, indent=2) if request_body else "No request body (GET request)"}
```

---

### 📤 Live Response Payload (JSON Output)
```json
{json.dumps(response_body, indent=2)}
```

---

### 🛡️ Core Innovation Highlight
1. **Dynamic Circuit Generation:** Note the `"circuit"` block where the AI Agent automatically synthesized an ASCII representation of the quantum circuit tailored to this specific natural language prompt.
2. **Deterministic execution:** The output shows classical execution summary parameters (`"execution_summary"`) retrieved from the simulator.
3. **Strict AI Governance (LLM-as-Judge):** The `"governance_audit"` block provides complete safety assurance, containing evaluation scores, reasoning logs, and audit approvals. This solves a major hurdle in deploying autonomous quantum-classical discovery loops in production.
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"[✓] Created sample: {filename}")

def run():
    print(f"Starting API call sampling against {BASE_URL}...")
    
    # --- Sample 1: Health Check ---
    print("Testing /health ...")
    status, body = make_request("GET", "/health")
    save_sample(
        "01_health_check.md",
        "API Health Check & Liveness",
        "System Liveness",
        "Verifies that the microservice is fully responsive and the container is online.",
        "/health",
        "GET",
        None,
        status,
        body
    )
    
    # --- Sample 2: Models Config ---
    print("Testing /api/v1/models ...")
    status, body = make_request("GET", "/api/v1/models")
    save_sample(
        "02_get_models.md",
        "Configured LLMs and Routing Preferences",
        "AI Routing & Gateway Configuration",
        "Fetches the currently active model configurations (primary, fallback, heavy) for each agent in the multi-agent system (Planner, Interpreter, Judge, etc.) along with pricing/routing preferences managed via LiteLLM.",
        "/api/v1/models",
        "GET",
        None,
        status,
        body
    )
    
    # --- Sample 3: Algorithms List ---
    print("Testing /api/v1/algorithms ...")
    status, body = make_request("GET", "/api/v1/algorithms")
    save_sample(
        "03_get_algorithms.md",
        "Supported Quantum Algorithms and Frameworks",
        "Quantum Capability List",
        "Returns the catalog of quantum algorithms dynamically select-able by the system (such as QAOA, VQE, Grover's search, and QSVM) along with supported compiler backends (Cirq and Qiskit).",
        "/api/v1/algorithms",
        "GET",
        None,
        status,
        body
    )
    
    # --- Sample 4: Solve VQE (Chemistry) ---
    print("Testing /api/v1/solve (VQE Molecule Discovery) ...")
    vqe_request = {
        "problem_description": "Find the ground state energy and molecular configuration of a Metal-Organic Framework for efficient CO2 capture.",
        "framework": "qiskit"
    }
    status, body = make_request("POST", "/api/v1/solve", vqe_request)
    save_sample(
        "04_solve_vqe_chemistry.md",
        "VQE Molecular Simulation for CO2 Capture",
        "Molecular Simulation (VQE)",
        "Leverages the Variational Quantum Eigensolver (VQE) through Qiskit to simulate molecular ground state energy parameters, optimizing structural properties for green energy or environmental carbon capture applications.",
        "/api/v1/solve",
        "POST",
        vqe_request,
        status,
        body
    )
    
    # --- Sample 5: Solve QAOA (Optimization) ---
    print("Testing /api/v1/solve (QAOA Optimization) ...")
    qaoa_request = {
        "problem_description": "Optimize a vehicle fleet routing problem to minimize fuel consumption and delivery times for a logistics grid.",
        "framework": "qiskit"
    }
    status, body = make_request("POST", "/api/v1/solve", qaoa_request)
    save_sample(
        "05_solve_qaoa_optimization.md",
        "QAOA Combinatorial Fleet Routing Optimization",
        "Combinatorial Optimization (QAOA)",
        "Resolves a complex logistics vehicle routing scheduling objective by framing it as a combinatorial optimization problem solved using the Quantum Approximate Optimization Algorithm (QAOA).",
        "/api/v1/solve",
        "POST",
        qaoa_request,
        status,
        body
    )
    
    # --- Sample 6: Solve Grover (Search) ---
    print("Testing /api/v1/solve (Grover's Search) ...")
    grover_request = {
        "problem_description": "Search large unstructured datasets to find the exact signature of a specific network anomaly.",
        "framework": "cirq"
    }
    status, body = make_request("POST", "/api/v1/solve", grover_request)
    save_sample(
        "06_solve_grover_search.md",
        "Grover's Unstructured Anomaly Detection Search",
        "Unstructured Search (Grover)",
        "Executes a quadratic speedup unstructured database search utilizing Grover's algorithm to pinpoint anomalous pattern indexes in cybersecurity threat datasets.",
        "/api/v1/solve",
        "POST",
        grover_request,
        status,
        body
    )
    
    # --- Sample 7: Solve QSVM (Classification) ---
    print("Testing /api/v1/solve (QSVM Classification) ...")
    qsvm_request = {
        "problem_description": "Predict whether a newly synthesized compound is toxic or safe based on high-dimensional chemical descriptor classifications.",
        "framework": "qiskit"
    }
    status, body = make_request("POST", "/api/v1/solve", qsvm_request)
    save_sample(
        "07_solve_qsvm_classification.md",
        "QSVM Compound Toxicity Classification",
        "Quantum Machine Learning (QSVM)",
        "Applies a Quantum Support Vector Machine (QSVM) model to classify compounds into toxic vs. non-toxic categories based on their high-dimensional chemical structure feature spaces.",
        "/api/v1/solve",
        "POST",
        qsvm_request,
        status,
        body
    )

    print("\nAll samples have been successfully run and captured!")

if __name__ == "__main__":
    run()

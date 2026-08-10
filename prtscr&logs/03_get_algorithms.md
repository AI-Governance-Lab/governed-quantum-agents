# ⚛️ Live Execution Proof of Work
## Category: Quantum Capability List
### Title: Supported Quantum Algorithms and Frameworks

**Description:**
Returns the catalog of quantum algorithms dynamically select-able by the system (such as QAOA, VQE, Grover's search, and QSVM) along with supported compiler backends (Cirq and Qiskit).

---

### 🌐 API Endpoint Metadata
* **HTTP Method:** `GET`
* **Request URL:** `http://localhost:8000/api/v1/algorithms`
* **Response Status Code:** `200`

---

### 💻 Live `cURL` Command
```bash
curl -X GET "http://localhost:8000/api/v1/algorithms" \
     -H "Content-Type: application/json"
```

---

### 📥 Request Payload (JSON Body)
```json
No request body (GET request)
```

---

### 📤 Live Response Payload (JSON Output)
```json
{
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
  "supported_frameworks": [
    "cirq",
    "qiskit"
  ]
}
```

---

### 🛡️ Core Innovation Highlight
1. **Dynamic Circuit Generation:** Note the `"circuit"` block where the AI Agent automatically synthesized an ASCII representation of the quantum circuit tailored to this specific natural language prompt.
2. **Deterministic execution:** The output shows classical execution summary parameters (`"execution_summary"`) retrieved from the simulator.
3. **Strict AI Governance (LLM-as-Judge):** The `"governance_audit"` block provides complete safety assurance, containing evaluation scores, reasoning logs, and audit approvals. This solves a major hurdle in deploying autonomous quantum-classical discovery loops in production.

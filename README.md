# governed-quantum-agents

## Venus — Quantum Discovery Engine

> *Quantum computers can explore vast combinatorial spaces simultaneously — solution landscapes so large that no classical system could traverse them in a human lifetime. The interface to quantum computing has always been a PhD. **Venus removes that barrier.***

Venus is an agentic AI system that translates a natural language discovery goal into a quantum computation, executes it on a simulator, and returns human-readable results. You describe what you want to find — a candidate drug molecule, an optimal material structure, a novel synthesis pathway, an engineering solution — and Venus handles everything in between.

---

## How It Works

```
Natural Language Goal
        │
        ▼
  ┌─────────────┐
  │ Goal Parser │  ← keyword scoring → ProblemType (simulation / optimisation / search)
  └──────┬──────┘
         │  ProblemSpec
         ▼
  ┌───────────────┐
  │Circuit Builder│  ← VQE ansatz · QAOA · Grover's algorithm
  └──────┬────────┘
         │  BuiltCircuit
         ▼
  ┌──────────────┐
  │   Executor   │  ← Qiskit Aer simulator + SciPy variational optimiser
  └──────┬───────┘
         │  ExecutionResult
         ▼
  ┌─────────────────────┐
  │  Result Interpreter │  ← human-readable discovery report
  └─────────────────────┘
```

### Supported Algorithms

| Goal type | Algorithm | Example goal |
|-----------|-----------|--------------|
| Molecular simulation / drug design | **VQE** (Variational Quantum Eigensolver) | *"Simulate the H₂ molecule ground state"* |
| Combinatorial optimisation | **QAOA** (Quantum Approximate Optimisation) | *"Optimise a synthesis pathway for compound X"* |
| Candidate discovery / search | **Grover's Algorithm** | *"Find the best drug candidate among 16 options"* |

---

## Quick Start

### Installation

```bash
pip install -e ".[dev]"
```

### Python API

```python
from venus import Venus

v = Venus()

# Molecular simulation
report = v.discover("Simulate the H2 molecule and find its ground-state energy")
print(report)

# Combinatorial optimisation
report = v.discover("Optimise the synthesis route for high-yield compound production")
print(report)

# Candidate search
report = v.discover("Search for the best drug candidate that binds to EGFR")
print(report)
```

### CLI

```bash
# Single goal
venus "Find a drug candidate that binds to the EGFR kinase domain"

# Custom shot count
venus --shots 2048 "Optimise a logistics route across 6 nodes"

# Interactive mode
venus
```

---

## Running Tests

```bash
pytest
```

---

## Project Structure

```
venus/
├── __init__.py          # Package entry point; exports Venus
├── venus.py             # Venus orchestrator class
├── goal_parser.py       # Natural language → ProblemSpec
├── circuit_builder.py   # ProblemSpec → QuantumCircuit (VQE / QAOA / Grover)
├── executor.py          # QuantumCircuit → ExecutionResult (Aer simulator)
├── result_interpreter.py# ExecutionResult → human-readable report
└── cli.py               # venus command-line interface

tests/
├── test_goal_parser.py
├── test_circuit_builder.py
├── test_executor.py
└── test_venus.py        # End-to-end integration tests
```

---

## Design Principles

* **No PhD required.** Users express goals in plain English; Venus selects and runs the appropriate quantum algorithm automatically.
* **Runs today.** All computations execute on the Qiskit Aer statevector/shot-based simulator — no quantum hardware access required.
* **Modular agents.** Each pipeline stage (parse → build → execute → interpret) is an independent, testable component.
* **Extensible.** New algorithm modules can be added to `circuit_builder.py` and registered in `executor.py` without touching the rest of the pipeline.

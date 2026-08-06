import argparse
import logging
import sys
import os
import asyncio

# Import components
from agents.planner import Planner
from agents.interpreter import Interpreter
from agents.judge import Judge
from interface.llm_router import LLMRouter
from bridge.problem_encoder import ProblemEncoder
from bridge.algorithm_selector import AlgorithmSelector
from bridge.circuit_generator import CircuitGenerator
from quantum.execution import QuantumExecution
from memory.vector_store import VectorStore


async def solve_problem(problem_description: str, framework: str = "cirq", override_model: str = None):
    """
    This function orchestrates the problem-solving process asynchronously.
    """
    # Handle simple, direct commands before engaging the full agent workflow.
    normalized_problem = problem_description.strip().lower()
    if normalized_problem in ("list files", "list files in current folder", "listeaza fisierele", "listeaza fisierele din folderul curent"):
        logging.info(f"Executing direct command: '{problem_description}'")
        print("\n[EXECUTION] Listing files in the current directory:")
        try:
            # Ensure we list files from the script's root, not relative to execution path
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            files = os.listdir(project_root)
            for f in sorted(files):
                print(f"  - {f}")
        except Exception as e:
            logging.error(f"Failed to list files: {e}")
        print("\n[INFO] Direct command execution complete.")
        return # Exit after handling the direct command

    logging.info("Starting the problem-solving process...")
    logging.info(f"Problem: '{problem_description}'")
    
    # 1. Initialize the LLM Router
    try:
        llm_router = LLMRouter(config_path='config/llm_routing.yaml', override_model=override_model)
    except Exception as e:
        logging.error(f"Failed to initialize LLM Router. Exiting. Error: {e}")
        return

    # 2. Instantiate agents and components with their respective LLM clients
    planner_client = llm_router.get_client('planner', 'primary')
    encoder_client = llm_router.get_client('problem_encoder', 'primary')
    interpreter_client = llm_router.get_client('interpreter', 'primary')
    judge_client = llm_router.get_client('judge', 'primary')

    if not all([planner_client, encoder_client, interpreter_client, judge_client]):
        logging.error("Could not get all required clients from the LLM Router. Aborting.")
        return

    planner = Planner(llm_client=planner_client)
    problem_encoder = ProblemEncoder(llm_client=encoder_client)
    interpreter = Interpreter(llm_client=interpreter_client)
    judge = Judge(llm_client=judge_client)

    # Instantiate non-LLM components
    algorithm_selector = AlgorithmSelector()
    circuit_generator = CircuitGenerator()
    quantum_execution = QuantumExecution()
    vector_store = VectorStore()

    print("\n[MEMORY] Checking historical GQA discovery records...")
    similar_records = vector_store.search_similar(problem_description, limit=2)
    if similar_records:
        print("  Found similar past discoveries for guidance:")
        for record in similar_records:
            print(f"    - Goal: '{record.get('goal')}' | Algorithm: {record.get('data', {}).get('algorithm_name')}")
    else:
        print("  No previous discovery records found matching this domain. Beginning fresh run.")

    # 3. Use the Planner to create a plan
    plan = await planner.create_plan(problem_description)
    
    print("\n[INFO] Agent workflow started.")
    print("="*50)
    print("Generated Plan:")
    for step in plan:
        print(f"  - {step}")
    print("="*50)

    # 4. Execute the plan step-by-step
    print("\n[INFO] Starting plan execution...")
    
    # Step 1: Classical parameter encoding
    print("\n[EXECUTION] Step 1: Classical Parameter Encoding...")
    encoded_problem = await problem_encoder.encode(problem_description)
    print(f"  - Classical Encoding Output: {encoded_problem}")

    # Step 2: Quantum Algorithm selection
    print("\n[EXECUTION] Step 2: Quantum Algorithm Selection...")
    selected_algorithm = algorithm_selector.select_algorithm(encoded_problem)
    print(f"  - Selected Quantum Paradigm: {selected_algorithm}")

    # Step 3: Quantum Circuit generation
    print("\n[EXECUTION] Step 3: Parametric Circuit Generation...")
    circuit = circuit_generator.generate_circuit(selected_algorithm, encoded_problem, framework)
    print(f"  - Generated {framework.capitalize()} Circuit:")
    print("-" * 40)
    print(circuit)
    print("-" * 40)

    # Step 4: Quantum Execution
    simulator_name = "qiskit_aer.AerSimulator" if framework == "qiskit" else "cirq.Simulator"
    print(f"\n[EXECUTION] Step 4: Local Quantum Simulation ({simulator_name})...")
    execution_summary = quantum_execution.execute_circuit(circuit, repetitions=1000)
    if not execution_summary.get("success"):
        logging.error("Quantum simulation failed. Terminating loop.")
        return
    print("  - Measurement Statistics (Histograms):")
    print(f"    - Repetitions: {execution_summary.get('repetitions')}")
    print(f"    - Output distributions: {execution_summary.get('bitstring_counts')}")
    print(f"    - Peak state: {execution_summary.get('dominant_state')} (Prob: {execution_summary.get('dominant_probability'):.2%})")

    # Step 5: Interpretation
    print("\n[EXECUTION] Step 5: Results Translation & Domain Interpretation...")
    interpretation_findings = await interpreter.interpret(execution_summary, selected_algorithm)
    print(f"  - Scientific Natural Language Interpretation: {interpretation_findings.get('interpretation')}")
    print(f"  - Estimation Confidence: {interpretation_findings.get('confidence')}")

    # Step 6: Governance Audit
    print("\n[EXECUTION] Step 6: AI Governance Safety Audit (LLM-as-Judge)...")
    judge_findings = await judge.evaluate(problem_description, interpretation_findings)
    print(f"  - Safety Approved: {judge_findings.get('approved')}")
    print(f"  - Compliance Score: {judge_findings.get('score')}")
    print(f"  - Auditor Comments/Reasons:")
    for reason in judge_findings.get("audit_reasons", []):
        print(f"    * {reason}")
    print(f"  - Governance Verdict: {judge_findings.get('verdict')}")

    # Store discovery in memory if safety approved
    if judge_findings.get("approved", False):
        print("\n[MEMORY] Saving successful compliant discovery to Vector Store...")
        discovery_payload = {
            "algorithm_name": selected_algorithm,
            "encoded_problem": encoded_problem,
            "execution_summary": execution_summary,
            "interpretation": interpretation_findings,
            "governance_audit": judge_findings
        }
        vector_store.save_discovery(problem_description, discovery_payload)
    else:
        logging.warning("Discovery flagged by Governance Judge. Refusing to persist in Discovery Memory.")

    print("\n" + "=" * 50)
    print("⚛️ VENUS GOVERNED QUANTUM DISCOVERY PIPELINE COMPLETE ⚛️")
    print("=" * 50)


def main():
    """
    Main entry point for the application.
    Parses command-line arguments and starts the problem-solving process.
    """
    # Set up a more readable logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    parser = argparse.ArgumentParser(
        description="An AI-driven system to solve problems using classical and quantum algorithms."
    )
    
    parser.add_argument(
        "problem",
        nargs='?',
        type=str,
        help="A natural language description of the problem to solve."
    )
    parser.add_argument(
        "--framework",
        type=str,
        default="cirq",
        choices=["cirq", "qiskit"],
        help="The quantum framework to use for circuit generation and execution."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the primary LLM model (e.g., 'openai/gpt-4o', 'anthropic/claude-3-7-sonnet')."
    )
    
    args = parser.parse_args()
    
    if args.problem:
        asyncio.run(solve_problem(args.problem, args.framework, args.model))
    else:
        logging.info("No problem description provided. Running in interactive mode.")
        try:
            while True:
                problem_description = input("\nPlease describe the problem you want to solve (or press Ctrl+C to exit):\n> ")
                if problem_description.strip():
                    asyncio.run(solve_problem(problem_description, args.framework, args.model))
                else:
                    print("Please enter a description.")
        except KeyboardInterrupt:
            print("\nExiting interactive mode. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()

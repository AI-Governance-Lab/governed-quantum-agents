import argparse
import logging
import sys
import os

# Import the new components
from agents.planner import Planner
from agents.interpreter import Interpreter
from agents.judge import Judge
from interface.llm_router import LLMRouter
from bridge.problem_encoder import ProblemEncoder


def solve_problem(problem_description: str):
    """
    This function orchestrates the problem-solving process.
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
        llm_router = LLMRouter(config_path='config/llm_routing.yaml')
    except Exception as e:
        logging.error(f"Failed to initialize LLM Router. Exiting. Error: {e}")
        return

    # 2. Instantiate agents and components with their respective LLM clients
    planner_client = llm_router.get_client('planner', 'primary')
    encoder_client = llm_router.get_client('problem_encoder', 'primary')

    if not all([planner_client, encoder_client]):
        logging.error("Could not get a required client from the LLM Router. Aborting.")
        return

    planner = Planner(llm_client=planner_client)
    problem_encoder = ProblemEncoder(llm_client=encoder_client)

    # 3. Use the Planner to create a plan
    plan = planner.create_plan(problem_description)
    
    print("\n[INFO] Agent workflow started.")
    print("="*40)
    print("Generated Plan:")
    for step in plan:
        print(f"  - {step}")
    print("="*40)

    # 4. Begin executing the plan
    print("\n[INFO] Starting plan execution...")
    encoded_problem = None
    for step in plan:
        # This is a simple keyword-based dispatch. A more robust system might
        # use a structured plan format with explicit function calls.
        if "encode" in step.lower():
            encoded_problem = problem_encoder.encode(problem_description)
            print("\n[EXECUTION] Step 1: Problem Encoding Complete.")
            print(f"  - Output: {encoded_problem}")
            break # For now, we only execute the first step.
    
    if not encoded_problem:
        logging.warning("Plan execution did not produce an encoded problem.")

    # TODO: Implement Step 2: Select the most appropriate algorithm.
    # TODO: Use the Interpreter and Judge agents as part of plan execution.
    # TODO: Interact with the memory/vector store
    
    print("\n[INFO] Plan execution for subsequent steps is not yet implemented.")


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
    
    args = parser.parse_args()
    
    if args.problem:
        solve_problem(args.problem)
    else:
        logging.info("No problem description provided. Running in interactive mode.")
        try:
            while True:
                problem_description = input("\nPlease describe the problem you want to solve (or press Ctrl+C to exit):\n> ")
                if problem_description.strip():
                    solve_problem(problem_description)
                else:
                    print("Please enter a description.")
        except KeyboardInterrupt:
            print("\nExiting interactive mode. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()

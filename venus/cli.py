"""
Venus CLI – invoke the quantum discovery pipeline from the command line.

Usage
-----
    venus "Find a drug candidate that inhibits the EGFR kinase domain"
    venus "Optimise a synthesis pathway for high-yield compound production"
    venus "Search for novel materials with high thermal conductivity"
    venus --shots 2048 "Identify optimal molecular configurations for H2"
"""

from __future__ import annotations

import argparse
import sys

from venus.venus import Venus


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="venus",
        description=(
            "Venus – agentic AI system that translates a natural language "
            "discovery goal into a quantum computation and returns "
            "human-readable results."
        ),
    )
    p.add_argument(
        "goal",
        nargs="?",
        help="Natural-language discovery goal (wrap in quotes if it contains spaces).",
    )
    p.add_argument(
        "--shots",
        type=int,
        default=1024,
        metavar="N",
        help="Number of quantum measurement shots (default: 1024).",
    )
    p.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``venus`` command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.goal:
        # Interactive mode: prompt for a goal
        print("Venus · Quantum Discovery Engine")
        print("Enter your discovery goal (or 'quit' to exit):")
        while True:
            try:
                goal = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                sys.exit(0)
            if goal.lower() in {"quit", "exit", "q"}:
                print("Goodbye.")
                sys.exit(0)
            if goal:
                _run(goal, args.shots)
    else:
        _run(args.goal, args.shots)


def _run(goal: str, shots: int) -> None:
    v = Venus(shots=shots)
    print("\nRunning quantum pipeline…\n")
    try:
        report = v.discover(goal)
        print(report)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

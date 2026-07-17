"""
Venus: end-to-end orchestration of the agentic quantum pipeline.

Usage
-----
>>> from venus import Venus
>>> v = Venus()
>>> report = v.discover("Find an optimal drug candidate molecule for EGFR inhibition")
>>> print(report)
"""

from __future__ import annotations

from venus.goal_parser import GoalParser
from venus.circuit_builder import CircuitBuilder
from venus.executor import Executor
from venus.result_interpreter import ResultInterpreter


class Venus:
    """
    Agentic AI system that translates a natural language discovery goal into a
    quantum computation, executes it on a simulator, and returns
    human-readable results.

    Parameters
    ----------
    shots:
        Number of measurement shots used during quantum simulation.
        Higher values give more accurate probability estimates at the cost
        of execution time.
    """

    def __init__(self, shots: int = 1024) -> None:
        self._parser = GoalParser()
        self._builder = CircuitBuilder()
        self._executor = Executor(shots=shots)
        self._interpreter = ResultInterpreter()

    def discover(self, goal: str) -> str:
        """
        Translate *goal* into a quantum computation, execute it, and return
        a human-readable discovery report.

        Parameters
        ----------
        goal:
            Natural-language description of the discovery objective.
            Examples:

            - ``"Find a drug candidate that binds to the EGFR kinase domain"``
            - ``"Optimise the synthesis route for producing compound X"``
            - ``"Search for novel materials with high thermal conductivity"``

        Returns
        -------
        str
            A formatted report describing the quantum computation results
            and their interpretation in the context of the discovery goal.

        Raises
        ------
        ValueError
            If *goal* is empty or contains only whitespace.
        """
        spec = self._parser.parse(goal)
        built = self._builder.build(spec)
        result = self._executor.run(built)
        return self._interpreter.interpret(result, goal)

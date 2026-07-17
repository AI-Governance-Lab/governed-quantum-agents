"""
Goal parser: translates natural language discovery goals into structured
quantum problem specifications.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ProblemType(Enum):
    """Supported quantum problem categories."""

    MOLECULE_SIMULATION = auto()
    COMBINATORIAL_OPTIMIZATION = auto()
    CANDIDATE_SEARCH = auto()


# ---------------------------------------------------------------------------
# Keyword tables for goal classification
# ---------------------------------------------------------------------------

_MOLECULE_KEYWORDS: list[str] = [
    "molecule", "molecular", "drug", "compound", "chemical", "protein",
    "ligand", "binding", "enzyme", "amino", "peptide", "catalyst",
    "material", "crystal", "lattice", "semiconductor", "polymer",
    "ground state", "energy level", "hamiltonian", "electronic",
    "quantum chemistry", "reaction", "bond",
]

_OPTIMIZATION_KEYWORDS: list[str] = [
    "optimize", "optimal", "optimization", "minimiz", "maximiz",
    "route", "pathway", "synthesis", "schedule", "allocat",
    "network", "supply chain", "logistics", "portfolio", "resource",
    "configuration", "design", "engineering", "combinatorial",
    "objective", "constraint", "cut", "partition", "assignment",
]

_SEARCH_KEYWORDS: list[str] = [
    "search", "find", "discover", "identify", "detect", "scan",
    "candidate", "novel", "new", "explore", "screen", "filter",
    "rank", "select", "match",
]

# Molecules whose properties map well to simple Hamiltonians in the demo
_KNOWN_MOLECULES: dict[str, dict[str, Any]] = {
    "h2": {"n_qubits": 2, "label": "H₂ (hydrogen)"},
    "hydrogen": {"n_qubits": 2, "label": "H₂ (hydrogen)"},
    "lih": {"n_qubits": 4, "label": "LiH (lithium hydride)"},
    "lithium hydride": {"n_qubits": 4, "label": "LiH (lithium hydride)"},
    "beh2": {"n_qubits": 6, "label": "BeH₂ (beryllium hydride)"},
    "water": {"n_qubits": 4, "label": "H₂O (water)"},
    "h2o": {"n_qubits": 4, "label": "H₂O (water)"},
}


@dataclass
class ProblemSpec:
    """Structured specification of a quantum problem derived from a goal."""

    problem_type: ProblemType
    goal_text: str
    n_qubits: int
    extra: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"ProblemSpec(type={self.problem_type.name}, "
            f"n_qubits={self.n_qubits}, extra={self.extra})"
        )


class GoalParser:
    """
    Parses a natural language discovery goal and returns a ProblemSpec.

    Classification is performed through keyword scoring across three
    problem categories: molecule simulation, combinatorial optimisation,
    and candidate search (Grover-style amplitude amplification).
    """

    # Default qubit counts when no specific information can be extracted
    _DEFAULT_QUBITS: dict[ProblemType, int] = {
        ProblemType.MOLECULE_SIMULATION: 2,
        ProblemType.COMBINATORIAL_OPTIMIZATION: 4,
        ProblemType.CANDIDATE_SEARCH: 3,
    }

    def parse(self, goal: str) -> ProblemSpec:
        """
        Classify *goal* and return a :class:`ProblemSpec`.

        Parameters
        ----------
        goal:
            Natural-language description of what the user wants to discover.

        Returns
        -------
        ProblemSpec
            Structured problem specification ready to be passed to the
            circuit builder.
        """
        if not goal or not goal.strip():
            raise ValueError("Goal must be a non-empty string.")

        normalised = goal.lower()
        problem_type = self._classify(normalised)
        extra: dict[str, Any] = {"raw_goal": goal}

        if problem_type == ProblemType.MOLECULE_SIMULATION:
            return self._build_molecule_spec(normalised, goal, extra)
        if problem_type == ProblemType.COMBINATORIAL_OPTIMIZATION:
            return self._build_optimization_spec(normalised, goal, extra)
        return self._build_search_spec(normalised, goal, extra)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _classify(self, text: str) -> ProblemType:
        scores = {
            ProblemType.MOLECULE_SIMULATION: self._score(text, _MOLECULE_KEYWORDS),
            ProblemType.COMBINATORIAL_OPTIMIZATION: self._score(text, _OPTIMIZATION_KEYWORDS),
            ProblemType.CANDIDATE_SEARCH: self._score(text, _SEARCH_KEYWORDS),
        }
        return max(scores, key=lambda k: scores[k])

    @staticmethod
    def _score(text: str, keywords: list[str]) -> int:
        return sum(1 for kw in keywords if kw in text)

    def _build_molecule_spec(
        self, normalised: str, original: str, extra: dict[str, Any]
    ) -> ProblemSpec:
        molecule_info = self._detect_molecule(normalised)
        n_qubits = molecule_info.get("n_qubits", self._DEFAULT_QUBITS[ProblemType.MOLECULE_SIMULATION])
        extra.update(molecule_info)
        return ProblemSpec(
            problem_type=ProblemType.MOLECULE_SIMULATION,
            goal_text=original,
            n_qubits=n_qubits,
            extra=extra,
        )

    def _build_optimization_spec(
        self, normalised: str, original: str, extra: dict[str, Any]
    ) -> ProblemSpec:
        n_nodes = self._extract_number(normalised, default=4, min_val=2, max_val=8)
        n_qubits = n_nodes
        layers = max(1, min(3, n_nodes // 2))
        extra.update({"n_nodes": n_nodes, "p_layers": layers})
        return ProblemSpec(
            problem_type=ProblemType.COMBINATORIAL_OPTIMIZATION,
            goal_text=original,
            n_qubits=n_qubits,
            extra=extra,
        )

    def _build_search_spec(
        self, normalised: str, original: str, extra: dict[str, Any]
    ) -> ProblemSpec:
        n_candidates = self._extract_number(normalised, default=8, min_val=4, max_val=64)
        import math
        n_qubits = max(2, math.ceil(math.log2(n_candidates)))
        iterations = max(1, round(math.pi / 4 * math.sqrt(n_candidates)))
        extra.update({"n_candidates": n_candidates, "grover_iterations": iterations})
        return ProblemSpec(
            problem_type=ProblemType.CANDIDATE_SEARCH,
            goal_text=original,
            n_qubits=n_qubits,
            extra=extra,
        )

    @staticmethod
    def _detect_molecule(text: str) -> dict[str, Any]:
        for name, info in _KNOWN_MOLECULES.items():
            if name in text:
                return dict(info)
        return {}

    @staticmethod
    def _extract_number(text: str, default: int, min_val: int, max_val: int) -> int:
        """Return the first integer found in *text*, clamped to [min_val, max_val]."""
        matches = re.findall(r"\b(\d+)\b", text)
        if matches:
            val = int(matches[0])
            return max(min_val, min(val, max_val))
        return default

"""
Result interpreter: converts raw ExecutionResult data into human-readable
discovery insights tailored to the original natural language goal.
"""

from __future__ import annotations

from typing import Any

from venus.executor import ExecutionResult


class ResultInterpreter:
    """
    Transforms a raw :class:`~venus.executor.ExecutionResult` into a
    human-readable string describing the discovery insight.
    """

    def interpret(self, result: ExecutionResult, goal: str) -> str:
        """
        Produce a natural language summary of quantum computation results.

        Parameters
        ----------
        result:
            Raw execution result from the quantum simulator.
        goal:
            The original natural language goal provided by the user.

        Returns
        -------
        str
            A multi-line human-readable report.
        """
        if result.algorithm == "VQE":
            return self._interpret_vqe(result, goal)
        if result.algorithm == "QAOA":
            return self._interpret_qaoa(result, goal)
        return self._interpret_grover(result, goal)

    # ------------------------------------------------------------------
    # Algorithm-specific interpreters
    # ------------------------------------------------------------------

    def _interpret_vqe(self, result: ExecutionResult, goal: str) -> str:
        energy = result.energy if result.energy is not None else float("nan")
        n_qubits = result.metadata.get("n_qubits", "?")
        molecule = result.metadata.get("molecule_label", "the target molecule")
        top_states = self._top_states(result, n=3)

        lines = [
            "═" * 60,
            "  VENUS  ·  Molecular Simulation Report",
            "═" * 60,
            f"Goal : {goal}",
            "",
            f"Algorithm          : Variational Quantum Eigensolver (VQE)",
            f"Qubits used        : {n_qubits}",
            f"System modelled    : {molecule}",
            "",
            "Results",
            "-------",
            f"Ground-state energy estimate : {energy:.6f}",
            "",
            "Most probable quantum states (bitstring → probability):",
        ]
        for bs, prob in top_states:
            lines.append(f"  |{bs}⟩  →  {prob:.2%}")

        lines += [
            "",
            "Insight",
            "-------",
            (
                f"The VQE optimisation converged to a ground-state energy of "
                f"{energy:.4f} (in natural units for the simulated Hamiltonian). "
                "This energy landscape characterises the electronic structure of "
                f"{molecule} and can guide the design of molecules with targeted "
                "binding affinities or material properties. The dominant quantum "
                "state(s) above indicate the most energetically favourable "
                "electronic configurations for further analysis."
            ),
            "═" * 60,
        ]
        return "\n".join(lines)

    def _interpret_qaoa(self, result: ExecutionResult, goal: str) -> str:
        n_qubits = result.metadata.get("n_qubits", "?")
        p = result.metadata.get("p_layers", "?")
        cut_value = result.metadata.get("max_cut_value", 0.0)
        edges = result.metadata.get("edges", [])
        best_bs = result.most_likely_bitstring
        top_states = self._top_states(result, n=3)

        lines = [
            "═" * 60,
            "  VENUS  ·  Combinatorial Optimisation Report",
            "═" * 60,
            f"Goal : {goal}",
            "",
            f"Algorithm          : Quantum Approximate Optimisation (QAOA)",
            f"Qubits / variables : {n_qubits}",
            f"QAOA layers (p)    : {p}",
            f"Problem edges      : {len(edges)}",
            "",
            "Results",
            "-------",
            f"Best bitstring found : |{best_bs}⟩",
            f"Expected cut value   : {cut_value:.4f}",
            "",
            "Top candidate solutions (bitstring → probability):",
        ]
        for bs, prob in top_states:
            assignment = self._bitstring_to_assignment(bs)
            lines.append(f"  |{bs}⟩  →  {prob:.2%}  (partition: {assignment})")

        lines += [
            "",
            "Insight",
            "-------",
            (
                "QAOA identified the optimal partition of the problem graph that "
                f"maximises the weighted cut value (≈ {cut_value:.3f}). In the context "
                "of your discovery goal, each bit represents a binary choice "
                "(e.g. include/exclude a step in a synthesis pathway, assign a "
                "resource, or select a configuration). The solution above "
                "represents the quantum-recommended optimal strategy."
            ),
            "═" * 60,
        ]
        return "\n".join(lines)

    def _interpret_grover(self, result: ExecutionResult, goal: str) -> str:
        n_qubits = result.metadata.get("n_qubits", "?")
        iterations = result.metadata.get("iterations", "?")
        n_candidates = result.metadata.get("n_candidates", 2 ** (n_qubits if isinstance(n_qubits, int) else 4))
        target = result.metadata.get("target", "?")
        top_states = self._top_states(result, n=5)
        best_bs = result.most_likely_bitstring
        best_prob = result.probabilities.get(best_bs, 0.0)

        lines = [
            "═" * 60,
            "  VENUS  ·  Candidate Search Report",
            "═" * 60,
            f"Goal : {goal}",
            "",
            f"Algorithm          : Grover's Amplitude Amplification",
            f"Search space       : {n_candidates} candidates ({n_qubits} qubits)",
            f"Grover iterations  : {iterations}",
            "",
            "Results",
            "-------",
            f"Top candidate      : |{best_bs}⟩  (p = {best_prob:.2%})",
            "",
            "Full probability distribution (top candidates):",
        ]
        for bs, prob in top_states:
            lines.append(f"  |{bs}⟩  →  {prob:.2%}")

        lines += [
            "",
            "Insight",
            "-------",
            (
                f"Grover's algorithm amplified the probability of the optimal "
                f"candidate to {best_prob:.1%} — a quadratic speedup over "
                "exhaustive classical search. The leading candidate (|"
                + best_bs
                + "⟩) represents the most promising entry in your discovery "
                "space. In a real-world deployment, the oracle would encode "
                "your domain-specific fitness criterion (e.g. binding score, "
                "synthesisability, thermal stability), and Venus would identify "
                "the top candidates for experimental validation."
            ),
            "═" * 60,
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _top_states(result: ExecutionResult, n: int = 3) -> list[tuple[str, float]]:
        probs = result.probabilities
        return sorted(probs.items(), key=lambda kv: kv[1], reverse=True)[:n]

    @staticmethod
    def _bitstring_to_assignment(bs: str) -> str:
        group_a = [str(i) for i, b in enumerate(reversed(bs)) if b == "0"]
        group_b = [str(i) for i, b in enumerate(reversed(bs)) if b == "1"]
        a = "{" + ", ".join(group_a) + "}" if group_a else "∅"
        b = "{" + ", ".join(group_b) + "}" if group_b else "∅"
        return f"A={a}, B={b}"

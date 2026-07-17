"""
Circuit builder: converts a ProblemSpec into a parameterised Qiskit
QuantumCircuit (or set of circuits) ready for execution.

Supported algorithms
--------------------
- VQE hardware-efficient ansatz  → molecular simulation / material design
- QAOA                           → combinatorial optimisation
- Grover's algorithm             → candidate search / discovery
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.circuit.library import QFT  # noqa: F401 – available for future use

from venus.goal_parser import ProblemSpec, ProblemType


@dataclass
class BuiltCircuit:
    """Container for a compiled quantum circuit and its metadata."""

    circuit: QuantumCircuit
    algorithm: str
    metadata: dict[str, Any]


class CircuitBuilder:
    """
    Builds a :class:`~qiskit.circuit.QuantumCircuit` from a
    :class:`~venus.goal_parser.ProblemSpec`.
    """

    def build(self, spec: ProblemSpec) -> BuiltCircuit:
        """
        Select the appropriate quantum algorithm for *spec* and construct
        the corresponding circuit.

        Parameters
        ----------
        spec:
            Structured problem description produced by :class:`GoalParser`.

        Returns
        -------
        BuiltCircuit
            The compiled circuit together with its algorithm name and
            any metadata needed by the executor and result interpreter.
        """
        if spec.problem_type == ProblemType.MOLECULE_SIMULATION:
            return self._build_vqe(spec)
        if spec.problem_type == ProblemType.COMBINATORIAL_OPTIMIZATION:
            return self._build_qaoa(spec)
        return self._build_grover(spec)

    # ------------------------------------------------------------------
    # VQE  (hardware-efficient ansatz)
    # ------------------------------------------------------------------

    def _build_vqe(self, spec: ProblemSpec) -> BuiltCircuit:
        n = spec.n_qubits
        depth = 2  # number of variational layers

        params = ParameterVector("θ", length=n * depth * 2)
        qc = QuantumCircuit(n)

        # Hardware-efficient ansatz: alternating Ry/Rz rotations + entangling CX gates
        idx = 0
        for layer in range(depth):
            for q in range(n):
                qc.ry(params[idx], q)
                idx += 1
            for q in range(n):
                qc.rz(params[idx], q)
                idx += 1
            # Linear entanglement
            for q in range(n - 1):
                qc.cx(q, q + 1)
            if layer < depth - 1:
                qc.barrier()

        qc.measure_all()

        # Ising-like Hamiltonian coefficients for a minimal demo
        hamiltonian_coeffs = self._demo_hamiltonian(n)

        return BuiltCircuit(
            circuit=qc,
            algorithm="VQE",
            metadata={
                "n_qubits": n,
                "depth": depth,
                "n_params": len(params),
                "hamiltonian_coeffs": hamiltonian_coeffs,
                "molecule_label": spec.extra.get("label", "unknown molecule"),
            },
        )

    # ------------------------------------------------------------------
    # QAOA
    # ------------------------------------------------------------------

    def _build_qaoa(self, spec: ProblemSpec) -> BuiltCircuit:
        n = spec.n_qubits
        p = spec.extra.get("p_layers", 1)

        # Build a random-weight graph for the Max-Cut problem
        rng = np.random.default_rng(seed=42)
        edges: list[tuple[int, int, float]] = []
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() > 0.4:  # ~60 % edge probability
                    weight = round(float(rng.uniform(0.5, 2.0)), 2)
                    edges.append((i, j, weight))

        gammas = ParameterVector("γ", length=p)
        betas = ParameterVector("β", length=p)

        qc = QuantumCircuit(n)

        # Initial state: uniform superposition
        qc.h(range(n))

        for layer in range(p):
            # Cost unitary
            for (i, j, w) in edges:
                qc.rzz(2 * gammas[layer] * w, i, j)
            # Mixer unitary
            for q in range(n):
                qc.rx(2 * betas[layer], q)
            if layer < p - 1:
                qc.barrier()

        qc.measure_all()

        return BuiltCircuit(
            circuit=qc,
            algorithm="QAOA",
            metadata={
                "n_qubits": n,
                "p_layers": p,
                "edges": edges,
                "n_nodes": n,
            },
        )

    # ------------------------------------------------------------------
    # Grover's algorithm
    # ------------------------------------------------------------------

    def _build_grover(self, spec: ProblemSpec) -> BuiltCircuit:
        n = spec.n_qubits
        iterations = spec.extra.get("grover_iterations", max(1, round(math.pi / 4 * math.sqrt(2 ** n))))

        # For the demo the "target" is the all-ones bitstring |11…1⟩
        target_bits = [1] * n

        qc = QuantumCircuit(n)

        # Initial superposition
        qc.h(range(n))

        for _ in range(iterations):
            # Oracle: marks |11…1⟩ with a phase flip
            qc.compose(self._phase_oracle(n, target_bits), inplace=True)
            # Diffusion operator
            qc.compose(self._diffusion(n), inplace=True)

        qc.measure_all()

        return BuiltCircuit(
            circuit=qc,
            algorithm="Grover",
            metadata={
                "n_qubits": n,
                "iterations": iterations,
                "n_candidates": 2 ** n,
                "target": "".join(str(b) for b in target_bits),
            },
        )

    # ------------------------------------------------------------------
    # Helper sub-circuits
    # ------------------------------------------------------------------

    @staticmethod
    def _phase_oracle(n: int, target: list[int]) -> QuantumCircuit:
        """Multi-controlled-Z oracle that marks *target* with a −1 phase."""
        qc = QuantumCircuit(n, name="Oracle")
        # Flip qubits whose target bit is 0 so the MCZ marks the right state
        for q, bit in enumerate(target):
            if bit == 0:
                qc.x(q)
        # Multi-controlled Z via CX + H trick for general n
        if n == 1:
            qc.z(0)
        else:
            qc.h(n - 1)
            qc.mcx(list(range(n - 1)), n - 1)
            qc.h(n - 1)
        for q, bit in enumerate(target):
            if bit == 0:
                qc.x(q)
        return qc

    @staticmethod
    def _diffusion(n: int) -> QuantumCircuit:
        """Grover diffusion (inversion about the mean) operator."""
        qc = QuantumCircuit(n, name="Diffusion")
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)
        qc.x(range(n))
        qc.h(range(n))
        return qc

    @staticmethod
    def _demo_hamiltonian(n: int) -> list[tuple[str, float]]:
        """
        Return a minimal Ising-type Hamiltonian for *n* qubits.

        The coefficients are chosen so that the ground state energy is
        negative and clearly distinguishable from excited states, giving
        an illustrative VQE optimisation landscape.
        """
        terms: list[tuple[str, float]] = []
        # Local Z terms
        for i in range(n):
            terms.append((f"Z{i}", -1.0))
        # Nearest-neighbour ZZ couplings
        for i in range(n - 1):
            terms.append((f"Z{i}Z{i + 1}", -0.5))
        return terms

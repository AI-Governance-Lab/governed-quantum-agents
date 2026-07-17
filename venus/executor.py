"""
Executor: runs a BuiltCircuit on the Qiskit Aer statevector / shot-based
simulator and returns raw measurement counts together with estimated
expectation values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.optimize import minimize
from qiskit.circuit import ParameterVector
from qiskit_aer import AerSimulator

from venus.circuit_builder import BuiltCircuit


@dataclass
class ExecutionResult:
    """Raw results produced by the quantum executor."""

    algorithm: str
    counts: dict[str, int]
    shots: int
    optimal_params: list[float] | None
    energy: float | None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def most_likely_bitstring(self) -> str:
        """Return the bitstring measured most frequently."""
        if not self.counts:
            return ""
        return max(self.counts, key=lambda k: self.counts[k])

    @property
    def probabilities(self) -> dict[str, float]:
        """Return normalised measurement probabilities."""
        total = sum(self.counts.values()) or 1
        return {k: v / total for k, v in self.counts.items()}


class Executor:
    """
    Executes a :class:`~venus.circuit_builder.BuiltCircuit` on the Qiskit
    Aer simulator.

    For VQE and QAOA the executor uses SciPy's COBYLA optimiser to find
    optimal variational parameters before sampling the final distribution.
    For Grover circuits the parameters are fixed; only shot-based sampling
    is performed.
    """

    def __init__(self, shots: int = 1024) -> None:
        self._shots = shots
        self._sim = AerSimulator()

    def run(self, built: BuiltCircuit) -> ExecutionResult:
        """
        Run *built* and return an :class:`ExecutionResult`.

        Parameters
        ----------
        built:
            Circuit + metadata produced by :class:`CircuitBuilder`.

        Returns
        -------
        ExecutionResult
        """
        if built.algorithm == "VQE":
            return self._run_vqe(built)
        if built.algorithm == "QAOA":
            return self._run_qaoa(built)
        return self._run_grover(built)

    # ------------------------------------------------------------------
    # VQE execution
    # ------------------------------------------------------------------

    def _run_vqe(self, built: BuiltCircuit) -> ExecutionResult:
        n_params = built.metadata["n_params"]
        hamiltonian = built.metadata["hamiltonian_coeffs"]

        # Initial parameter guess
        rng = np.random.default_rng(seed=0)
        x0 = rng.uniform(0, 2 * np.pi, size=n_params)

        def cost(params: np.ndarray) -> float:
            return self._expectation_value(built.circuit, params, hamiltonian, built.metadata["n_qubits"])

        result = minimize(cost, x0, method="COBYLA", options={"maxiter": 200, "rhobeg": 0.5})
        optimal_params = list(result.x)
        energy = float(result.fun)

        counts = self._sample(built.circuit, optimal_params)
        return ExecutionResult(
            algorithm="VQE",
            counts=counts,
            shots=self._shots,
            optimal_params=optimal_params,
            energy=energy,
            metadata=built.metadata,
        )

    # ------------------------------------------------------------------
    # QAOA execution
    # ------------------------------------------------------------------

    def _run_qaoa(self, built: BuiltCircuit) -> ExecutionResult:
        p = built.metadata["p_layers"]
        n_params = 2 * p  # p gammas + p betas

        rng = np.random.default_rng(seed=0)
        x0 = rng.uniform(0, np.pi, size=n_params)

        edges = built.metadata["edges"]

        def cost(params: np.ndarray) -> float:
            counts = self._sample(built.circuit, list(params))
            return -self._maxcut_expectation(counts, edges)

        result = minimize(cost, x0, method="COBYLA", options={"maxiter": 300, "rhobeg": 0.3})
        optimal_params = list(result.x)

        counts = self._sample(built.circuit, optimal_params)
        cut_value = self._maxcut_expectation(counts, edges)

        return ExecutionResult(
            algorithm="QAOA",
            counts=counts,
            shots=self._shots,
            optimal_params=optimal_params,
            energy=-cut_value,
            metadata={**built.metadata, "max_cut_value": cut_value},
        )

    # ------------------------------------------------------------------
    # Grover execution
    # ------------------------------------------------------------------

    def _run_grover(self, built: BuiltCircuit) -> ExecutionResult:
        counts = self._sample(built.circuit, params=None)
        return ExecutionResult(
            algorithm="Grover",
            counts=counts,
            shots=self._shots,
            optimal_params=None,
            energy=None,
            metadata=built.metadata,
        )

    # ------------------------------------------------------------------
    # Simulation helpers
    # ------------------------------------------------------------------

    def _sample(self, circuit: "QuantumCircuit", params: list[float] | None) -> dict[str, int]:
        """Bind *params* to *circuit* (if any) and measure *self._shots* times."""
        if params is not None:
            param_objs = sorted(circuit.parameters, key=lambda p: p.name)
            bound = circuit.assign_parameters(
                {p: v for p, v in zip(param_objs, params)}
            )
        else:
            bound = circuit

        job = self._sim.run(bound, shots=self._shots)
        result = job.result()
        return dict(result.get_counts())

    def _expectation_value(
        self,
        circuit: "QuantumCircuit",
        params: np.ndarray,
        hamiltonian: list[tuple[str, float]],
        n_qubits: int,
    ) -> float:
        """
        Estimate ⟨H⟩ by sampling measurement outcomes for each Pauli term.

        For each Z_i term we read bit i; for Z_iZ_j we read the product of
        bits i and j.  This gives a shot-noise estimate sufficient for the
        VQE optimisation demo.
        """
        counts = self._sample(circuit, list(params))
        total = sum(counts.values())
        exp_val = 0.0

        for (term, coeff) in hamiltonian:
            term_sum = 0.0
            for bitstring, count in counts.items():
                # Qiskit counts use little-endian bit order (rightmost = qubit 0)
                bits = [int(b) for b in reversed(bitstring.replace(" ", ""))]
                # Map 0 → +1, 1 → −1
                paulis = [1 - 2 * b for b in bits]
                if term.startswith("Z") and len(term) == 2:
                    q = int(term[1])
                    val = paulis[q] if q < len(paulis) else 0
                elif len(term) == 4 and term[0] == "Z" and term[2] == "Z":
                    q0, q1 = int(term[1]), int(term[3])
                    val = (paulis[q0] if q0 < len(paulis) else 0) * (
                        paulis[q1] if q1 < len(paulis) else 0
                    )
                else:
                    val = 0.0
                term_sum += val * count
            exp_val += coeff * term_sum / total

        return exp_val

    @staticmethod
    def _maxcut_expectation(
        counts: dict[str, int], edges: list[tuple[int, int, float]]
    ) -> float:
        """Compute the weighted Max-Cut value averaged over measurement outcomes."""
        total = sum(counts.values())
        cut_sum = 0.0
        for bitstring, count in counts.items():
            bits = [int(b) for b in reversed(bitstring.replace(" ", ""))]
            cut = sum(
                w * (bits[i] != bits[j])
                for (i, j, w) in edges
                if i < len(bits) and j < len(bits)
            )
            cut_sum += cut * count
        return cut_sum / total

"""Tests for Executor."""

import pytest

from venus.goal_parser import GoalParser
from venus.circuit_builder import CircuitBuilder
from venus.executor import Executor, ExecutionResult


@pytest.fixture
def pipeline():
    return GoalParser(), CircuitBuilder(), Executor(shots=256)


class TestExecutorOutputStructure:
    @pytest.mark.parametrize("goal,expected_algo", [
        ("Simulate the H2 molecule ground state energy", "VQE"),
        ("Optimize a synthesis pathway for production", "QAOA"),
        ("Search for the best candidate among 8 options", "Grover"),
    ])
    def test_algorithm_label_matches(self, pipeline, goal, expected_algo):
        parser, builder, executor = pipeline
        spec = parser.parse(goal)
        built = builder.build(spec)
        result = executor.run(built)
        assert result.algorithm == expected_algo

    def test_counts_nonempty(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Find the H2 ground state")
        built = builder.build(spec)
        result = executor.run(built)
        assert len(result.counts) > 0

    def test_counts_sum_to_shots(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Find the H2 ground state")
        built = builder.build(spec)
        result = executor.run(built)
        assert sum(result.counts.values()) == result.shots

    def test_probabilities_sum_to_one(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Search for candidates")
        built = builder.build(spec)
        result = executor.run(built)
        total = sum(result.probabilities.values())
        assert abs(total - 1.0) < 1e-6

    def test_most_likely_bitstring_is_a_key(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Search for the best compound")
        built = builder.build(spec)
        result = executor.run(built)
        assert result.most_likely_bitstring in result.counts


class TestVQEExecution:
    def test_vqe_has_energy(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Simulate the H2 molecule")
        built = builder.build(spec)
        result = executor.run(built)
        assert result.energy is not None
        assert isinstance(result.energy, float)

    def test_vqe_has_optimal_params(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Simulate the H2 molecule")
        built = builder.build(spec)
        result = executor.run(built)
        assert result.optimal_params is not None
        assert len(result.optimal_params) > 0


class TestQAOAExecution:
    def test_qaoa_has_cut_value(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Optimize the synthesis route for production")
        built = builder.build(spec)
        result = executor.run(built)
        assert "max_cut_value" in result.metadata
        assert result.metadata["max_cut_value"] >= 0


class TestGroverExecution:
    def test_grover_no_optimal_params(self, pipeline):
        parser, builder, executor = pipeline
        spec = parser.parse("Search for the best candidate among 8 options")
        built = builder.build(spec)
        result = executor.run(built)
        assert result.optimal_params is None
        assert result.energy is None

    def test_grover_amplifies_target(self, pipeline):
        """The all-ones state should have higher-than-uniform probability."""
        parser, builder, executor = pipeline
        spec = parser.parse("Find novel candidates")
        built = builder.build(spec)
        result = executor.run(built)
        n = built.metadata["n_qubits"]
        target = built.metadata["target"]
        uniform_prob = 1.0 / (2 ** n)
        target_prob = result.probabilities.get(target, 0.0)
        assert target_prob > uniform_prob

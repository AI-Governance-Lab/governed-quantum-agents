"""Tests for CircuitBuilder."""

import pytest
from qiskit.circuit import QuantumCircuit

from venus.goal_parser import GoalParser, ProblemType
from venus.circuit_builder import CircuitBuilder, BuiltCircuit


@pytest.fixture
def builder() -> CircuitBuilder:
    return CircuitBuilder()


@pytest.fixture
def parser() -> GoalParser:
    return GoalParser()


class TestVQECircuit:
    def test_builds_for_molecule_spec(self, parser, builder):
        spec = parser.parse("Simulate the H2 molecule ground state")
        built = builder.build(spec)
        assert built.algorithm == "VQE"

    def test_circuit_has_correct_qubit_count(self, parser, builder):
        spec = parser.parse("Simulate the H2 molecule ground state")
        built = builder.build(spec)
        assert built.circuit.num_qubits == 2

    def test_circuit_has_measurements(self, parser, builder):
        spec = parser.parse("Simulate the H2 molecule")
        built = builder.build(spec)
        assert built.circuit.num_clbits > 0

    def test_circuit_has_parameters(self, parser, builder):
        spec = parser.parse("Simulate the H2 molecule")
        built = builder.build(spec)
        assert len(built.circuit.parameters) > 0

    def test_metadata_contains_hamiltonian(self, parser, builder):
        spec = parser.parse("Find the ground state of H2")
        built = builder.build(spec)
        assert "hamiltonian_coeffs" in built.metadata
        assert len(built.metadata["hamiltonian_coeffs"]) > 0

    def test_lih_uses_4_qubits(self, parser, builder):
        spec = parser.parse("Simulate the LiH molecule")
        built = builder.build(spec)
        assert built.circuit.num_qubits == 4


class TestQAOACircuit:
    def test_builds_for_optimization_spec(self, parser, builder):
        spec = parser.parse("Optimize the synthesis pathway for compound X")
        built = builder.build(spec)
        assert built.algorithm == "QAOA"

    def test_circuit_has_parameters(self, parser, builder):
        spec = parser.parse("Find the optimal route for production")
        built = builder.build(spec)
        assert len(built.circuit.parameters) > 0

    def test_metadata_contains_edges(self, parser, builder):
        spec = parser.parse("Optimize a logistics network")
        built = builder.build(spec)
        assert "edges" in built.metadata

    def test_circuit_has_measurements(self, parser, builder):
        spec = parser.parse("Optimize the resource allocation")
        built = builder.build(spec)
        assert built.circuit.num_clbits > 0


class TestGroverCircuit:
    def test_builds_for_search_spec(self, parser, builder):
        spec = parser.parse("Search for the best candidate")
        built = builder.build(spec)
        assert built.algorithm == "Grover"

    def test_circuit_has_measurements(self, parser, builder):
        spec = parser.parse("Search for novel compounds")
        built = builder.build(spec)
        assert built.circuit.num_clbits > 0

    def test_no_free_parameters(self, parser, builder):
        spec = parser.parse("Scan for candidates")
        built = builder.build(spec)
        # Grover circuits have no variational parameters
        assert len(built.circuit.parameters) == 0

    def test_metadata_contains_iterations(self, parser, builder):
        spec = parser.parse("Search for new molecules")
        built = builder.build(spec)
        assert "iterations" in built.metadata
        assert built.metadata["iterations"] >= 1


class TestBuiltCircuitContract:
    @pytest.mark.parametrize("goal", [
        "Simulate the H2 molecule",
        "Optimize a synthesis route",
        "Search for a drug candidate",
    ])
    def test_returns_built_circuit(self, parser, builder, goal):
        spec = parser.parse(goal)
        built = builder.build(spec)
        assert isinstance(built, BuiltCircuit)
        assert isinstance(built.circuit, QuantumCircuit)
        assert built.algorithm in {"VQE", "QAOA", "Grover"}
        assert isinstance(built.metadata, dict)

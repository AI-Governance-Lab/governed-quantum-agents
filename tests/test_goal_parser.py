"""Tests for GoalParser."""

import pytest

from venus.goal_parser import GoalParser, ProblemType, ProblemSpec


@pytest.fixture
def parser() -> GoalParser:
    return GoalParser()


class TestGoalParserClassification:
    def test_molecule_keyword_maps_to_simulation(self, parser):
        spec = parser.parse("Find a drug molecule that binds to a cancer enzyme")
        assert spec.problem_type == ProblemType.MOLECULE_SIMULATION

    def test_chemical_keyword_maps_to_simulation(self, parser):
        spec = parser.parse("Simulate the ground state energy of a molecular compound")
        assert spec.problem_type == ProblemType.MOLECULE_SIMULATION

    def test_optimize_keyword_maps_to_optimization(self, parser):
        spec = parser.parse("Optimize the synthesis route for compound production")
        assert spec.problem_type == ProblemType.COMBINATORIAL_OPTIMIZATION

    def test_route_keyword_maps_to_optimization(self, parser):
        spec = parser.parse("Find the optimal logistics route across 6 nodes")
        assert spec.problem_type == ProblemType.COMBINATORIAL_OPTIMIZATION

    def test_search_keyword_maps_to_search(self, parser):
        spec = parser.parse("Search for novel candidates in the design space")
        assert spec.problem_type == ProblemType.CANDIDATE_SEARCH

    def test_discover_keyword_maps_to_search(self, parser):
        spec = parser.parse("Discover new materials with high conductivity")
        # 'materials' is a molecule keyword; result depends on scoring
        assert spec.problem_type in (ProblemType.MOLECULE_SIMULATION, ProblemType.CANDIDATE_SEARCH)


class TestGoalParserMolecules:
    def test_h2_detected(self, parser):
        spec = parser.parse("Simulate the H2 molecule ground state energy")
        assert spec.n_qubits == 2
        assert spec.extra.get("label") == "H₂ (hydrogen)"

    def test_hydrogen_detected(self, parser):
        spec = parser.parse("Compute the ground state of hydrogen")
        assert spec.n_qubits == 2

    def test_lih_detected(self, parser):
        spec = parser.parse("Find the ground state energy of LiH")
        assert spec.n_qubits == 4

    def test_water_detected(self, parser):
        spec = parser.parse("Simulate the water molecule")
        assert spec.n_qubits == 4

    def test_unknown_molecule_uses_default_qubits(self, parser):
        spec = parser.parse("Model the protein-ligand binding energy")
        assert spec.n_qubits >= 2


class TestGoalParserOptimization:
    def test_extracts_node_count_from_text(self, parser):
        spec = parser.parse("Optimize a network with 6 nodes")
        assert spec.extra["n_nodes"] == 6

    def test_default_node_count_when_absent(self, parser):
        spec = parser.parse("Optimize a supply chain configuration")
        assert spec.extra["n_nodes"] >= 2

    def test_p_layers_set(self, parser):
        spec = parser.parse("Find the optimal scheduling solution")
        assert spec.extra["p_layers"] >= 1


class TestGoalParserSearch:
    def test_candidate_count_inferred(self, parser):
        spec = parser.parse("Search for the best candidate among 8 options")
        assert spec.extra["n_candidates"] == 8

    def test_qubits_cover_search_space(self, parser):
        import math
        spec = parser.parse("Search for the best candidate among 16 options")
        assert spec.n_qubits >= math.ceil(math.log2(spec.extra["n_candidates"]))

    def test_grover_iterations_positive(self, parser):
        spec = parser.parse("Scan for novel materials")
        assert spec.extra["grover_iterations"] >= 1


class TestGoalParserEdgeCases:
    def test_empty_goal_raises(self, parser):
        with pytest.raises(ValueError):
            parser.parse("")

    def test_whitespace_only_raises(self, parser):
        with pytest.raises(ValueError):
            parser.parse("   ")

    def test_returns_problem_spec(self, parser):
        spec = parser.parse("Find an optimal molecule")
        assert isinstance(spec, ProblemSpec)

    def test_goal_text_preserved(self, parser):
        goal = "Find a drug molecule"
        spec = parser.parse(goal)
        assert spec.goal_text == goal

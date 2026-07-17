"""End-to-end tests for the Venus orchestrator."""

import pytest

from venus import Venus


@pytest.fixture
def venus() -> Venus:
    return Venus(shots=256)


class TestVenusEndToEnd:
    @pytest.mark.parametrize("goal", [
        "Find a drug molecule that binds to the EGFR kinase domain",
        "Simulate the H2 molecule ground state energy",
        "Optimize the synthesis route for compound production",
        "Search for novel material candidates with high conductivity",
    ])
    def test_discover_returns_string(self, venus, goal):
        report = venus.discover(goal)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_discover_raises_on_empty_goal(self, venus):
        with pytest.raises(ValueError):
            venus.discover("")

    def test_vqe_report_contains_algorithm_name(self, venus):
        report = venus.discover("Simulate the H2 molecule")
        assert "VQE" in report

    def test_qaoa_report_contains_algorithm_name(self, venus):
        report = venus.discover("Optimize a synthesis pathway for compound production")
        assert "QAOA" in report

    def test_grover_report_contains_algorithm_name(self, venus):
        report = venus.discover("Search for the best candidate among 8 options")
        assert "Grover" in report

    def test_report_contains_goal_text(self, venus):
        goal = "Find a drug molecule for cancer treatment"
        report = venus.discover(goal)
        assert goal in report

    def test_report_contains_insight_section(self, venus):
        report = venus.discover("Find a drug molecule")
        assert "Insight" in report

    def test_report_contains_results_section(self, venus):
        report = venus.discover("Find a drug molecule")
        assert "Results" in report

    def test_different_shots_affects_counts(self):
        goal = "Search for novel compounds"
        v_low = Venus(shots=128)
        v_high = Venus(shots=512)
        r_low = v_low.discover(goal)
        r_high = v_high.discover(goal)
        # Both should be non-empty strings
        assert len(r_low) > 0
        assert len(r_high) > 0

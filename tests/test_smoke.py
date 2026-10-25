"""Smoke tests to verify the Python environment and package structure."""

import importlib
import sys
import pytest


def test_python_version():
    """Ensure we are running on Python 3.9+."""
    assert sys.version_info >= (3, 9), (
        f"Expected Python 3.9+, got {sys.version_info}"
    )


def test_src_packages_importable():
    """Verify that the top-level src packages can be imported without errors."""
    packages = [
        "agents",
        "bridge",
        "interface",
        "memory",
        "quantum",
        "api",
        "main",
    ]
    for package in packages:
        importlib.import_module(package)


@pytest.mark.asyncio
async def test_end_to_end_api_and_ui():
    """Verify FastAPI React UI, health, memory, and solve endpoints."""
    import os
    os.environ["GQA_OFFLINE_MODE"] = "1"
    from api import serve_react_ui, health_check, get_algorithms, get_memory, solve, chat_with_results, ProblemRequest, ChatRequest

    ui_resp = await serve_react_ui()
    assert ui_resp.status_code == 200

    h_resp = await health_check()
    assert h_resp["status"] == "ok"

    alg_resp = await get_algorithms()
    assert len(alg_resp["supported_algorithms"]) == 4

    mem_resp = await get_memory(limit=5)
    assert "records" in mem_resp

    solve_resp = await solve(ProblemRequest(
        problem_description="Find the ground state energy and molecular configuration of a Metal-Organic Framework for efficient CO2 capture.",
        framework="qiskit",
        shots=512,
        noise_level=0.02
    ))
    assert solve_resp["selected_algorithm"] == "VQE"
    assert solve_resp["execution_summary"]["success"] is True
    assert solve_resp["governance_audit"]["approved"] is True

    chat_resp = await chat_with_results(ChatRequest(
        question="Explain these quantum results in simple business terms",
        context=solve_resp
    ))
    assert "answer" in chat_resp
    assert len(chat_resp["answer"]) > 20



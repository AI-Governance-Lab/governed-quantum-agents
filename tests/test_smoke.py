"""Smoke tests to verify the Python environment and package structure."""

import importlib
import sys


def test_python_version():
    """Ensure we are running on Python 3.11+."""
    assert sys.version_info >= (3, 11), (
        f"Expected Python 3.11+, got {sys.version_info}"
    )


def test_src_packages_importable():
    """Verify that the top-level src packages can be imported without errors."""
    packages = [
        "agents",
        "bridge",
        "interface",
        "memory",
        "quantum",
    ]
    for package in packages:
        mod = importlib.import_module(package)
        assert mod is not None, f"Failed to import package: {package}"

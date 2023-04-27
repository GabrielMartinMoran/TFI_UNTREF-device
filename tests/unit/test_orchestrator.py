"""
import pytest

from src.orchestrator import Orchestrator


@pytest.fixture
def orchestrator(*args) -> Orchestrator:
    orchestrator = Orchestrator()
    return orchestrator
"""

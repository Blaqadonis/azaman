import pytest
from src.state import State
from project_config import PROJECT_CONFIG
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

@pytest.fixture
def mock_project_config():
    """Fixture to provide a mock PROJECT_CONFIG dictionary."""
    return {
        "currency_default": "NGN",
        "state_defaults": {
            "username": "",
            "income": 0.0,
            "budget_for_expenses": 0.0,
            "expense": 0.0,
            "expenses": [],
            "savings_goal": 0.0,
            "savings": 0.0,
            "currency": "",
            "summary": ""
        },
        "state_variables": {
            "username": str,
            "income": float,
            "budget_for_expenses": float,
            "expense": float,
            "expenses": list,
            "savings_goal": float,
            "savings": float,
            "currency": str,
            "summary": str
        },
        "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
        "provider": "groq",
        "tools": ["set_username", "budget", "log_expenses", "math_tool"],
        "project_name": "Aza Man"
    }

@pytest.fixture
def mock_state():
    """Fixture for a default State object."""
    return State(
        username="",
        income=0.0,
        budget_for_expenses=0.0,
        expense=0.0,
        expenses=[],
        savings_goal=0.0,
        savings=0.0,
        currency="NGN",
        summary=""
    )

@pytest.fixture
def mock_sqlite_saver(tmp_path):
    """Fixture for an in-memory SQLite saver."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    yield SqliteSaver(conn)
    conn.close()
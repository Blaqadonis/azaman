"""Pytest fixtures for the Aza Man application test suite.

This module defines shared fixtures used across the test suite to provide mocked
configurations, state objects, and in-memory SQLite checkpointers. The fixtures
isolate dependencies and ensure consistent test environments for testing the
application's state management, tools, and graph workflows.

Dependencies:
    - pytest==8.4.1
    - src.state (State class)
    - project_config (PROJECT_CONFIG constant)
    - langgraph-checkpoint-sqlite==2.0.10 (SqliteSaver)
    - sqlite3 (standard library)

The fixtures are designed for production-grade testing, providing reusable setups
for project configuration, state initialization, and checkpoint persistence, with
proper cleanup to avoid resource leaks.
"""

import pytest
from src.state import State
from project_config import PROJECT_CONFIG
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


@pytest.fixture
def mock_project_config():
    """Fixture to provide a mock PROJECT_CONFIG dictionary.

    Returns a dictionary mimicking the PROJECT_CONFIG structure, defining default
    state values, type specifications, model, provider, tools, and project name
    for consistent test setup.

    Returns:
        dict: Mocked project configuration dictionary.

    Scope:
        function: Creates a new configuration for each test function to ensure
            isolation.
    """
    # Define mock project configuration with default values and settings
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
    """Fixture for a default State object.

    Returns a State instance initialized with default values, suitable for testing
    scenarios requiring an empty or baseline application state.

    Returns:
        State: Default State object with empty or zeroed fields.

    Scope:
        function: Creates a new State instance for each test function to ensure
            isolation.
    """
    # Initialize and return a default State object
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
    """Fixture for an in-memory SQLite saver.

    Creates an in-memory SQLite database for the SqliteSaver checkpointer used in
    LangGraph workflows, ensuring tests do not persist data to disk. The
    connection is closed after each test to prevent resource leaks.

    Args:
        tmp_path: Pytest fixture providing a temporary directory path (unused
            here, but required for fixture compatibility).

    Yields:
        SqliteSaver: In-memory SQLite checkpointer.

    Scope:
        function: Creates a new in-memory database for each test function to
            ensure isolation and prevent state leakage.
    """
    # Create an in-memory SQLite connection
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    # Yield the SqliteSaver instance
    yield SqliteSaver(conn)
    # Close the connection to clean up resources
    conn.close()
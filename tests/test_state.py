"""Unit tests for the State class in the Aza Man application.

This module contains tests for the `State` class defined in `src/state.py`, which
manages the application state for user data, financial metrics, and conversation
summaries. The tests validate default initialization, custom value initialization,
and type enforcement in the `__post_init__` method. It uses pytest and a mocked
project configuration to isolate dependencies.

Dependencies:
    - pytest==8.4.1
    - src.state (State class)
    - project_config (PROJECT_CONFIG constant)

The tests ensure robust state management in a production environment, covering
default values, custom values, and type safety for financial and user data.
"""

import pytest
from src.state import State
from project_config import PROJECT_CONFIG


def test_state_initialization(mock_project_config):
    """Test State initializes with defaults.

    Verifies that a State instance initialized without arguments sets all fields
    to their default values as defined in the class.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If any state field does not match its expected default
            value.
    """
    # Initialize State with default values
    state = State()
    # Verify default values for all fields
    assert state.username == ""
    assert state.income == 0.0
    assert state.budget_for_expenses == 0.0
    assert state.expense == 0.0
    assert state.expenses == []
    assert state.savings_goal == 0.0
    assert state.savings == 0.0
    assert state.currency == ""
    assert state.summary == ""


def test_state_custom_values(mock_project_config):
    """Test State with custom values.

    Verifies that a State instance initialized with custom values correctly sets
    all fields, including financial data, expenses, and user information.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If any state field does not match the provided custom
            value.
    """
    # Initialize State with custom values
    state = State(
        username="testuser",
        income=10000.0,
        budget_for_expenses=8000.0,
        expense=2000.0,
        expenses=[{"amount": 1000.0, "category": "Food"}],
        savings_goal=3000.0,
        savings=2000.0,
        currency="NGN",
        summary="Test summary"
    )
    # Verify all fields match the provided values
    assert state.username == "testuser"
    assert state.income == 10000.0
    assert state.budget_for_expenses == 8000.0
    assert state.expense == 2000.0
    assert state.expenses == [{"amount": 1000.0, "category": "Food"}]
    assert state.savings_goal == 3000.0
    assert state.savings == 2000.0
    assert state.currency == "NGN"
    assert state.summary == "Test summary"


def test_state_post_init_type_enforcement(mock_project_config):
    """Test __post_init__ enforces correct types.

    Verifies that the __post_init__ method coerces invalid input types to their
    default values to ensure type safety in the State instance.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If type coercion does not produce the expected default
            values.
    """
    # Initialize State with invalid types
    state = State(
        username=123,  # Wrong type (int instead of str)
        income="invalid",  # Wrong type (str instead of float)
        expenses="not a list"  # Wrong type (str instead of list)
    )
    # Verify type coercion to default values
    assert state.username == ""
    assert state.income == 0.0
    assert state.expenses == []
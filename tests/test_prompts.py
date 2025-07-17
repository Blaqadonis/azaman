"""Unit tests for system prompt functionality in the Aza Man application.

This module contains tests for the `SYSTEM_PROMPT` defined in `src/prompts.py`
and its formatting logic in `src/configuration.py`. The tests validate that the
system prompt is correctly formatted with state data (username, income, currency,
expenses) and includes instructions for required tools (set_username, budget,
log_expenses, math_tool). It uses pytest, src.configuration.Configuration, and
src.state.State to simulate state data and verify prompt content.

Dependencies:
    - pytest==8.4.1
    - src.configuration (Configuration class)
    - src.state (State class)
    - src.prompts (SYSTEM_PROMPT constant)

The tests ensure robust prompt handling in a production environment, covering
prompt formatting and tool instruction inclusion.
"""

import pytest
from src.configuration import Configuration
from src.state import State
from src.prompts import SYSTEM_PROMPT


def test_system_prompt_formatting():
    """Test SYSTEM_PROMPT formatting with state values.

    Verifies that the system prompt is correctly formatted using state data,
    including username, income, and currency, when processed by the Configuration
    class.

    Raises:
        AssertionError: If the formatted prompt does not contain expected values.
    """
    # Initialize Configuration instance
    config = Configuration()
    # Create a State instance with test data
    state = State(
        username="Chinonso",
        income=500000.0,
        currency="NGN",
        expenses=[{"amount": 10000, "category": "Food"}]
    )
    # Format the system prompt using the state
    formatted_prompt = config.format_system_prompt(state)
    # Verify the prompt includes the username
    assert "Username: Chinonso" in formatted_prompt
    # Verify the prompt includes the formatted income
    assert "Income: 500000.00 NGN" in formatted_prompt
    # Verify the prompt includes the currency
    assert "Currency: NGN" in formatted_prompt


def test_system_prompt_tool_instructions():
    """Test SYSTEM_PROMPT includes tool instructions.

    Verifies that the SYSTEM_PROMPT constant contains instructions for the
    required tools: set_username, budget, log_expenses, and math_tool.

    Raises:
        AssertionError: If any required tool instruction is missing from the
            prompt.
    """
    # Verify the SYSTEM_PROMPT includes the set_username tool
    assert "set_username" in SYSTEM_PROMPT
    # Verify the SYSTEM_PROMPT includes the budget tool
    assert "budget" in SYSTEM_PROMPT
    # Verify the SYSTEM_PROMPT includes the log_expenses tool
    assert "log_expenses" in SYSTEM_PROMPT
    # Verify the SYSTEM_PROMPT includes the math_tool
    assert "math_tool" in SYSTEM_PROMPT
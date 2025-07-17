"""Unit tests for the tool functions in the Aza Man application.

This module contains tests for the tool functions defined in `src/tools.py`, which
are used in the LangGraph workflow to manage budgets, expenses, mathematical
operations, and user settings. The tests validate budget creation, expense logging,
math operations, and username setting, including error handling for invalid inputs.
It uses pytest and a mocked project configuration to isolate dependencies.

Dependencies:
    - pytest==8.4.1
    - src.tools (budget, log_expenses, math_tool, set_username functions)
    - project_config (PROJECT_CONFIG constant)

The tests ensure robust tool functionality in a production environment, covering
budget calculations, expense tracking, mathematical operations, and user
configuration with appropriate error handling.
"""

import pytest
from src.tools import budget, log_expenses, math_tool, set_username


def test_budget_fixed_goal(mock_project_config):
    """Test budget tool with a fixed savings goal.

    Verifies that the budget tool correctly processes a fixed savings goal,
    calculating the budget for expenses and returning a formatted confirmation
    message.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If the budget output does not match expected values.
    """
    # Invoke budget tool with a fixed savings goal
    result = budget.invoke({"income": 10000.0, "savings_goal": 2000.0, "currency": "NGN"})
    # Verify the output dictionary contains expected values
    assert result == {
        "income": 10000.0,
        "savings": 2000.0,
        "budget_for_expenses": 8000.0,
        "currency": "NGN",
        "message": "Budget created! Income: 10,000.00 NGN, Savings: 2,000.00 NGN, Expenses: 8,000.00 NGN"
    }


def test_budget_percentage_goal(mock_project_config):
    """Test budget tool with a percentage savings goal.

    Verifies that the budget tool correctly processes a percentage-based savings
    goal, calculating savings and budget for expenses, and returning a formatted
    confirmation message.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If the budget output does not match expected values.
    """
    # Invoke budget tool with a percentage savings goal
    result = budget.invoke({"income": 10000.0, "savings_goal": "40%", "currency": "NGN"})
    # Verify the output dictionary contains expected values
    assert result == {
        "income": 10000.0,
        "savings": 4000.0,
        "budget_for_expenses": 6000.0,
        "currency": "NGN",
        "message": "Budget created! Income: 10,000.00 NGN, Savings: 4,000.00 NGN, Expenses: 6,000.00 NGN"
    }


def test_log_expenses(mock_project_config):
    """Test log_expenses tool with a list of expenses.

    Verifies that the log_expenses tool correctly processes a list of expenses,
    calculates the total, and returns a formatted confirmation message.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If the expenses output does not match expected values.
    """
    # Define test expenses
    expenses = [{"amount": 500.0, "category": "Food"}, {"amount": 300.0, "category": "Transport"}]
    # Invoke log_expenses tool
    result = log_expenses.invoke({"expenses": expenses, "currency": "NGN"})
    # Verify the output dictionary contains expected values
    assert result == {
        "expense": 800.0,
        "expenses": expenses,
        "currency": "NGN",
        "message": "Expenses logged! Total: 800.00 NGN"
    }


def test_math_tool_add():
    """Test math_tool with addition.

    Verifies that the math_tool correctly performs addition on a list of numbers.

    Raises:
        AssertionError: If the addition result is incorrect.
    """
    # Invoke math_tool with addition operation
    result = math_tool.invoke({"numbers": [1.0, 2.0, 3.0], "operation": "add"})
    # Verify the result
    assert result == 6.0


def test_math_tool_subtract():
    """Test math_tool with subtraction.

    Verifies that the math_tool correctly performs subtraction on a list of numbers.

    Raises:
        AssertionError: If the subtraction result is incorrect.
    """
    # Invoke math_tool with subtraction operation
    result = math_tool.invoke({"numbers": [10.0, 3.0, 2.0], "operation": "subtract"})
    # Verify the result
    assert result == 5.0


def test_math_tool_multiply():
    """Test math_tool with multiplication.

    Verifies that the math_tool correctly performs multiplication on a list of numbers.

    Raises:
        AssertionError: If the multiplication result is incorrect.
    """
    # Invoke math_tool with multiplication operation
    result = math_tool.invoke({"numbers": [2.0, 3.0, 4.0], "operation": "multiply"})
    # Verify the result
    assert result == 24.0


def test_math_tool_divide():
    """Test math_tool with division.

    Verifies that the math_tool correctly performs division on a list of numbers.

    Raises:
        AssertionError: If the division result is incorrect.
    """
    # Invoke math_tool with division operation
    result = math_tool.invoke({"numbers": [100.0, 2.0, 5.0], "operation": "divide"})
    # Verify the result
    assert result == 10.0


def test_math_tool_divide_by_zero():
    """Test math_tool division by zero raises ValueError.

    Verifies that the math_tool raises a ValueError when attempting to divide by zero.

    Raises:
        AssertionError: If the ValueError is not raised or has an incorrect message.
    """
    # Expect a ValueError for division by zero
    with pytest.raises(ValueError, match="Division by zero."):
        math_tool.invoke({"numbers": [100.0, 0.0], "operation": "divide"})


def test_math_tool_empty_list():
    """Test math_tool with empty list raises ValueError.

    Verifies that the math_tool raises a ValueError when given an empty list of numbers.

    Raises:
        AssertionError: If the ValueError is not raised or has an incorrect message.
    """
    # Expect a ValueError for an empty number list
    with pytest.raises(ValueError, match="At least one number required."):
        math_tool.invoke({"numbers": [], "operation": "add"})


def test_math_tool_invalid_operation():
    """Test math_tool with invalid operation raises ValueError.

    Verifies that the math_tool raises a ValueError when given an unsupported operation.

    Raises:
        AssertionError: If the ValueError is not raised or has an incorrect message.
    """
    # Expect a ValueError for an invalid operation
    with pytest.raises(ValueError, match="Unsupported operation: invalid."):
        math_tool.invoke({"numbers": [1.0, 2.0], "operation": "invalid"})


def test_set_username():
    """Test set_username tool.

    Verifies that the set_username tool correctly sets the username and returns a
    confirmation message.

    Raises:
        AssertionError: If the output does not match expected values.
    """
    # Invoke set_username tool
    result = set_username.invoke({"username": "testuser"})
    # Verify the output dictionary contains expected values
    assert result == {"username": "testuser", "message": "Username set to testuser"}
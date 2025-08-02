import pytest
from src.tools import budget, log_expenses, math_tool, set_username

def test_budget_negative_income(mock_project_config):
    with pytest.raises(ValueError, match="Income must be positive."):
        budget.invoke({"income": -1000.0, "savings_goal": 200.0, "currency": "NGN"})

def test_budget_invalid_percentage(mock_project_config):
    with pytest.raises(ValueError, match="Invalid savings goal percentage."):
        budget.invoke({"income": 10000.0, "savings_goal": "invalid%", "currency": "NGN"})

def test_budget_fixed_goal(mock_project_config):
    result = budget.invoke({"income": 10000.0, "savings_goal": 2000.0, "currency": "NGN"})
    assert result == {
        "income": 10000.0,
        "savings": 2000.0,
        "budget_for_expenses": 8000.0,
        "currency": "NGN",
        "message": "Budget created! Income: 10,000.00 NGN, Savings: 2,000.00 NGN, Expenses: 8,000.00 NGN"
    }

def test_budget_percentage_goal(mock_project_config):
    result = budget.invoke({"income": 10000.0, "savings_goal": "40%", "currency": "NGN"})
    assert result == {
        "income": 10000.0,
        "savings": 4000.0,
        "budget_for_expenses": 6000.0,
        "currency": "NGN",
        "message": "Budget created! Income: 10,000.00 NGN, Savings: 4,000.00 NGN, Expenses: 6,000.00 NGN"
    }

def test_log_expenses_empty_list(mock_project_config):
    with pytest.raises(ValueError, match="At least one expense must be provided."):
        log_expenses.invoke({"expenses": [], "currency": "NGN"})

def test_log_expenses_negative_amount(mock_project_config):
    with pytest.raises(ValueError, match="Expense amount must be a positive number."):
        log_expenses.invoke({"expenses": [{"amount": -100.0, "category": "Food"}], "currency": "NGN"})

def test_log_expenses(mock_project_config):
    expenses = [{"amount": 500.0, "category": "Food"}, {"amount": 300.0, "category": "Transport"}]
    result = log_expenses.invoke({"expenses": expenses, "currency": "NGN"})
    assert result == {
        "expense": 800.0,
        "expenses": expenses,
        "currency": "NGN",
        "message": "Expenses logged! Total: 800.00 NGN"
    }

def test_math_tool_add():
    result = math_tool.invoke({"numbers": [1.0, 2.0, 3.0], "operation": "add"})
    assert result == 6.0

def test_math_tool_subtract():
    result = math_tool.invoke({"numbers": [10.0, 3.0, 2.0], "operation": "subtract"})
    assert result == 5.0

def test_math_tool_multiply():
    result = math_tool.invoke({"numbers": [2.0, 3.0, 4.0], "operation": "multiply"})
    assert result == 24.0

def test_math_tool_divide():
    result = math_tool.invoke({"numbers": [100.0, 2.0, 5.0], "operation": "divide"})
    assert result == 10.0

def test_math_tool_divide_by_zero():
    with pytest.raises(ValueError, match="Division by zero."):
        math_tool.invoke({"numbers": [100.0, 0.0], "operation": "divide"})

def test_math_tool_insufficient_numbers():
    with pytest.raises(ValueError, match="Subtract requires at least two numbers."):
        math_tool.invoke({"numbers": [10.0], "operation": "subtract"})

def test_set_username_empty():
    with pytest.raises(ValueError, match="Username cannot be empty."):
        set_username.invoke({"username": ""})

def test_set_username():
    result = set_username.invoke({"username": "testuser"})
    assert result == {"username": "testuser", "message": "Username set to testuser"}
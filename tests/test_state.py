import pytest
from src.state import State
from project_config import PROJECT_CONFIG

def test_state_initialization(mock_project_config):
    state = State()
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
    state = State(username=123, income="invalid", expenses="not a list")
    assert state.username == ""
    assert state.income == 0.0
    assert state.expenses == []
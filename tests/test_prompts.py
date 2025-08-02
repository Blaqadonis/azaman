import pytest
from src.configuration import Configuration
from src.state import State
from src.prompts import SYSTEM_PROMPT

def test_system_prompt_formatting():
    config = Configuration()
    state = State(username="Chinonso", income=500000.0, currency="NGN", expenses=[{"amount": 10000, "category": "Food"}])
    formatted_prompt = config.format_system_prompt(state)
    assert "Username: Chinonso" in formatted_prompt
    assert "Income: 500000.00 NGN" in formatted_prompt
    assert "Currency: NGN" in formatted_prompt

def test_system_prompt_tool_instructions():
    assert "set_username" in SYSTEM_PROMPT
    assert "budget" in SYSTEM_PROMPT
    assert "log_expenses" in SYSTEM_PROMPT
    assert "math_tool" in SYSTEM_PROMPT
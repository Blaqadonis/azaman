import pytest
from src.configuration import Configuration
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableBinding
from unittest.mock import Mock

def test_get_llm_groq(mocker, mock_project_config):
    mocker.patch("os.environ.get", side_effect=lambda k, d=None: "fake_groq_key" if k == "GROQ_API_KEY" else d)
    mock_llm = Mock(model_name="test-model")
    mocker.patch("langchain_groq.ChatGroq", return_value=mock_llm)
    config = Configuration(provider="groq", model="test-model")
    llm = config.get_llm()
    assert isinstance(llm, RunnableBinding)
    assert llm.bound.model_name == "test-model"

def test_get_llm_invalid_provider(mock_project_config):
    config = Configuration(provider="invalid")
    with pytest.raises(ValueError, match="Unsupported provider: invalid."):
        config.get_llm()

def test_format_system_prompt(mock_project_config, mock_state):
    config = Configuration()
    mock_state.username = "testuser"
    mock_state.income = 10000.0
    mock_state.currency = "NGN"
    prompt = config.format_system_prompt(mock_state)
    assert "Username: testuser" in prompt
    assert "Income: 10000.00 NGN" in prompt
    assert "Currency: NGN" in prompt

def test_format_system_prompt_missing_values(mock_project_config, mock_state):
    config = Configuration(system_prompt="{missing_key}")
    prompt = config.format_system_prompt(mock_state)
    assert prompt == "{missing_key}"

def test_from_runnable_config(mocker, mock_project_config):
    mocker.patch("os.environ.get", side_effect=lambda x, d: d)
    config = {"configurable": {"user_id": "testuser", "thread_id": "testthread", "model": "custom-model", "provider": "groq"}}
    cfg = Configuration.from_runnable_config(config)
    assert cfg.user_id == "testuser"
    assert cfg.thread_id == "testthread"
    assert cfg.model == "custom-model"
    assert cfg.provider == "groq"
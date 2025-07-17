"""Unit tests for the Configuration class in the Aza Man application.

This module contains tests for the `Configuration` class defined in
`src/configuration.py`, which manages settings for language model (LLM)
initialization and system prompt formatting. The tests validate LLM provider
handling, system prompt generation, and configuration initialization from
runnable configs. It uses pytest and unittest.mock to simulate dependencies
and test edge cases.

Dependencies:
    - pytest==8.4.1
    - pytest-mock==3.14.1
    - langchain-groq==0.3.2
    - langchain-core==0.3.68
    - src.configuration (Configuration class)

The tests are designed to ensure robust configuration handling in a production
environment, covering valid and invalid LLM providers, prompt formatting, and
configuration precedence.
"""

import pytest
from src.configuration import Configuration
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableBinding
from unittest.mock import Mock


def test_get_llm_groq(mocker, mock_project_config):
    """Test get_llm with the Groq provider.

    Simulates initializing an LLM with the Groq provider using a mocked API key
    and verifies that the returned LLM is a RunnableBinding with the correct
    model name.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If the returned LLM is not a RunnableBinding or the
            model name is incorrect.
    """
    # Mock the GROQ_API_KEY environment variable
    mocker.patch("os.environ.get", side_effect=lambda k, d=None: "fake_groq_key" if k == "GROQ_API_KEY" else d)
    # Mock the ChatGroq class to return a mock LLM
    mock_llm = Mock(model_name="test-model")
    mocker.patch("langchain_groq.ChatGroq", return_value=mock_llm)
    # Initialize Configuration with Groq provider and test model
    config = Configuration(provider="groq", model="test-model")
    # Get the LLM instance
    llm = config.get_llm()
    # Verify the LLM is a RunnableBinding
    assert isinstance(llm, RunnableBinding)
    # Verify the model name in the bound LLM
    assert llm.bound.model_name == "test-model"


def test_get_llm_invalid_provider(mock_project_config):
    """Test get_llm with an invalid provider raises ValueError.

    Verifies that attempting to initialize an LLM with an unsupported provider
    raises a ValueError with the expected error message.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If the ValueError is not raised or has an incorrect
            message.
    """
    # Initialize Configuration with an invalid provider
    config = Configuration(provider="invalid")
    # Expect a ValueError for the unsupported provider
    with pytest.raises(ValueError, match="Unsupported provider: invalid."):
        config.get_llm()


def test_format_system_prompt(mock_project_config, mock_state):
    """Test format_system_prompt with valid state values.

    Verifies that the system prompt is correctly formatted using state data,
    including username, income, and currency.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.
        mock_state: Fixture providing a mocked state object with test data.

    Raises:
        AssertionError: If the formatted prompt does not contain expected values.
    """
    # Initialize Configuration with default settings
    config = Configuration()
    # Set mock state values
    mock_state.username = "testuser"
    mock_state.income = 10000.0
    mock_state.currency = "NGN"
    # Format the system prompt using the mock state
    prompt = config.format_system_prompt(mock_state)
    # Verify the prompt includes the username
    assert "Username: testuser" in prompt
    # Verify the prompt includes the formatted income
    assert "Income: 10000.00 NGN" in prompt
    # Verify the prompt includes the currency
    assert "Currency: NGN" in prompt


def test_format_system_prompt_missing_values(mock_project_config, mock_state):
    """Test format_system_prompt with missing state values.

    Verifies that the system prompt falls back to the unformatted prompt string
    when state data contains missing or invalid keys.

    Args:
        mock_project_config: Fixture providing a mocked project configuration.
        mock_state: Fixture providing a mocked state object.

    Raises:
        AssertionError: If the prompt does not fall back to the unformatted
            string.
    """
    # Initialize Configuration with a prompt containing an invalid key
    config = Configuration(system_prompt="{missing_key}")
    # Format the system prompt with the mock state
    prompt = config.format_system_prompt(mock_state)
    # Verify the prompt falls back to the unformatted string
    assert prompt == "{missing_key}"  # Expect fallback to unformatted prompt


def test_from_runnable_config(mocker, mock_project_config):
    """Test from_runnable_config prioritizes config values.

    Verifies that creating a Configuration instance from a runnable config
    correctly sets attributes based on the provided config dictionary.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_project_config: Fixture providing a mocked project configuration.

    Raises:
        AssertionError: If the Configuration attributes do not match the expected
            values from the config.
    """
    # Mock os.environ.get to return None, ensuring config values take precedence
    mocker.patch("os.environ.get", side_effect=lambda x, d: d)
    # Define a test runnable config
    config = {"configurable": {"user_id": "testuser", "thread_id": "testthread", "model": "custom-model", "provider": "groq"}}
    # Create Configuration from the runnable config
    cfg = Configuration.from_runnable_config(config)
    # Verify Configuration attributes
    assert cfg.user_id == "testuser"
    assert cfg.thread_id == "testthread"
    assert cfg.model == "custom-model"
    assert cfg.provider == "groq"
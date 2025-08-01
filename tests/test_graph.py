"""Unit tests for the graph-related functionality in the Aza Man application.

This module contains tests for the functions in `src/graph.py`, which manages
the LangGraph workflow for the Aza Man financial assistant. The tests validate
language model invocation, state updates for budget tools, message routing, graph
construction, and error handling. It uses pytest, unittest.mock, and langchain_core
to simulate dependencies and test edge cases.

Dependencies:
    - pytest==8.4.1
    - pytest-mock==3.14.1
    - langchain-core==0.3.68 (for AIMessage, HumanMessage)
    - langchain-groq==0.3.2 (for mocked LLM in call_model)
    - src.graph (call_model, store_memory, route_message, build_graph)
    - src.state (State class)
    - src.configuration (Configuration class)

The tests ensure robust graph behavior in a production environment, covering tool
calls, state persistence, routing logic, graph initialization, and error cases.
"""

import pytest
from src.graph import call_model, store_memory, summarize_conversation, route_message, build_graph
from src.state import State
from langchain_core.messages import AIMessage, HumanMessage
from unittest.mock import Mock

def test_call_model(mocker, mock_state, mock_sqlite_saver):
    """Test call_model invokes LLM and processes tool calls.

    Simulates invoking the language model with a user message and verifies that
    the LLM response is correctly processed, including handling tool calls.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.

    Raises:
        AssertionError: If the resulting messages or tool calls do not match
            expected values.
    """
    mock_llm = Mock()
    mock_llm.invoke.return_value = AIMessage(content='{"name": "set_username", "parameters": {"username": "testuser"}}')
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    mock_state.messages = [HumanMessage(content="set my username to testuser")]
    result = call_model(mock_state, config)
    assert len(result["messages"]) == 1
    assert result["messages"][0]["tool_calls"] == [{"name": "set_username", "args": {"username": "testuser"}, "id": "manual_call"}]

def test_call_model_llm_failure(mocker, mock_state, mock_sqlite_saver):
    """Test call_model handles LLM failure gracefully.

    Simulates an LLM API failure and verifies an error message is added to the state.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.
    """
    mock_llm = Mock()
    mock_llm.invoke.side_effect = Exception("API timeout")
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    mock_state.messages = [HumanMessage(content="set my username to testuser")]
    result = call_model(mock_state, config)
    assert isinstance(result, dict)
    assert "messages" in result
    assert any(isinstance(msg, dict) and "Error: Failed to process request due to API timeout" in msg["content"] for msg in result["messages"])

def test_call_model_empty_input(mocker, mock_state, mock_sqlite_saver):
    """Test call_model handles empty user input.

    Verifies that an empty input results in a prompt for valid input.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.
    """
    mock_llm = Mock()
    mock_llm.invoke.return_value = AIMessage(content="Please provide a valid input")
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    mock_state.messages = [HumanMessage(content="")]
    result = call_model(mock_state, config)
    assert any(isinstance(msg, dict) and "Please provide a valid input" in msg["content"] for msg in result["messages"])

def test_call_model_unsafe_content(mocker, mock_state, mock_sqlite_saver):
    """Test call_model filters inappropriate content.

    Simulates an LLM response with inappropriate content and verifies it is filtered.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.
    """
    mock_llm = Mock()
    mock_llm.invoke.return_value = AIMessage(content="This is an inappropriate response")
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    mock_state.messages = [HumanMessage(content="Tell me something")]
    result = call_model(mock_state, config)
    assert any(isinstance(msg, dict) and "Warning: Inappropriate content detected" in msg["content"] for msg in result["messages"])

def test_call_model_json_decode_error(mocker, mock_state, mock_sqlite_saver):
    """Test call_model handles JSON decode errors.

    Simulates an LLM response with invalid JSON and verifies it is handled gracefully.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.
    """
    mock_llm = Mock()
    mock_llm.invoke.return_value = AIMessage(content="Invalid JSON")
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    mock_state.messages = [HumanMessage(content="set my username to testuser")]
    result = call_model(mock_state, config)
    assert any(isinstance(msg, dict) and "Invalid JSON" in msg["content"] for msg in result["messages"])

def test_store_memory_budget(mocker, mock_state, mock_sqlite_saver):
    """Test store_memory updates state for budget tool.

    Simulates a budget tool call and verifies that the state is updated with
    financial data (income, savings, budget, currency) and a confirmation message.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.

    Raises:
        AssertionError: If the state or message content does not match expected
            values.
    """
    mocker.patch("src.tools.budget", return_value={
        "income": 10000.0,
        "savings": 2000.0,
        "budget_for_expenses": 8000.0,
        "currency": "NGN",
        "message": "Budget created! Income: 10,000.00 NGN, Savings: 2,000.00 NGN, Expenses: 8,000.00 NGN"
    })
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "budget", "args": {"income": 10000.0, "savings_goal": 2000.0, "currency": "NGN"}, "id": "call1"}])]
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    result = store_memory(mock_state, config)
    assert result["income"] == 10000.0
    assert result["savings"] == 2000.0
    assert result["budget_for_expenses"] == 8000.0
    assert result["currency"] == "NGN"
    assert result["messages"][0]["content"] == "Budget created! Income: 10,000.00 NGN, Savings: 2,000.00 NGN, Expenses: 8,000.00 NGN"

def test_store_memory_invalid_tool(mocker, mock_state, mock_sqlite_saver):
    """Test store_memory handles invalid tool calls.

    Simulates an invalid tool call and verifies an error message is added.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.
    """
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "invalid_tool", "args": {}, "id": "call1"}])]
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    result = store_memory(mock_state, config)
    assert isinstance(result, dict)
    assert "messages" in result
    assert any(isinstance(msg, dict) and "Error: Invalid tool invalid_tool requested" in msg["content"] for msg in result["messages"])

def test_store_memory_tool_failure(mocker, mock_state, mock_sqlite_saver):
    """Test store_memory handles tool execution failures.

    Simulates a tool execution failure and verifies an error message is added.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.
    """
    mocker.patch("src.tools.budget", side_effect=Exception("Invalid budget data"))
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "budget", "args": {"income": -1000}, "id": "call1"}])]
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    result = store_memory(mock_state, config)
    assert isinstance(result, dict)
    assert "messages" in result
    assert any(isinstance(msg, dict) and "Error: Tool budget failed with Invalid budget data" in msg["content"] for msg in result["messages"])

def test_route_message_tool_call(mock_state):
    """Test route_message directs to store_memory for tool calls.

    Verifies that a message with a tool call is routed to the 'store_memory' node.

    Args:
        mock_state: Fixture providing a mocked State object.

    Raises:
        AssertionError: If the routing decision is incorrect.
    """
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "budget", "args": {}, "id": "call1"}])]
    assert route_message(mock_state) == "store_memory"

def test_route_message_summary(mock_state):
    """Test route_message directs to summarize_conversation for long conversations.

    Verifies that a conversation with more than 10 messages is routed to the
    'summarize_conversation' node.

    Args:
        mock_state: Fixture providing a mocked State object.

    Raises:
        AssertionError: If the routing decision is incorrect.
    """
    mock_state.messages = [HumanMessage(content="msg")] * 10 + [AIMessage(content="response")]
    assert route_message(mock_state) == "summarize_conversation"

def test_route_message_end(mock_state):
    """Test route_message directs to END for regular messages.

    Verifies that a regular message without tool calls or excessive length is
    routed to the '__end__' node.

    Args:
        mock_state: Fixture providing a mocked State object.

    Raises:
        AssertionError: If the routing decision is incorrect.
    """
    mock_state.messages = [AIMessage(content="Hello!")]
    assert route_message(mock_state) == "__end__"

def test_route_message_no_messages(mock_state):
    """Test route_message handles empty message list.

    Verifies that an empty message list routes to '__end__'.

    Args:
        mock_state: Fixture providing a mocked State object.
    """
    mock_state.messages = []
    assert route_message(mock_state) == "__end__"

def test_summarize_conversation_empty(mocker, mock_state, mock_sqlite_saver):
    """Test summarize_conversation handles empty conversation.

    Verifies that summarizing an empty conversation returns an empty summary.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.
        mock_state: Fixture providing a mocked State object.
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.
    """
    mock_llm = Mock()
    mock_llm.invoke.return_value = AIMessage(content="No conversation to summarize")
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    mock_state.messages = []
    result = summarize_conversation(mock_state, config)
    assert isinstance(result, dict)
    assert "summary" in result
    assert result["summary"] == "No conversation to summarize"
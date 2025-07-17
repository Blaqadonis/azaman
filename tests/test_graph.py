"""Unit tests for the graph-related functionality in the Aza Man application.

This module contains tests for the functions in `src/graph.py`, which manages
the LangGraph workflow for the Aza Man financial assistant. The tests validate
language model invocation, state updates for budget tools, message routing, and
graph construction. It uses pytest, unittest.mock, and langchain_core to simulate
dependencies and test edge cases.

Dependencies:
    - pytest==8.4.1
    - pytest-mock==3.14.1
    - langchain-core==0.3.68 (for AIMessage, HumanMessage)
    - langchain-groq==0.3.2 (for mocked LLM in call_model)
    - src.graph (call_model, store_memory, route_message, build_graph)
    - src.state (State class)
    - src.configuration (Configuration class)

The tests ensure robust graph behavior in a production environment, covering tool
calls, state persistence, routing logic, and graph initialization.
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
    # Mock the LLM and its response
    mock_llm = Mock()
    mock_llm.invoke.return_value = AIMessage(content='{"name": "set_username", "parameters": {"username": "testuser"}}')
    # Mock Configuration.get_llm to return the mocked LLM
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    # Set up test configuration
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    # Set mock state with a user message
    mock_state.messages = [HumanMessage(content="set my username to testuser")]
    # Call the function under test
    result = call_model(mock_state, config)
    # Verify a single message is returned
    assert len(result["messages"]) == 1
    # Verify the message contains the expected tool call
    assert result["messages"][0].tool_calls == [{"name": "set_username", "args": {"username": "testuser"}, "id": "manual_call"}]


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
    # Mock the budget tool response
    mocker.patch("src.tools.budget", return_value={
        "income": 10000.0,
        "savings": 2000.0,
        "budget_for_expenses": 8000.0,
        "currency": "NGN",
        "message": "Budget created! Income: 10,000.00 NGN, Savings: 2,000.00 NGN, Expenses: 8,000.00 NGN"
    })
    # Set mock state with a budget tool call
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "budget", "args": {"income": 10000.0, "savings_goal": 2000.0, "currency": "NGN"}, "id": "call1"}])]
    # Set up test configuration
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    # Call the function under test
    result = store_memory(mock_state, config)
    # Verify state updates
    assert result["income"] == 10000.0
    assert result["savings"] == 2000.0
    assert result["budget_for_expenses"] == 8000.0
    assert result["currency"] == "NGN"
    # Verify the confirmation message
    assert result["messages"][0]["content"] == "Budget created! Income: 10,000.00 NGN, Savings: 2,000.00 NGN, Expenses: 8,000.00 NGN"


def test_route_message_tool_call(mock_state):
    """Test route_message directs to store_memory for tool calls.

    Verifies that a message with a tool call is routed to the 'store_memory' node.

    Args:
        mock_state: Fixture providing a mocked State object.

    Raises:
        AssertionError: If the routing decision is incorrect.
    """
    # Set mock state with a tool call message
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "budget", "args": {}, "id": "call1"}])]
    # Verify routing to store_memory
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
    # Set mock state with 11 messages to trigger summary
    mock_state.messages = [HumanMessage(content="msg")] * 10 + [AIMessage(content="response")]
    # Verify routing to summarize_conversation
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
    # Set mock state with a regular message
    mock_state.messages = [AIMessage(content="Hello!")]
    # Verify routing to __end__
    assert route_message(mock_state) == "__end__"


def test_build_graph(mock_sqlite_saver):
    """Test build_graph constructs the graph correctly.

    Verifies that the graph is constructed with the correct name and checkpointer.

    Args:
        mock_sqlite_saver: Fixture providing a mocked SqliteSaver checkpointer.

    Raises:
        AssertionError: If the graph name or checkpointer is incorrect.
    """
    # Build the graph with the mocked checkpointer
    graph = build_graph(mock_sqlite_saver)
    # Verify the graph name
    assert graph.name == "Aza Man"
    # Verify the checkpointer is correctly set
    assert mock_sqlite_saver == graph.checkpointer
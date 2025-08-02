import pytest
from src.graph import call_model, store_memory, summarize_conversation, route_message, build_graph
from src.state import State
from langchain_core.messages import AIMessage, HumanMessage
from unittest.mock import Mock

def test_call_model(mocker, mock_state, mock_sqlite_saver):
    """Test call_model invokes the LLM and processes tool calls correctly."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = AIMessage(content='{"name": "set_username", "parameters": {"username": "testuser"}}')
    mocker.patch("src.configuration.Configuration.get_llm", return_value=mock_llm)
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    mock_state.messages = [HumanMessage(content="set my username to testuser")]
    result = call_model(mock_state, config)
    assert len(result["messages"]) == 1
    assert result["messages"][0].tool_calls == [{"name": "set_username", "args": {"username": "testuser"}, "id": "manual_call"}]

def test_store_memory_budget(mocker, mock_state, mock_sqlite_saver):
    """Test store_memory processes budget tool correctly."""
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

def test_store_memory_tool_error(mocker, mock_state, mock_sqlite_saver):
    """Test store_memory handling of tool execution errors."""
    # Match the Pydantic validation error raised by the budget tool
    mocker.patch("src.tools.budget", side_effect=ValueError("2 validation errors for budget\nincome\n  Field required [type=missing, input_value={}, input_type=dict]"))
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "budget", "args": {}, "id": "call1"}])]
    config = {"configurable": {"user_id": "testuser", "thread_id": "thread1"}}
    result = store_memory(mock_state, config)
    assert "Error in tool budget: 2 validation errors for budget\nincome\n  Field required" in result["messages"][0]["content"]

def test_route_message_tool_call(mock_state):
    """Test route_message routes to store_memory for tool calls."""
    mock_state.messages = [AIMessage(content="", tool_calls=[{"name": "budget", "args": {}, "id": "call1"}])]
    assert route_message(mock_state) == "store_memory"

def test_route_message_summary(mock_state):
    """Test route_message routes to summarize_conversation for long conversations."""
    mock_state.messages = [HumanMessage(content="msg")] * 10 + [AIMessage(content="response")]
    assert route_message(mock_state) == "summarize_conversation"

def test_route_message_end(mock_state):
    """Test route_message routes to __end__ for non-tool call messages."""
    mock_state.messages = [AIMessage(content="Hello!")]
    assert route_message(mock_state) == "__end__"

def test_build_graph(mock_sqlite_saver):
    """Test build_graph creates a graph with correct name and checkpointer."""
    graph = build_graph(mock_sqlite_saver)
    assert graph.name == "Aza Man"
    assert mock_sqlite_saver == graph.checkpointer
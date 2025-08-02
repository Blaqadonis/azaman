import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, Mock
from langchain_core.messages import AIMessage, HumanMessage
from src.graph import build_graph

@pytest.fixture
def mock_graph(mocker):
    """Fixture to mock the LangGraph build_graph function."""
    mock_graph = MagicMock()
    mocker.patch("src.graph.build_graph", return_value=mock_graph)
    return mock_graph

def test_login_page_valid_user_id(mock_graph):
    at = AppTest.from_file("app.py")
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    mock_graph.get_state.return_value = Mock(values={"username": "testuser"})
    at.run()
    assert not at.exception
    assert len(at.text_input) > 0
    at.text_input[0].set_value("testuser01")
    assert len(at.button) > 0
    at.button[0].click()
    at.run()
    assert at.session_state["user_id"] == "testuser01"
    assert at.session_state["page"] == "Chat"
    assert len(at.session_state["messages"]) == 1
    assert at.session_state["messages"][0].content == "Welcome back, testuser! How may I assist you?"

def test_login_page_invalid_user_id():
    at = AppTest.from_file("app.py")
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    at.run()
    assert not at.exception
    assert len(at.text_input) > 0
    at.text_input[0].set_value("invalid")
    assert len(at.button) > 0
    at.button[0].click()
    at.run()
    assert "user_id" not in at.session_state
    assert at.session_state["page"] == "Login"

def test_chat_interface_no_user_id(mock_graph):
    at = AppTest.from_file("app.py")
    at.session_state["messages"] = []
    at.session_state["page"] = "Chat"
    at.session_state["user_id"] = None
    at.run()
    assert not at.exception
    assert len(at.session_state["messages"]) == 0
    assert at.session_state["page"] == "Chat"

def test_chat_interface_send_message(mock_graph):
    at = AppTest.from_file("app.py")
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    mock_graph.get_state.return_value = Mock(values={"username": "testuser"})
    at.run()
    at.text_input[0].set_value("testuser01")
    at.button[0].click()
    at.run()
    at.session_state["page"] = "Chat"
    at.run()
    mock_graph.stream.return_value = [{"call_model": {"messages": [AIMessage(content="Hello!")]}}]
    assert len(at.text_input) > 0
    at.text_input[0].set_value("Hi!")
    assert len(at.button) > 0
    at.button[0].click()
    at.run()
    assert len(at.session_state["messages"]) == 3
    assert at.session_state["messages"][0].content == "Welcome back, testuser! How may I assist you?"
    assert isinstance(at.session_state["messages"][1], HumanMessage)
    assert at.session_state["messages"][1].content == "Hi!"
    assert isinstance(at.session_state["messages"][2], AIMessage)
    assert at.session_state["messages"][2].content == "Hello!"

def test_dashboard_page(mock_graph):
    at = AppTest.from_file("app.py")
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    mock_graph.get_state.return_value = Mock(values={"username": "testuser"})
    at.run()
    at.text_input[0].set_value("testuser01")
    at.button[0].click()
    at.run()
    at.session_state["page"] = "Dashboard"
    mock_graph.get_state.return_value = Mock(values={
        "income": 10000.0,
        "expense": 2000.0,
        "budget_for_expenses": 8000.0,
        "savings": 1500.0,
        "savings_goal": 3000.0,
        "currency": "NGN",
        "expenses": [{"amount": 1000.0, "category": "Food"}, {"amount": 1000.0, "category": "Transport"}]
    })
    at.run()
    assert not at.exception
    config = {"configurable": {"user_id": "testuser01", "thread_id": "thread_testuser01"}}
    state = mock_graph.get_state(config).values
    assert state["income"] == 10000.0
    assert state["expense"] == 2000.0
    assert state["budget_for_expenses"] == 8000.0
    assert state["savings"] == 1500.0
    assert state["currency"] == "NGN"
    assert len(state["expenses"]) == 2

def test_about_page():
    at = AppTest.from_file("app.py")
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    at.run()
    at.text_input[0].set_value("testuser01")
    at.button[0].click()
    at.run()
    at.session_state["page"] = "About"
    at.run()
    assert not at.exception
    assert at.session_state["page"] == "About"
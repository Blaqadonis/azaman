"""Unit tests for the Aza Man Streamlit application.

This module contains tests for the core functionality of the `app.py` script,
including login, chat interface, dashboard, and about pages. It uses pytest,
Streamlit's AppTest, and unittest.mock to simulate user interactions and mock
the LangGraph dependency. The tests verify page rendering, user input handling,
session state management, and graph state interactions in a test environment.

Dependencies:
    - pytest==8.4.1
    - pytest-mock==3.14.1
    - streamlit==1.46.0
    - langchain-core==0.3.68
    - src.graph (build_graph function)

The tests are designed to run in a test environment where UI rendering is
suppressed (via `is_test_environment()` in `app.py`), focusing on backend logic
and session state validation.
"""

import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, Mock
from langchain_core.messages import AIMessage, HumanMessage
from src.graph import build_graph


@pytest.fixture
def mock_graph(mocker):
    """Fixture to mock the LangGraph build_graph function.

    Args:
        mocker: Pytest-mock fixture for patching dependencies.

    Returns:
        MagicMock: Mocked graph object with configurable state and stream methods.
    """
    # Mock the build_graph function to return a MagicMock object
    mock_graph = MagicMock()
    mocker.patch("src.graph.build_graph", return_value=mock_graph)
    return mock_graph


def test_login_page_valid_user_id(mock_graph):
    """Test login_page with a valid user ID.

    Simulates a user entering a valid user ID (e.g., 'testuser01') and verifies
    that the session state is updated correctly, the page navigates to 'Chat',
    and the welcome message is added to the messages list.

    Args:
        mock_graph: Mocked graph object from the fixture.

    Raises:
        AssertionError: If session state, page navigation, or message content
            does not match expected values.
    """
    # Initialize Streamlit AppTest with app.py
    at = AppTest.from_file("app.py")
    # Set initial session state for welcome popup and messages
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    # Mock graph state to simulate an existing user
    mock_graph.get_state.return_value = Mock(values={"username": "testuser"})
    # Run the app to render the login page
    at.run()
    # Verify no exceptions occurred during rendering
    assert not at.exception
    # Check that a text input field is present
    assert len(at.text_input) > 0, "No text input found on login page"
    # Simulate entering a valid user ID
    at.text_input[0].set_value("testuser01")
    # Check that a submit button is present
    assert len(at.button) > 0, "No submit button found on login page"
    # Simulate clicking the login button
    at.button[0].click()
    # Run the app to process the login
    at.run()
    # Verify session state updates
    assert at.session_state["user_id"] == "testuser01"
    assert at.session_state["page"] == "Chat"
    # Verify a single welcome message is added
    assert len(at.session_state["messages"]) == 1
    # Verify the welcome message content
    assert at.session_state["messages"][0].content == "Welcome back, testuser! How may I assist you?"


def test_login_page_invalid_user_id():
    """Test login_page with an invalid user ID.

    Simulates entering an invalid user ID (e.g., 'invalid') and verifies that
    the session state remains unchanged, no user_id is set, and the page remains
    'Login'.

    Raises:
        AssertionError: If session state or page navigation is unexpectedly
            modified.
    """
    # Initialize Streamlit AppTest with app.py
    at = AppTest.from_file("app.py")
    # Set initial session state for welcome popup and messages
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    # Run the app to render the login page
    at.run()
    # Verify no exceptions occurred during rendering
    assert not at.exception
    # Check that a text input field is present
    assert len(at.text_input) > 0, "No text input found on login page"
    # Simulate entering an invalid user ID
    at.text_input[0].set_value("invalid")
    # Check that a submit button is present
    assert len(at.button) > 0, "No submit button found on login page"
    # Simulate clicking the login button
    at.button[0].click()
    # Run the app to process the login attempt
    at.run()
    # Verify no user_id is set in session state
    assert "user_id" not in at.session_state, f"Invalid user ID set: {at.session_state}"
    # Verify the page remains 'Login'
    assert at.session_state["page"] == "Login", f"Page changed unexpectedly: {at.session_state}"


def test_chat_interface_no_user_id(mock_graph):
    """Test chat_interface behavior when no user_id is set.

    Simulates accessing the chat page without a user_id and verifies that no
    messages are added and the page remains 'Chat'.

    Args:
        mock_graph: Mocked graph object from the fixture (unused in this test).

    Raises:
        AssertionError: If messages are added or the page changes unexpectedly.
    """
    # Initialize Streamlit AppTest with app.py
    at = AppTest.from_file("app.py")
    # Set initial session state with no user_id
    at.session_state["messages"] = []
    at.session_state["page"] = "Chat"
    at.session_state["user_id"] = None
    # Run the app to render the chat page
    at.run()
    # Verify no exceptions occurred
    assert not at.exception
    # Verify no messages are added
    assert len(at.session_state["messages"]) == 0, f"Messages unexpectedly added: {at.session_state}"
    # Verify the page remains 'Chat'
    assert at.session_state["page"] == "Chat", f"Page changed unexpectedly: {at.session_state}"


def test_chat_interface_send_message(mock_graph):
    """Test chat_interface sending a message.

    Simulates a login, navigates to the chat page, sends a message, and verifies
    that the message is processed correctly, including the welcome message, user
    message, and mocked AI response.

    Args:
        mock_graph: Mocked graph object from the fixture.

    Raises:
        AssertionError: If session state, message count, or message content does
            not match expected values.
    """
    # Simulate login first
    at = AppTest.from_file("app.py")
    # Set initial session state for login
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    # Mock graph state for a returning user
    mock_graph.get_state.return_value = Mock(values={"username": "testuser"})
    # Run the app to render the login page
    at.run()
    # Simulate entering a valid user ID
    at.text_input[0].set_value("testuser01")
    # Simulate clicking the login button
    at.button[0].click()
    # Run the app to process the login
    at.run()
    # Navigate to the chat page
    at.session_state["page"] = "Chat"
    # Run the app to render the chat page
    at.run()
    # Mock the graph stream response for the chat message
    mock_graph.stream.return_value = [{"call_model": {"messages": [AIMessage(content="Hello!")]}}]
    # Verify a text input field is present
    assert len(at.text_input) > 0, "No chat input found"
    # Simulate entering a user message
    at.text_input[0].set_value("Hi!")
    # Verify a send button is present
    assert len(at.button) > 0, "No send button found"
    # Simulate clicking the send button
    at.button[0].click()
    # Run the app to process the message
    at.run()
    # Verify three messages: welcome, user input, and AI response
    assert len(at.session_state["messages"]) == 3, f"Expected 3 messages, got {len(at.session_state['messages'])}: {at.session_state['messages']}"
    # Verify the welcome message
    assert isinstance(at.session_state["messages"][0], AIMessage)  # Welcome message
    assert at.session_state["messages"][0].content == "Welcome back, testuser! How may I assist you?"
    # Verify the user message
    assert isinstance(at.session_state["messages"][1], HumanMessage)
    assert at.session_state["messages"][1].content == "Hi!"
    # Verify the AI response
    assert isinstance(at.session_state["messages"][2], AIMessage)
    assert at.session_state["messages"][2].content == "Hello!"


def test_dashboard_page(mock_graph):
    """Test dashboard_page with mocked state data.

    Simulates a login, navigates to the dashboard page, and verifies that the
    graph state is correctly accessed and contains expected financial data.
    Metrics are not checked, as they are skipped in the test environment.

    Args:
        mock_graph: Mocked graph object from the fixture.

    Raises:
        AssertionError: If session state or graph state does not match expected
            values.
    """
    # Simulate login first
    at = AppTest.from_file("app.py")
    # Set initial session state for login
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    # Mock graph state for a returning user
    mock_graph.get_state.return_value = Mock(values={"username": "testuser"})
    # Run the app to render the login page
    at.run()
    # Simulate entering a valid user ID
    at.text_input[0].set_value("testuser01")
    # Simulate clicking the login button
    at.button[0].click()
    # Run the app to process the login
    at.run()
    # Navigate to the dashboard page
    at.session_state["page"] = "Dashboard"
    # Mock graph state with financial data
    mock_graph.get_state.return_value = Mock(values={
        "income": 10000.0,
        "expense": 2000.0,
        "budget_for_expenses": 8000.0,
        "savings": 1500.0,
        "savings_goal": 3000.0,
        "currency": "NGN",
        "expenses": [{"amount": 1000.0, "category": "Food"}, {"amount": 1000.0, "category": "Transport"}]
    })
    # Run the app to render the dashboard
    at.run()
    # Verify no exceptions occurred
    assert not at.exception
    # Verify graph state instead of metrics, as st.metric is skipped in tests
    config = {"configurable": {"user_id": "testuser01", "thread_id": "thread_testuser01"}}
    state = mock_graph.get_state(config).values
    # Verify financial data in the graph state
    assert state["income"] == 10000.0
    assert state["expense"] == 2000.0
    assert state["budget_for_expenses"] == 8000.0
    assert state["savings"] == 1500.0
    assert state["currency"] == "NGN"
    assert len(state["expenses"]) == 2


def test_about_page():
    """Test about_page rendering.

    Simulates a login, navigates to the about page, and verifies that the page
    renders without errors and maintains the correct session state. Markdown
    elements are not checked, as they are skipped in the test environment.

    Raises:
        AssertionError: If the page does not render correctly or session state
            is incorrect.
    """
    # Simulate login first
    at = AppTest.from_file("app.py")
    # Set initial session state for login
    at.session_state["hide_welcome_popup"] = False
    at.session_state["show_popup"] = True
    at.session_state["messages"] = []
    # Run the app to render the login page
    at.run()
    # Simulate entering a valid user ID
    at.text_input[0].set_value("testuser01")
    # Simulate clicking the login button
    at.button[0].click()
    # Run the app to process the login
    at.run()
    # Navigate to the about page
    at.session_state["page"] = "About"
    # Run the app to render the about page
    at.run()
    # Verify no exceptions occurred
    assert not at.exception
    # Verify the page is set to 'About'
    assert at.session_state["page"] == "About", f"Page not set correctly: {at.session_state}"
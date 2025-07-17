"""Project configuration for Aza Man."""

import sys
import os
import re
import logging
import sqlite3
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from langgraph.checkpoint.sqlite import SqliteSaver
import streamlit as st
from streamlit.errors import StreamlitAPIException
from dotenv import load_dotenv
from src.graph import build_graph
from project_config import PROJECT_CONFIG

# Check if running in test environment
def is_test_environment():
    return "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST")

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the Graph
conn = sqlite3.connect(PROJECT_CONFIG["data_path"], check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = build_graph(checkpointer)

# Streamlit page configuration
if not is_test_environment():
    st.set_page_config(
        page_title=PROJECT_CONFIG["project_name"],
        page_icon=PROJECT_CONFIG["page_icon"],
        layout="centered",
        initial_sidebar_state="expanded"
    )

# Custom CSS
if not is_test_environment():
    st.markdown(f"""
        <style>
        :root {{
            --primary-red: {PROJECT_CONFIG["theme"]["primary_color"]};
            --dark-bg: {PROJECT_CONFIG["theme"]["dark_bg"]};
            --card-bg: {PROJECT_CONFIG["theme"]["card_bg"]};
        }}
        .stApp {{
            background-color: var(--dark-bg);
            color: white;
        }}
        .stTextInput input {{
            background-color: var(--card-bg) !important;
            color: white !important;
            border: 1px solid var(--primary-red) !important;
        }}
        .stButton>button {{
            background-color: var(--primary-red) !important;
            color: white !important;
            border: none;
            transition: all 0.3s;
        }}
        .stButton>button:hover {{
            opacity: 0.8;
            transform: scale(1.05);
        }}
        .assistant-message {{
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid var(--primary-red);
            margin: 1rem 0;
        }}
        .user-message {{
            background: #2A2A2A;
            padding: 1rem;
            border-radius: 10px;
            border-right: 4px solid #FFFFFF;
            margin: 1rem 0;
        }}
        .sidebar .sidebar-content {{
            background: var(--dark-bg) !important;
            border-right: 1px solid var(--primary-red);
        }}
        .intro-text {{
            text-align: center;
            font-size: 1.1rem;
            color: #CCCCCC;
            line-height: 1.6;
        }}
        .active-header {{
            background: var(--card-bg);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid var(--primary-red);
            margin-bottom: 1rem;
            text-align: center;
            font-size: 1.2rem;
        }}
        .dont-show-again {{
            margin-top: 15px;
            display: flex;
            align-items: center;
        }}
        [data-testid="stDialog"] {{
            background: var(--card-bg);
            border-left: 4px solid var(--primary-red);
            border-radius: 10px;
            color: white;
            width: 80%;
            max-width: 500px;
        }}
        .about-section {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid var(--primary-red);
            margin: 1rem 0;
        }}
        .about-section h2 {{
            color: var(--primary-red);
        }}
        .about-section a {{
            color: var(--primary-red);
            text-decoration: none;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)

# Initialize session state
if "page" not in st.session_state:
    st.session_state["page"] = "Login"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "hide_welcome_popup" not in st.session_state:
    st.session_state["hide_welcome_popup"] = False
if "show_popup" not in st.session_state:
    st.session_state["show_popup"] = not st.session_state["hide_welcome_popup"]

def show_welcome_popup():
    """Display welcome popup for new users."""
    if is_test_environment():
        logger.debug("Skipping dialog in test environment")
        return
    if not st.session_state["hide_welcome_popup"] and st.session_state["show_popup"]:
        try:
            @st.dialog(f"Welcome to {PROJECT_CONFIG['project_name']}!")
            def welcome_dialog():
                st.markdown(f'<h2 style="color: var(--primary-red);">Welcome to {PROJECT_CONFIG["project_name"]}!</h2>', unsafe_allow_html=True)
                st.markdown(PROJECT_CONFIG["instructions"], unsafe_allow_html=True)
                st.markdown('<div class="dont-show-again">', unsafe_allow_html=True)
                dont_show = st.checkbox("Don't show this again")
                if dont_show:
                    st.session_state["hide_welcome_popup"] = True
                    st.session_state["show_popup"] = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            welcome_dialog()
        except StreamlitAPIException as e:
            logger.debug(f"StreamlitAPIException in dialog: {str(e)}")

def login_page():
    """Render login page with user ID validation."""
    show_welcome_popup()
    if not is_test_environment():
        st.markdown(f"<h1 style='color: var(--primary-red); text-align: center;'>Welcome to {PROJECT_CONFIG['project_name']}</h1>", unsafe_allow_html=True)
        st.markdown("<p class='intro-text'>Enter your User ID to begin (4-10 chars, last 2 digits, e.g., odogwu91)</p>", unsafe_allow_html=True)
    with st.form(key="login_form"):
        user_id = st.text_input("User ID", max_chars=10, key="login_user_id")
        submit_button = st.form_submit_button("Login")
        if submit_button:
            if re.match(r"^[a-zA-Z]{2,8}\d{2}$", user_id):
                st.session_state["user_id"] = user_id
                st.session_state["thread_id"] = f"thread_{user_id}"
                st.session_state["page"] = "Chat"
                try:
                    config = {"configurable": {"user_id": user_id, "thread_id": st.session_state["thread_id"]}}
                    state = graph.get_state(config).values
                    if state.get("username"):
                        st.session_state["messages"].append(
                            AIMessage(content=f"Welcome back, {state['username']}! How may I assist you?")
                        )
                except Exception as e:
                    logger.error(f"Error fetching initial state: {str(e)}")
                    st.session_state["messages"].append(
                        AIMessage(content=f"Error loading session.")
                    )
                if not is_test_environment():
                    st.rerun()
            else:
                if not is_test_environment():
                    st.error("Invalid User ID! Must be 4-10 characters, ending with 2 digits (e.g., blaq01).")

def landing_page():
    if not is_test_environment():
        st.markdown("<h1 style='color: #FF0000; text-align: center; font-family: Arial;'>Aza Man</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #FFFFFF;'>AI-Powered Financial Guardian</h3>", unsafe_allow_html=True)
        st.image('images/azaman2.png', use_container_width=True)
        st.markdown("<div class='intro-text'>Welcome to your personal financial command center. Select 'Chat' from the sidebar to begin.</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #FFFFFF;'>Key Features</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div style='text-align: center;'><span style='font-size: 2rem;'>🔥</span><h3>Smart Budgeting</h3><p>Plan your finances with AI precision</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='text-align: center;'><span style='font-size: 2rem;'>💸</span><h3>Expense Tracking</h3><p>Monitor spending in real-time</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div style='text-align: center;'><span style='font-size: 2rem;'>📈</span><h3>Savings Goals</h3><p>Set and achieve financial targets</p></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-top: 2rem;'><small>Developed by </small><a href='https://www.linkedin.com/in/chinonsoodiaka/' style='color: var(--primary-red); text-decoration: none; font-weight: bold;'>🅱🅻🅰🆀</a></div>", unsafe_allow_html=True)

def chat_interface():
    """Render chat interface with Aza Man graph responses."""
    if "user_id" not in st.session_state:
        if not is_test_environment():
            st.error("Please log in first!")
        return
    if not is_test_environment():
        st.markdown(
            f"""
            <div class='active-header'>
                <span style='color: var(--primary-red);'>{PROJECT_CONFIG['project_name']}</span> 
                <span style='color: #FFFFFF;'> is NOW</span> 
                <span style='color: #FFD700;'>★</span>
                <span style='color: #FFD700;'>★</span>
                <span style='color: #FFD700;'> ACTIVE</span> 
                <span style='color: #FFD700;'>★</span>
                <span style='color: #FFD700;'>★</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["messages"]:
            if isinstance(msg, AIMessage):
                content = re.sub(r'<[^>]+>\s*', '', msg.content, flags=re.DOTALL).strip()
                if not is_test_environment():
                    st.markdown(f"<div class='assistant-message'><div style='color: var(--primary-red); font-weight: bold;'>{PROJECT_CONFIG['project_name'].upper()}:</div>{content}</div>", unsafe_allow_html=True)
            elif isinstance(msg, HumanMessage):
                if not is_test_environment():
                    st.markdown(f"<div class='user-message'><div style='color: white; font-weight: bold;'>YOU:</div>{msg.content}</div>", unsafe_allow_html=True)

    prompt = st.text_input("Send secure message...", placeholder="Type your message here...", key="chat_input")
    if st.button("Send"):
        if prompt:
            st.session_state["messages"].append(HumanMessage(content=prompt))
            if not is_test_environment():
                with st.spinner("**...Thinking...**"):
                    try:
                        config = {"configurable": {"user_id": st.session_state["user_id"], "thread_id": st.session_state["thread_id"]}}
                        inputs = {"messages": [HumanMessage(content=prompt)]}
                        response = ""
                        for output in graph.stream(inputs, config, stream_mode="updates"):
                            for node, data in output.items():
                                if "messages" in data and data["messages"]:
                                    msg = data["messages"][-1]
                                    if hasattr(msg, "content") and msg.content:
                                        response += msg.content
                        if not response:
                            response = "Sorry, I couldn't process that. Please try again."
                        st.session_state["messages"].append(AIMessage(content=response))
                    except Exception as e:
                        logger.error(f"Error in chat processing: {str(e)}")
                        response = f"Error: {str(e)}"
                        st.session_state["messages"].append(AIMessage(content=response))
                    st.rerun()
            else:
                # Simulate response in test environment
                try:
                    config = {"configurable": {"user_id": st.session_state["user_id"], "thread_id": st.session_state["thread_id"]}}
                    inputs = {"messages": [HumanMessage(content=prompt)]}
                    response = ""
                    for output in graph.stream(inputs, config, stream_mode="updates"):
                        for node, data in output.items():
                            if "messages" in data and data["messages"]:
                                msg = data["messages"][-1]
                                if hasattr(msg, "content") and msg.content:
                                    response += msg.content
                    if not response:
                        response = "Sorry, I couldn't process that. Please try again."
                    st.session_state["messages"].append(AIMessage(content=response))
                except Exception as e:
                    logger.error(f"Error in chat processing: {str(e)}")
                    st.session_state["messages"].append(AIMessage(content=f"Error: {str(e)}"))

def dashboard_page():
    """Render dashboard with financial metrics from Aza Man state."""
    if "user_id" not in st.session_state:
        if not is_test_environment():
            st.error("Please log in first!")
        return

    try:
        config = {"configurable": {"user_id": st.session_state["user_id"], "thread_id": st.session_state["thread_id"]}}
        state_data = graph.get_state(config).values
    except Exception as e:
        logger.error(f"Error fetching dashboard state: {str(e)}")
        if not is_test_environment():
            st.error("Failed to load dashboard data. Please try again.")
        return

    if not is_test_environment():
        st.subheader("Summary Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Income", f"{state_data.get('income', 0.0):,.2f} {state_data.get('currency', PROJECT_CONFIG['currency_default'])}")
        with col2: st.metric("Total Expenses", f"{state_data.get('expense', 0.0):,.2f} {state_data.get('currency', PROJECT_CONFIG['currency_default'])}")
        with col3: st.metric("Remaining Budget", f"{state_data.get('budget_for_expenses', 0.0) - state_data.get('expense', 0.0):,.2f} {state_data.get('currency', PROJECT_CONFIG['currency_default'])}")
        with col4: st.metric("Current Savings", f"{state_data.get('savings', 0.0):,.2f} {state_data.get('currency', PROJECT_CONFIG['currency_default'])}")

        st.subheader("Savings Progress")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=state_data.get('savings', 0.0), domain={'x': [0, 1], 'y': [0, 1]},
            title={"text": "Savings vs Goal"}, gauge={"axis": {"range": [0, state_data.get('savings_goal', 0.0)]}, "bar": {"color": "green"}}
        ))
        st.plotly_chart(fig_gauge)

        st.subheader("Expense Distribution")
        expenses = state_data.get('expenses', [])
        if expenses:
            fig_pie = px.pie(values=[e["amount"] for e in expenses], names=[e["category"] for e in expenses], color_discrete_sequence=px.colors.sequential.Reds)
            st.plotly_chart(fig_pie)
        else:
            st.write("No expenses logged yet.")

        st.subheader("Expense Trends")
        if expenses:
            dates = [datetime.now().date() if 'date' not in e else datetime.strptime(e['date'], '%Y-%m-%d').date() for e in expenses]
            amounts = [e["amount"] for e in expenses]
            fig_line = px.line(x=dates, y=amounts, labels={"x": "Date", "y": f"Amount ({state_data.get('currency', PROJECT_CONFIG['currency_default'])})"})
            st.plotly_chart(fig_line)
        else:
            st.write("No expense trends to display yet.")

def about_page():
    """Render About page with project details and links."""
    if not is_test_environment():
        st.markdown(f"<h1 style='color: var(--primary-red); text-align: center;'>About</h1>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='about-section'>
                <h2>{PROJECT_CONFIG['project_name']}</h2>
                <p>Aza Man is an AI-powered personal financial assistant designed to help users manage their budget, track expenses, and achieve savings goals.</p>
                <h2>How to Use</h2>
                <p><a href='{PROJECT_CONFIG['youtube_url']}'>YouTube</a></p>
                <h2>Connect</h2>
                <p>Developed by <a href='{PROJECT_CONFIG['author_linkedin']}'>{PROJECT_CONFIG['author_name']}</a></p>
            </div>
            """,
            unsafe_allow_html=True
        )

def main():
    """Main application logic."""
    if not is_test_environment():
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox("Select Page", ["Home", "Chat", "Dashboard", "About"], disabled=(st.session_state["page"] == "Login"))
    else:
        page = st.session_state.get("page", "Login")
    if st.session_state["page"] == "Login":
        login_page()
    elif page == "Home":
        landing_page()
    elif page == "Chat":
        chat_interface()
    elif page == "Dashboard":
        dashboard_page()
    elif page == "About":
        about_page()

    if not is_test_environment():
        if st.sidebar.button("◀ RETURN TO BASE"):
            st.session_state.clear()
            st.session_state["page"] = "Login"
            st.rerun()

if __name__ == "__main__":
    main()
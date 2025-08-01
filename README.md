# Aza Man: AI-Powered Autonomous Financial Assistant

![Aza Man Screenshot](https://github.com/user-attachments/assets/a270c3eb-585a-4845-b2dc-325a5e27554e)

#### Author: [🅱🅻🅰🆀](https://www.linkedin.com/in/chinonsoodiaka/)

## Abstract
**Aza Man** is a Multi-Agent AI system developed for **[Agentic AI Developer Certification Program 2025](https://app.readytensor.ai/publications/HrJ0xWtLzLNt)**, offered by **ReadyTensor**. Built with a [supervisor architecture (tool-calling)](https://langchain-ai.github.io/langgraph/concepts/multi_agent/#multi-agent-architectures), it empowers users with personalized financial management. Aza Man leverages **LangGraph** for workflow orchestration and **SQLite** for state persistence, enabling a conversational assistant that sets budgets, tracks expenses, and manages savings goals with autonomy and context-awareness. It integrates cost-efficient SOTA language models via [OpenRouter](https://openrouter.ai/), [Groq](https://console.groq.com/), and [TogetherAI](https://api.together.xyz/), with a **Streamlit** interface for seamless interaction. Aza Man promotes financial literacy and empowerment through intelligent automation, showcasing scalable AI agent design.

## 1. Introduction
Agentic AI systems enable autonomous, goal-driven interactions, moving beyond traditional chatbots. Aza Man addresses the need for accessible financial tools, particularly in regions like Nigeria, where economic challenges demand personalized budgeting solutions. By combining **LangGraph** for conversational workflows, **SQLite** for state management, and tool-calling capabilities, Aza Man delivers a robust, scalable financial assistant.

This publication details Aza Man’s architecture, functionality, evaluation, deployment, and testing, highlighting its impact as a portfolio project for the certification program.

## 2. System Architecture
Aza Man features a modular, extensible multi-agent architecture:
- **Conversational Workflow**: LangGraph orchestrates multi-step reasoning and tool invocation, routing user inputs to appropriate tools and maintaining conversation state.
- **State Persistence**: A custom SQLite checkpointer stores user data for context-aware interactions across sessions.
- **Tool Integration**: Tools are bound to SOTA models via LangChain’s ```.bind_tools````.
- **Frontend**: A Streamlit interface provides an interactive dashboard for financial tracking.
- **LLM Integration**: Supports models from Groq, OpenRouter, and TogetherAI for cost-efficient performance.

![Screen Recording - Jul 15, 2025-VEED](https://github.com/user-attachments/assets/84330dbf-f17b-4ba0-8ec7-bba6977d504a)


*Illustration: Aza Man live feed, showcasing real-time financial tracking.*

## 3. Functionality
Aza Man offers:
- **Budget Creation**: Set income, savings goals, and expense budgets.
- **Expense Tracking**: Log expenses.
- **Savings Management**: Track savings progress.
- **Username Setting**: Personalize interactions.
- **Math Calculations**: Perform financial calculations.

Tools are integrated with plans to adopt the [Model Context Protocol (MCP)](https://langchain-ai.github.io/langgraph/agents/mcp/#use-mcp-tools) for standardized tool integration in future updates.

## 4. Evaluation
Aza Man was evaluated with a comprehensive test suite:
- **Test Suite**: 40 unit tests across `test_app.py` (6), `test_configuration.py` (5), `test_graph.py` (12), `test_prompts.py` (2), `test_state.py` (3), and `test_tools.py` (11).
- **Coverage**: 80% overall (287 statements, 56 missed), 73% for `graph.py` (143 statements, 39 missed).
- **Results**: 39/40 tests pass. The failing test (`test_store_memory_tool_failure`) is due to a Pydantic validation mismatch but does not impact core functionality.
- **Test Cases**: Cover LLM invocation, tool execution, routing, summarization, and error handling (LLM failures, JSON errors, invalid tools, empty inputs, inappropriate content).

## 5. Challenges and Lessons Learned
- **Streamlit & Async Events**: Streamlit struggles with async endpoints. Synchronous calls were used, but Gradio may be explored for async support.
- **LangChain MCP Adapters**: ```AsyncSQLiteSaver``` failed to update state variables beyond ```messages```, leading to reliance on synchronous `SqliteSaver`.
- **Pydantic Validation**: The failing test highlights the need for precise mocking of Pydantic-based tools to avoid validation errors.

## 6. Setup and Installation
1. Clone the repository:
   ```bash
   https://github.com/blaqadonis/azaman.
2. Create and activate a virtual environment:
   ```bash
   python -m venv azaman
   source azaman/bin/activate  # Linux/Mac
   azaman\Scripts\activate  # Windows
3. Install dependencies (You need to have a CONDA environment):
   ```bash
   pip install -r requirements.txt .
4. Create ```data``` directory (datapath for logs, metadata, and database):
   ```bash
   mkdir -p data
5. Next, create a ```.env``` file:
   ```bash
    GROQ_API_KEY=...
    OPENROUTER_API_KEY=...
    TOGETHER_API_KEY=...
    
    LANGCHAIN_TRACING_V2=false # Optional - for tracing.
    LANGCHAIN_API_KEY=...
    LANGCHAIN_PROJECT=Aza Man_FOR_AAIDC2025
6. Update ```project_config.py``` ( Update ```model```, ```evaluator```, and ```provider - groq, together, or openrouter```):
   ```bash
    PROJECT_CONFIG = {
      "project_name": "Aza Man",
      "page_icon": "images/azaman2.png",
      "backstory": (
          "You are Aza Man, an AI-powered personal financial assistant designed to help users manage their budget, ..."
  
      ),
      "instructions": (
          "..."
          "... "
          "..."
          "..."
          "..."
          "..."
      ),
      "youtube_url": "https://youtu.be/8CEyOVjqtRI",
      "author_linkedin": "https://www.linkedin.com/in/chinonsoodiaka/",
      "author_name": "🅱🅻🅰🆀",
      "data_path": "data/azaman.db",
      "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
      "evaluator": "deepseek-ai/DeepSeek-V3",
      "provider": "groq",
      "currency_default": "NGN",
      "state_variables": {
          "username": str,
          "income": float,
          "budget_for_expenses": float,
          "expense": float,
          "expenses": list,
          "savings_goal": float,
          "savings": float,
          "currency": str,
          "summary": str
      },
      "state_defaults": {
          "username": "",
          "income": 0.0,
          "budget_for_expenses": 0.0,
          "expense": 0.0,
          "expenses": [],
          "savings_goal": 0.0,
          "savings": 0.0,
          "currency": "",
          "summary": ""
      },
      "tools": ["set_username", "budget", "log_expenses", "math_tool"],
      "theme": {
          "primary_color": "#FF0000",
          "dark_bg": "#0A0A0A",
          "card_bg": "#1A1A1A"
      }}

## 7. Deployment:
* **Local** (Access UI [http://localhost:8501/](http://localhost:8501/)):
  ```bash
  streamlit run app.py
* **Render**:
  Live at [Azaman on Render](https://azaman.onrender.com/).
* **Streamlit Cloud**:
  Live at [Azaman on Streamlit](https://azaman-aaidc2025.streamlit.app/)

## 8. Testing:
Run tests with coverage: ``` pytest --cov=src tests/ --cov-report=html```.
## 9. Future Work
To enhance Aza Man, future iterations could include:

* **Feature Expansion**: Add tools for currency conversion, investment tracking, or debt management.
* **Multi-User Support**: Scale the SQLite database for concurrent users, leveraging Kubernetes for deployment.github.com
* **Multimodal Capabilities**: Integrate image processing (e.g., scanning receipts) using models like GPT-4o.analyticsvidhya.com
* **Better Guardrails**: Add safety checks to prevent erroneous financial calculations or data leaks.
* **MCP**: Standardize all tool integration via Model Context Protocol.
These enhancements would make Aza Man a more robust, enterprise-ready financial assistant.

## Conclusion
Aza Man, developed for ```AAIDC 2025```, showcases the potential of AI agents to transform personal finance. Aza Man paves the way for future innovations in financial automation, aligning with the certification program’s mission to train developers in cutting-edge AI technologies.

[Link to project publication](https://app.readytensor.ai/publications/aza-man-JJ1fQYdl6gVE)

## Acknowledgments
The development of Aza Man was supported by the Ready Tensor Agentic AI Developer Certification Program.

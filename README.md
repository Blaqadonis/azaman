# Aza Man: AI-Powered Autonomous Financial Assistant

![Aza Man Screenshot](https://github.com/user-attachments/assets/a270c3eb-585a-4845-b2dc-325a5e27554e)

#### Author: [🅱🅻🅰🆀](https://www.linkedin.com/in/chinonsoodiaka/)

## Abstract
**Aza Man** is a Multi-Agent AI system developed for the **[Agentic AI Developer Certification Program 2025](https://app.readytensor.ai/publications/HrJ0xWtLzLNt)**, offered by **ReadyTensor**. Built with a [supervisor architecture (tool-calling)](https://langchain-ai.github.io/langgraph/concepts/multi_agent/#multi-agent-architectures), it empowers users with personalized financial management. Aza Man leverages **LangGraph** for workflow orchestration and **SQLite** for state persistence, enabling a conversational assistant that sets budgets, tracks expenses, and manages savings goals with autonomy and context-awareness. It integrates cost-efficient SOTA language models via [OpenRouter](https://openrouter.ai/), [Groq](https://console.groq.com/), and [TogetherAI](https://api.together.xyz/), with a **Streamlit** interface for seamless interaction. Aza Man promotes financial literacy and empowerment through intelligent automation, showcasing scalable AI agent design.

## 1. Introduction
Agentic AI systems enable autonomous, goal-driven interactions, moving beyond traditional chatbots. Aza Man addresses the need for accessible financial tools, particularly in regions like Nigeria, where economic challenges demand personalized budgeting solutions. By combining **LangGraph** for conversational workflows, **SQLite** for state management, and tool-calling capabilities, Aza Man delivers a robust, scalable financial assistant.

This publication details Aza Man’s architecture, functionality, evaluation, deployment, and testing, highlighting its impact as a portfolio project for the certification program.

## 2. System Architecture
Aza Man features a modular, extensible multi-agent architecture:
- **Conversational Workflow**: LangGraph orchestrates multi-step reasoning and tool invocation, routing user inputs to appropriate tools and maintaining conversation state.
- **State Persistence**: A custom SQLite checkpointer stores user data for context-aware interactions across sessions.
- **Tool Integration**: Tools are bound to SOTA models via LangChain’s `.bind_tools`.
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
- **Test Suite**: 38 unit tests across `test_app.py` (6), `test_configuration.py` (5), `test_graph.py` (7), `test_prompts.py` (2), `test_state.py` (3), and `test_tools.py` (15).
- **Coverage**: 79% overall (267 statements, 56 missed), 66% for `graph.py` (102 statements, 35 missed).
- **Results**: 38/38 tests pass.
- **Test Cases**: Cover LLM invocation, tool execution, routing, summarization, and error handling (LLM failures, JSON errors, invalid tools, empty inputs, inappropriate content).
- **Coverage Gaps**: The 66% coverage for `graph.py` indicates untested branches in `call_model` and `summarize_conversation`. Future tests will target these areas to reach ~80% coverage.

## 5. Challenges and Lessons Learned
- **Streamlit & Async Events**: Streamlit struggles with async endpoints. Synchronous calls were used, but Gradio may be explored for async support.
- **LangChain MCP Adapters**: `AsyncSQLiteSaver` failed to update state variables beyond `messages`, leading to reliance on synchronous `SqliteSaver`.
- **Pydantic Validation**: Precise mocking of Pydantic-based tools was necessary to handle validation errors in tests.

## 6. Setup and Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Blaqadonis/azaman.git
   cd azaman
   ```
2. **Create and Activate a Virtual Environment**:
   ```bash
   conda create -n azaman python=3.11
   conda activate azaman  # Windows/Linux/Mac
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create `data` Directory** (for logs, metadata, and SQLite database):
   ```bash
   mkdir -p data
   ```
5. **Set Up Environment Variables**:
   Create a `.env` file in the root directory:
   ```bash
   touch .env
   ```
   Add the following (replace with your API keys):
   ```
   GROQ_API_KEY=your_groq_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   TOGETHER_API_KEY=your_together_api_key
   LANGCHAIN_TRACING_V2=false
   LANGCHAIN_API_KEY=your_langchain_api_key
   LANGCHAIN_PROJECT=Aza Man_FOR_AAIDC2025
   ```
6. **Configure Line Endings**:
   The repository includes a `.gitattributes` file to ensure consistent line endings.
7. **Update `project_config.py`**:
   Edit `project_config.py` to set `model`, `evaluator`, and `provider` (e.g., `groq`, `together`, `openrouter`):
   ```python
   PROJECT_CONFIG = {
       "project_name": "Aza Man",
       "page_icon": "images/azaman2.png",
       "backstory": (
           "You are Aza Man, an AI-powered personal financial assistant designed to help users manage their budget, ..."
       ),
       "instructions": (
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
       }
   }
   ```

## 7. Deployment
- **Local** (Access UI at [http://localhost:8501/](http://localhost:8501/)):
  ```bash
  streamlit run app.py
  ```
- **Render**:
  Live at [Azaman on Render](https://azaman.onrender.com/).
- **Streamlit Cloud**:
  Live at [Azaman on Streamlit](https://azaman-aaidc2025.streamlit.app/).

### Troubleshooting
- **API Key Errors**: Ensure `GROQ_API_KEY`, `OPENROUTER_API_KEY`, or `TOGETHER_API_KEY` is set in `.env`. Obtain keys from [Groq](https://console.groq.com/), [OpenRouter](https://openrouter.ai/), or [TogetherAI](https://api.together.xyz/).
- **SQLite Database Issues**: Verify the `data` directory exists and is writable. Run `mkdir -p data` if missing.
- **Streamlit Failure**: Ensure `requirements.txt` dependencies are installed. Run `pip install streamlit` if errors occur.
- **Test Failures**: Run `pytest --cov=src tests/` to check for regressions. Update tests for Pydantic validation errors if needed.
- **Line-Ending Warnings**: The `.gitattributes` file ensures consistent LF endings for Python files. Run `git add --renormalize .` if warnings persist.

## 8. Testing
Run tests with coverage:
```bash
pytest --cov=src tests/ --cov-report=html
```
Output: 38/38 tests pass, 79% coverage. HTML report available in `htmlcov/`.

## 9. Future Work
To enhance Aza Man, future iterations could include:
- **Feature Expansion**: Add tools for currency conversion, investment tracking, or debt management.
- **Multi-User Support**: Scale the SQLite database for concurrent users, leveraging Kubernetes for deployment.
- **Multimodal Capabilities**: Integrate image processing (e.g., scanning receipts) using models like GPT-4o.
- **Better Guardrails**: Add safety checks for erroneous calculations and data leaks, with dedicated tests.
- **Resilience**: Implement retry with exponential backoff and timeout handling for LLM calls.
- **MCP**: Standardize all tool integration via Model Context Protocol.

## Conclusion
Aza Man, developed for **AAIDC 2025**, showcases the potential of AI agents to transform personal finance. It paves the way for future innovations in financial automation, aligning with the certification program’s mission to train developers in cutting-edge AI technologies.

[Link to project publication](https://app.readytensor.ai/publications/aza-man-JJ1fQYdl6gVE)

## Acknowledgments
The development of Aza Man was supported by the Ready Tensor Agentic AI Developer Certification Program.

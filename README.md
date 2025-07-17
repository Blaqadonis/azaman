# Aza Man: AI-Powered Autonomous Financial Assistant

<img width="1402" height="552" alt="azaman2" src="https://github.com/user-attachments/assets/474467e9-ea9e-413f-bfa1-bdab5a43c445" />
  
___________________________________________________________________________________________

# Abstract
**Aza Man** is a Multi-Agent AI system developed as part of **Module 2** of the **Agentic AI Developer Certification Program 2025**, offered by **Ready Tensor**. With a [supervisor architecture(tool-calling)](https://langchain-ai.github.io/langgraph/concepts/multi_agent/#multi-agent-architectures), it was designed to empower users with personalized financial management. Aza Man leverages LangGraph and SQLite to deliver a conversational assistant capable of setting budgets, tracking expenses, and managing savings goals with autonomy and context-awareness. Built with a modular architecture, it integrates tool-calling capabilities via [OpenRouter](https://openrouter.ai/), [Groq](https://console.groq.com/), and [TogetherAI](https://api.together.xyz/) for cost-efficient access to state-of-the-art (SOTA) language models. Aza Man features a Streamlit interface for seamless user interaction and a SQLite-backed state management system for long-term persistence.  Aza Man showcases the potential of AI agents to transform personal finance, promoting financial literacy and empowerment through intelligent automation.

## 1. Introduction
In the rapidly evolving landscape of artificial intelligence, agentic AI systems represent a paradigm shift, enabling autonomous, goal-driven interactions that go beyond traditional chatbot responses. Aza Man exemplifies this shift by providing a financial assistant tailored to individual user needs. Unlike conventional financial tools, Aza Man combines Real-time conversational flows with tool-calling capabilities to manage budgets, log expenses, and track savings goals.

The Agentic AI Developer Certification Program emphasizes hands-on development of real-world AI systems, with Module 2 focusing on Building Agentic Systems at Scale. Aza Man addresses the growing demand for accessible financial management tools, particularly in regions like Nigeria, where economic challenges underscore the need for personalized budgeting solutions. By leveraging LangGraph for workflow orchestration, and SQLite for state persistence, Aza Man delivers a robust, scalable solution.

This publication details Aza Man’s architecture, functionality, evaluation, and its impact as a portfolio project for the certification program. It also highlights lessons learned and future optimization opportunities.

## 2. System Architecture
Aza Man is built with a modular, extensible Multi-agent system architecture to support autonomous financial management. Its core components include:

* Conversational: Aza Man uses LangGraph to orchestrate conversational workflows, enabling multi-step reasoning and tool invocation. The graph manages user inputs, routes them to appropriate tools, and maintains conversation state.
* Personalized: Aza Man uses an in-built custom checkpointer to stores user data in a SQLite database, ensuring persistence across sessions for data like user's name, last recorded budget, last entered expense list, etc. This allows Aza Man to recall user context, in follow-up interactions.
* Equipped with Finance Tools: Aza Man integrates with SOTA models that make tool calls. Tools like ```set_username``` ```budget``` ```log_expense``` and ```math_tool``` enable dynamic updates to the user’s financial state.
* Streamlit Interface: A user-friendly Streamlit frontend provides an interactive dashboard.

![Screen Recording - Jul 15, 2025-VEED](https://github.com/user-attachments/assets/386c5eef-519d-43ee-9054-983ef25f3910)





*Illustration: Aza Man live feed, showcasing real-time financial tracking.*

## 3. Functionality
Aza Man offers a suite of financial management features tailored to assist user in managing their budget:

* Budget Creation.
* Expense Tracking.
* Savings Management & Expert Insights and recommendations.

These features are handled by custom tools bound to my tool-calling LLM thanks to to Langchain's ```.bind_tools```. However, this is not the ideal practice. I intend to update Aza man agent, in the near-future, to make use of [Model Context Protocol](https://langchain-ai.github.io/langgraph/agents/mcp/#use-mcp-tools) to standardize this integration with tools.
I also intend to add more features - like a realtime currency exchange rate calculator for such contexts.

## 4. Evaluation
Aza Man was evaluated using a test suite with just five test cases; it was not rigorouusly tested, I just assessed its accuracy and relevance of responses. The test dataset included:

Username Setup;
Budget Creation; 
Expense Logging;
Off-Topic Input;
Savings Update.

#### Results:

Accuracy: All test cases passed.

## 5. Challenges and Lessons Learned
* **Streamlit & Async Events**: It is not straight-forward to deploy an async endpoint in streamlit. Gradio is better at handling such tasks. However, as was made evident by this project, Streamlit is easy-to-manage for synchronous calls to the endpoint. 
* **Langchain mcp Adapters**: I tried to use Langchain's MCP adapters but its asynchronous cient server meant I had to use ```AsyncSQLiteSaver``` which kept failing to update other state variablles except ```messages```.

## 6. How To Run
Follow these steps in order:
* Go into the root folder. Open up a bash terminal, then enter ```pip install -r requirements.txt``` (You need to have a CONDA environment).
* Next, enter ```mkdir -p data``` to create a datapath for logs, metadata, and database.
* Next. create a ```.env``` file (just one key is enough):
  
  ```
  GROQ_API_KEY=...
  OPENROUTER_API_KEY=...
  TOGETHER_API_KEY=...
  
  LANGCHAIN_TRACING_V2=false # Optional - for tracing.
  LANGCHAIN_API_KEY=...
  LANGCHAIN_PROJECT=Aza Man_FOR_AAIDC2025
  ```
  
* Next, go into the ```project_config``` script and update Aza Man's configuration.

  ```PROJECT_CONFIG = {
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
    

  Update ```model```, ```evaluator```, and ```provider - groq, together, or openrouter```.

* Lastly, run ```streamlit run app.py```. Visit [http://localhost:8501/](http://localhost:8501/) to open the UI.

# Future Work
To enhance Aza Man, future iterations could include:

* Feature Expansion: Add tools for currency conversion, investment tracking, or debt management.
* Multi-User Support: Scale the SQLite database for concurrent users, leveraging Kubernetes for deployment.github.com
* Multimodal Capabilities: Integrate image processing (e.g., scanning receipts) using models like GPT-4o.analyticsvidhya.com
* Better Guardrails: Add safety checks to prevent erroneous financial calculations or data leaks.
* MCP: Standardize all tool integration via Model Context Protocol.
These enhancements would make Aza Man a more robust, enterprise-ready financial assistant.

# Conclusion
Aza Man, developed for Module 2 of the Agentic AI Developer Certification Program 2025, showcases the potential of AI agents to transform personal finance. Aza Man paves the way for future innovations in financial automation, aligning with the certification program’s mission to train developers in cutting-edge AI technologies.

[Link to project publication](https://app.readytensor.ai/publications/aza-man-JJ1fQYdl6gVE)

# Acknowledgments
The development of Aza Man was supported by the Ready Tensor Agentic AI Developer Certification Program.

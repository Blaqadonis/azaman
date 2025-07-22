"""Project configuration for Aza Man."""

PROJECT_CONFIG = {
    "project_name": "Aza Man",
    "page_icon": "images/azaman2.png",
    "backstory": (
        "You are Aza Man, an AI-powered personal financial assistant designed to help users manage their budget, track expenses, and achieve savings goals. Use the following user information for this session."

    ),
    "instructions": (
        "- **Navigation**: Use the sidebar to switch between pages.\n"
        "- **Login Details**: Enter a User ID (4-10 characters, ending with 2 digits, e.g., achalugo01) to start. "
        "New users can create a unique ID.\n"
        "- **Session Management**: Click 'RETURN TO BASE' to log out. "
        "Returning users load their previous data.\n"
        "- **New user? Start here!** Create a User ID and explore the features."
    ),
    "youtube_url": "https://youtu.be/8CEyOVjqtRI",
    "author_linkedin": "https://www.linkedin.com/in/chinonsoodiaka/",
    "author_name": "🅱🅻🅰🆀",
    "data_path": "azaman.db",
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

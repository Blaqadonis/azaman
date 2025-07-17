from dataclasses import dataclass, field
from typing import List, Dict, Any
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing import Annotated
from project_config import PROJECT_CONFIG

@dataclass(kw_only=True)
class State:
    """State class for Aza Man financial assistant."""
    messages: Annotated[List[AnyMessage], add_messages] = field(default_factory=list)
    username: str = PROJECT_CONFIG["state_defaults"]["username"]
    income: float = PROJECT_CONFIG["state_defaults"]["income"]
    budget_for_expenses: float = PROJECT_CONFIG["state_defaults"]["budget_for_expenses"]
    expense: float = PROJECT_CONFIG["state_defaults"]["expense"]
    expenses: List[Dict[str, Any]] = field(default_factory=lambda: PROJECT_CONFIG["state_defaults"]["expenses"])
    savings_goal: float = PROJECT_CONFIG["state_defaults"]["savings_goal"]
    savings: float = PROJECT_CONFIG["state_defaults"]["savings"]
    currency: str = PROJECT_CONFIG["state_defaults"]["currency"]
    summary: str = PROJECT_CONFIG["state_defaults"]["summary"]

    def __post_init__(self):
        """Ensure type consistency after initialization."""
        if not isinstance(self.messages, list):
            self.messages = PROJECT_CONFIG["state_defaults"]["messages"]
        if not isinstance(self.expenses, list):
            self.expenses = PROJECT_CONFIG["state_defaults"]["expenses"]
        if not isinstance(self.username, PROJECT_CONFIG["state_variables"]["username"]):
            self.username = PROJECT_CONFIG["state_defaults"]["username"]
        if not isinstance(self.income, PROJECT_CONFIG["state_variables"]["income"]):
            self.income = PROJECT_CONFIG["state_defaults"]["income"]
        if not isinstance(self.budget_for_expenses, PROJECT_CONFIG["state_variables"]["budget_for_expenses"]):
            self.budget_for_expenses = PROJECT_CONFIG["state_defaults"]["budget_for_expenses"]
        if not isinstance(self.expense, PROJECT_CONFIG["state_variables"]["expense"]):
            self.expense = PROJECT_CONFIG["state_defaults"]["expense"]
        if not isinstance(self.savings_goal, PROJECT_CONFIG["state_variables"]["savings_goal"]):
            self.savings_goal = PROJECT_CONFIG["state_defaults"]["savings_goal"]
        if not isinstance(self.savings, PROJECT_CONFIG["state_variables"]["savings"]):
            self.savings = PROJECT_CONFIG["state_defaults"]["savings"]
        if not isinstance(self.currency, PROJECT_CONFIG["state_variables"]["currency"]):
            self.currency = PROJECT_CONFIG["state_defaults"]["currency"]
        if not isinstance(self.summary, PROJECT_CONFIG["state_variables"]["summary"]):
            self.summary = PROJECT_CONFIG["state_defaults"]["summary"]
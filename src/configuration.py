from dataclasses import dataclass, field
from typing import Optional, Union
from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from langchain_groq import ChatGroq
from langchain_together import ChatTogether
from langchain_openai import ChatOpenAI
import os
import logging
from .prompts import SYSTEM_PROMPT
from .tools import ALL_TOOLS
from project_config import PROJECT_CONFIG

logger = logging.getLogger(__name__)

@dataclass(kw_only=True)
class Configuration:
    """Configuration class for the Aza Man financial assistant."""
    user_id: str = "default"
    thread_id: str = "default"
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default=PROJECT_CONFIG["model"],
        metadata={"description": "The name of the language model to use."}
    )
    provider: str = field(
        default=PROJECT_CONFIG["provider"],
        metadata={"description": "The LLM provider to use: 'groq', 'together', or 'openrouter'."}
    )
    system_prompt: str = SYSTEM_PROMPT

    def get_llm(self) -> Union[ChatGroq, ChatTogether, ChatOpenAI]:
        """Initialize and return the language model with bound tools based on the provider."""
        if "SSL_CERT_FILE" not in os.environ:
            os.environ["SSL_CERT_FILE"] = ""  # Fallback to avoid KeyError
        if self.provider.lower() == "groq":
            llm = ChatGroq(
                model=self.model,
                api_key=os.environ.get("GROQ_API_KEY")
            )
        elif self.provider.lower() == "together":
            llm = ChatTogether(
                model=self.model,
                api_key=os.environ.get("TOGETHER_API_KEY")
            )
        elif self.provider.lower() == "openrouter":
            llm = ChatOpenAI(
                model=self.model,
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                default_headers={
                    "X-Title": PROJECT_CONFIG["project_name"]
                }
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Use 'groq', 'together', or 'openrouter'.")
        return llm.bind_tools(ALL_TOOLS)

    def format_system_prompt(self, state) -> str:
        """Format the system prompt with current state values."""
        prompt = self.system_prompt
        format_args = {
            "username": state.username or "Unknown",
            "income": f"{state.income:.2f}" if state.income else "0.00",
            "budget_for_expenses": f"{state.budget_for_expenses:.2f}" if state.budget_for_expenses else "0.00",
            "expense": f"{state.expense:.2f}" if state.expense else "0.00",
            "expenses": str(state.expenses or []),
            "savings_goal": f"{state.savings_goal:.2f}" if state.savings_goal else "0.00",
            "savings": f"{state.savings:.2f}" if state.savings else "0.00",
            "currency": state.currency or PROJECT_CONFIG["currency_default"],
            "summary": state.summary or "No prior conversation summary available."
        }
        try:
            for key, value in format_args.items():
                prompt = prompt.replace(f"${key}", str(value))
            return prompt
        except Exception as e:
            logger.error(f"Prompt formatting failed: {str(e)}")
            return self.system_prompt

    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig or environment variables."""
        configurable = config["configurable"] if config and "configurable" in config else {}
        values = {
            "user_id": configurable.get("user_id", os.environ.get("USER_ID", "default")),
            "thread_id": configurable.get("thread_id", os.environ.get("THREAD_ID", "default")),
            "model": configurable.get("model", os.environ.get("MODEL", PROJECT_CONFIG["model"])),
            "provider": configurable.get("provider", os.environ.get("PROVIDER", PROJECT_CONFIG["provider"]))
        }
        return cls(**values)
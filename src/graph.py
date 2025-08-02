from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from .configuration import Configuration
from .tools import budget, log_expenses, math_tool, set_username
from .utils import split_model_and_provider
from .state import State
from project_config import PROJECT_CONFIG
import json
import logging

logger = logging.getLogger(__name__)

def call_model(current_state: State, config: RunnableConfig) -> dict:
    """Invoke the language model with the current state and system prompt.

    Args:
        current_state (State): The current conversation state.
        config (RunnableConfig): Configuration for the runtime.

    Returns:
        dict: A dictionary with the model's response in the "messages" key.
    """
    configurable = Configuration.from_runnable_config(config)
    llm = configurable.get_llm()
    sys_prompt = configurable.format_system_prompt(current_state)
    msg = llm.invoke(
        [{"role": "system", "content": sys_prompt}, *current_state.messages],
        {"configurable": split_model_and_provider(configurable.model)}
    )
    if not msg.tool_calls and msg.content:
        try:
            tool_call = json.loads(msg.content)
            if isinstance(tool_call, dict) and "name" in tool_call and "parameters" in tool_call:
                parameters = tool_call['parameters']
                if isinstance(parameters, str):
                    parameters = json.loads(parameters)
                msg.tool_calls = [{'name': tool_call['name'], 'args': parameters, 'id': 'manual_call'}]
                msg.content = ""
        except json.JSONDecodeError:
            pass
    return {"messages": [msg]}

def store_memory(current_state: State, config: RunnableConfig) -> dict:
    """Process tool calls and update the state accordingly.

    Args:
        current_state (State): The current conversation state.
        config (RunnableConfig): Configuration for the runtime.

    Returns:
        dict: Updated state fields based on tool outputs.
    """
    tool_calls = current_state.messages[-1].tool_calls
    if not tool_calls:
        return {"messages": []}

    results = []
    updates = {}
    current_expenses = current_state.expenses or []

    for tc in tool_calls:
        try:
            if tc["name"] == "budget":
                result = budget.invoke(tc["args"])
                updates["income"] = result["income"]
                updates["savings"] = result["savings"]
                updates["budget_for_expenses"] = result["budget_for_expenses"]
                updates["currency"] = result["currency"]
                updates["savings_goal"] = result["savings"]
                results.append(result["message"])
            elif tc["name"] == "log_expenses":
                args = tc["args"]
                if isinstance(args, str):
                    args = json.loads(args)
                result = log_expenses.invoke(args)
                updates["expense"] = result["expense"] + current_state.expense
                updates["expenses"] = current_expenses + result["expenses"]
                updates["currency"] = result["currency"]
                results.append(result["message"])
            elif tc["name"] == "math_tool":
                result = math_tool.invoke(tc["args"])
                results.append(str(result))
            elif tc["name"] == "set_username":
                result = set_username.invoke(tc["args"])
                updates["username"] = tc["args"]["username"]
                results.append(result["message"])
            else:
                results.append(f"Unknown tool: {tc['name']}")
        except Exception as e:
            results.append(f"Error in tool {tc['name']}: {str(e)}")

    tool_messages = [
        {"role": "tool", "content": str(result), "tool_call_id": tc["id"]}
        for tc, result in zip(tool_calls, results)
    ]
    updates["messages"] = tool_messages
    return updates

def summarize_conversation(current_state: State, config: RunnableConfig) -> dict:
    """Summarize the conversation if it exceeds a threshold.

    Args:
        current_state (State): The current conversation state.
        config (RunnableConfig): Configuration for the runtime.

    Returns:
        dict: A dictionary with the summary if applicable.
    """
    configurable = Configuration.from_runnable_config(config)
    llm = configurable.get_llm()
    if len(current_state.messages) > 10:
        summary_prompt = f"Summarize this conversation:\n{[msg.content for msg in current_state.messages]}"
        summary = llm.invoke(summary_prompt).content
        return {"summary": summary}
    return {}

def route_message(current_state: State) -> str:
    """Determine the next node based on the current message.

    Args:
        current_state (State): The current conversation state.

    Returns:
        str: The name of the next node or END.
    """
    msg = current_state.messages[-1]
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        return "store_memory"
    elif len(current_state.messages) > 10:
        return "summarize_conversation"
    return END

class CustomStateGraph(StateGraph):
    """Custom StateGraph with filtered state saving."""
    def stream(self, input, config=None, stream_mode="updates", **kwargs):
        for output in super().stream(input, config, stream_mode, **kwargs):
            yield output
        if self.checkpointer:
            current_state = self.get_state(config).values
            filtered_state = {k: v for k, v in current_state.items() if k != "messages" or v}
            filtered_state["messages"] = [{"content": msg.content} for msg in filtered_state.get("messages", [])]
            self.checkpointer.put(config, filtered_state)

def build_graph(checkpointer):
    """Build and return the LangGraph workflow.

    Args:
        checkpointer: The checkpointing mechanism for state persistence.

    Returns:
        CustomStateGraph: The compiled graph instance.
    """
    builder = CustomStateGraph(State, config_schema=Configuration)
    builder.add_node(call_model)
    builder.add_edge("__start__", "call_model")
    builder.add_node(store_memory)
    builder.add_node(summarize_conversation)
    builder.add_conditional_edges("call_model", route_message, ["store_memory", "summarize_conversation", END])
    builder.add_edge("store_memory", "call_model")
    builder.add_edge("summarize_conversation", END)
    graph = builder.compile(checkpointer=checkpointer)
    graph.name = PROJECT_CONFIG["project_name"]
    return graph
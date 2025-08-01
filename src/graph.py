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
    tool_calls = current_state.messages[-1].tool_calls
    if not tool_calls:
        return {"messages": []}

    results = []
    updates = {}
    current_expenses = current_state.expenses or []

    for tc in tool_calls:
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

    tool_messages = [
        {"role": "tool", "content": str(result), "tool_call_id": tc["id"]}
        for tc, result in zip(tool_calls, results)
    ]
    updates["messages"] = tool_messages
    return updates

def summarize_conversation(current_state: State, config: RunnableConfig) -> dict:
    configurable = Configuration.from_runnable_config(config)
    llm = configurable.get_llm()
    if len(current_state.messages) > 10:
        summary_prompt = f"Summarize this conversation:\n{[msg.content for msg in current_state.messages]}"
        summary = llm.invoke(summary_prompt).content
        return {"summary": summary}
    return {}

def route_message(current_state: State) -> str:
    msg = current_state.messages[-1]
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        return "store_memory"
    elif len(current_state.messages) > 10:
        return "summarize_conversation"
    return END

# filter messages to content only before saving
def filter_messages_to_content(state_dict):
    filtered_messages = [{"content": msg.content} for msg in state_dict["messages"]]
    state_dict["messages"] = filtered_messages
    return state_dict

# override state saving
class CustomStateGraph(StateGraph):
    def stream(self, input, config=None, stream_mode="updates", **kwargs):
        for output in super().stream(input, config, stream_mode, **kwargs):
            yield output
        if self.checkpointer:
            current_state = self.get_state(config).values
            filtered_state = filter_messages_to_content(current_state)
            self.checkpointer.put(config, filtered_state)

def build_graph(checkpointer):
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
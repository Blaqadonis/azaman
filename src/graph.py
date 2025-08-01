from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from .configuration import Configuration
from .tools import budget, log_expenses, math_tool, set_username
from .utils import split_model_and_provider
from .state import State
from project_config import PROJECT_CONFIG
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)

def filter_content(content: str) -> str:
    """Filter inappropriate content from LLM outputs."""
    inappropriate_keywords = ["inappropriate", "offensive", "hate", "violence"]  # Expand as needed
    if any(keyword in content.lower() for keyword in inappropriate_keywords):
        logger.warning(f"Inappropriate content detected: {content}")
        return "Warning: Inappropriate content detected. Please provide a financial-related request."
    return content

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.info(f"Retrying LLM call, attempt {retry_state.attempt_number}")
)
def call_model(current_state: State, config: RunnableConfig) -> dict:
    configurable = Configuration.from_runnable_config(config)
    llm = configurable.get_llm()
    sys_prompt = configurable.format_system_prompt(current_state)
    try:
        msg = llm.invoke(
            [{"role": "system", "content": sys_prompt}, *current_state.messages],
            {"configurable": split_model_and_provider(configurable.model)}
        )
        # Filter LLM output for safety
        if msg.content:
            msg.content = filter_content(msg.content)
        if not msg.tool_calls and msg.content:
            try:
                tool_call = json.loads(msg.content)
                if isinstance(tool_call, dict) and "name" in tool_call and "parameters" in tool_call:
                    parameters = tool_call['parameters']
                    if isinstance(parameters, str):
                        parameters = json.loads(parameters)
                    msg.tool_calls = [{'name': tool_call['name'], 'args': parameters, 'id': 'manual_call'}]
                    msg.content = ""
                else:
                    logger.debug(f"Invalid tool call format: {msg.content}")
            except json.JSONDecodeError:
                logger.debug(f"Non-JSON response: {msg.content}")
        # Convert AIMessage to dict for consistency
        message_dict = {
            "role": "assistant",
            "content": msg.content,
            "tool_calls": msg.tool_calls if msg.tool_calls else []
        }
        return {"messages": [message_dict]}
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        return {"messages": [{"role": "assistant", "content": f"Error: Failed to process request due to {str(e)}"}]}

def store_memory(current_state: State, config: RunnableConfig) -> dict:
    tool_calls = current_state.messages[-1].tool_calls
    if not tool_calls:
        logger.debug("No tool calls in message")
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
                logger.info(f"Successfully executed budget tool with args: {tc['args']}")
            elif tc["name"] == "log_expenses":
                args = tc["args"]
                if isinstance(args, str):
                    args = json.loads(args)
                result = log_expenses.invoke(args)
                updates["expense"] = result["expense"] + current_state.expense
                updates["expenses"] = current_expenses + result["expenses"]
                updates["currency"] = result["currency"]
                results.append(result["message"])
                logger.info(f"Successfully executed log_expenses tool with args: {tc['args']}")
            elif tc["name"] == "math_tool":
                result = math_tool.invoke(tc["args"])
                results.append(str(result))
                logger.info(f"Successfully executed math_tool with args: {tc['args']}")
            elif tc["name"] == "set_username":
                result = set_username.invoke(tc["args"])
                updates["username"] = tc["args"]["username"]
                results.append(result["message"])
                logger.info(f"Successfully executed set_username tool with args: {tc['args']}")
            else:
                logger.warning(f"Invalid tool call: {tc['name']}")
                results.append(f"Error: Invalid tool {tc['name']} requested")
        except Exception as e:
            error_msg = f"Error: Tool {tc['name']} failed with {str(e)}"
            logger.error(error_msg)
            results.append(error_msg)

    tool_messages = [
        {"role": "tool", "content": str(result), "tool_call_id": tc["id"]}
        for tc, result in zip(tool_calls, results)
    ]
    updates["messages"] = tool_messages
    return updates

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.info(f"Retrying summarization, attempt {retry_state.attempt_number}")
)
def summarize_conversation(current_state: State, config: RunnableConfig) -> dict:
    if not current_state.messages:
        logger.debug("No messages to summarize")
        return {"summary": "No conversation to summarize"}
    
    configurable = Configuration.from_runnable_config(config)
    llm = configurable.get_llm()
    if len(current_state.messages) > 10:
        summary_prompt = f"Summarize this conversation:\n{[msg.content for msg in current_state.messages]}"
        summary = llm.invoke(summary_prompt).content
        summary = filter_content(summary)
        logger.info("Conversation summarized")
        return {"summary": summary}
    logger.debug("Conversation too short to summarize")
    return {"summary": "No conversation to summarize"}

def route_message(current_state: State) -> str:
    if not current_state.messages:
        logger.debug("Empty message list, routing to END")
        return END
    msg = current_state.messages[-1]
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        logger.debug(f"Routing to store_memory for tool call: {msg.tool_calls}")
        return "store_memory"
    elif len(current_state.messages) > 10:
        logger.debug("Routing to summarize_conversation for long conversation")
        return "summarize_conversation"
    logger.debug("Routing to END for regular message")
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
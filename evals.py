import os
import csv
import sys
import sqlite3
from dotenv import load_dotenv
from langchain_together import ChatTogether
from openevals.llm import create_llm_as_judge
from langgraph.checkpoint.sqlite import SqliteSaver
from src.graph import build_graph
from project_config import PROJECT_CONFIG

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

os.environ["PYTHONIOENCODING"] = "utf-8"

FINANCE_EVAL_PROMPT = """
You are an evaluator for a financial assistant system, Aza Man, designed to help users manage budgets, track expenses, and achieve savings goals. Compare the provided output to the expected output and determine if the response is correct and relevant to the financial query.

Input: {inputs}
Output: {outputs}
Expected Output: {reference_outputs}

Return a JSON object with the following keys:
- score: A boolean (True if the output is correct or sufficiently accurate, False otherwise).
- reasoning: A string explaining why the score was assigned.

Ensure the output is factually accurate, relevant to the financial query, and aligns with Aza Man’s functionality (e.g., setting usernames, budgets, expenses, or savings goals). If the output and expected output differ but both are factually correct and contextually appropriate, consider the conversational flow and user intent to assign the score.
"""

conn = sqlite3.connect(PROJECT_CONFIG["data_path"], check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = build_graph(checkpointer=checkpointer)

evaluator = create_llm_as_judge(
    prompt=FINANCE_EVAL_PROMPT,
    judge=ChatTogether(
        model=PROJECT_CONFIG["evaluator"],
        api_key=os.getenv("TOGETHER_API_KEY"),
    ),
    feedback_key="finance_correctness",
)

def safe_print(text):
    return text.replace('\u20a6', 'NGN')

def load_test_cases_from_csv(csv_file="data/finance_eval_dataset.csv"):
    test_cases = []
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_cases.append({"inputs": row["Input"], "outputs": row["Output"]})
        return test_cases
    except FileNotFoundError:
        print(f"Error: {csv_file} not found in the data folder.")
        return []
    except Exception as e:
        print(f"Error loading test cases: {e}")
        return []

def evaluate_finance():
    print(f"Running {PROJECT_CONFIG['project_name']} Financial Evaluations with Test Cases from CSV...\n")
    test_cases = load_test_cases_from_csv()
    if not test_cases:
        print("No test cases loaded. Exiting.")
        return
    
    results = []
    conversation_history = []
    state = {"messages": [], "summary": ""}
    config = {"configurable": {"user_id": "testuser01", "thread_id": "eval_thread"}}
    
    for i, test in enumerate(test_cases, 1):
        conversation_history.append(test["inputs"])
        full_inputs = "\n".join(conversation_history)
        state["messages"].append({"role": "user", "content": test["inputs"]})
        output_state = graph.invoke(state, config)
        output = output_state["messages"][-1].content if output_state["messages"] else "No response generated."
        
        print(f"Test {i}:")
        print(f"Input: {test['inputs']}")
        print(f"Output: {safe_print(output)}")
        print(f"Expected: {safe_print(test['outputs'])}")
        try:
            eval_result = evaluator(inputs=full_inputs, outputs=output, reference_outputs=test['outputs'])
            score = eval_result.get('score', 'N/A')
            comment = eval_result.get('comment', 'Evaluation failed')
            print(f"Score: {score}")
            print(f"Comment: {comment}")
        except Exception as e:
            print(f"Evaluator error: {e}")
            score = 'N/A'
            comment = f"Evaluation failed: {str(e)}"
        print("-" * 50)
        
        results.append({
            "Test Number": i,
            "Input": test["inputs"],
            "Output": output,
            "Expected": test["outputs"],
            "Score": score,
            "Comment": comment
        })
        
        conversation_history.append(output)
        state["messages"].append({"role": "assistant", "content": output})
        if "summary" in output_state:
            state["summary"] = output_state["summary"]

    csv_file = "finance_eval_results.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Test Number", "Input", "Output", "Expected", "Score", "Comment"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Evaluation results saved to {csv_file}")

if __name__ == "__main__":
    evaluate_finance()
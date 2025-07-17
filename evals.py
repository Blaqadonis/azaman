"""Evaluation tests for the Aza Man financial assistant.

This module implements automated evaluation tests for the Aza Man application,
using a CSV dataset to validate system responses against expected outputs. It
uses the LangGraph workflow to process inputs, an OpenEvals LLM judge to score
responses, and SQLite for checkpointing state. Results are saved to a CSV file
for analysis.

Dependencies:
    - pytest==8.4.1
    - langchain-together==0.3.0 (ChatTogether)
    - openevals==0.1.0 (create_llm_as_judge)
    - langgraph-checkpoint-sqlite==2.0.10 (SqliteSaver)
    - python-dotenv==1.1.0 (load_dotenv)
    - src.graph (build_graph)
    - project_config (PROJECT_CONFIG)
    - sqlite3 (standard library)
    - csv (standard library)

The script ensures production-grade evaluation by handling special characters,
managing conversation state, and providing detailed error reporting.
"""

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

# root folder 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables 
load_dotenv()

os.environ["PYTHONIOENCODING"] = "utf-8" 

# Define Finance Evaluation Prompt
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

# Initialize Aza Man system
conn = sqlite3.connect(PROJECT_CONFIG["data_path"], check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = build_graph(checkpointer=checkpointer)

# Initialize OpenEvals evaluator
evaluator = create_llm_as_judge(
    prompt=FINANCE_EVAL_PROMPT,
    judge=ChatTogether(
        model=PROJECT_CONFIG["evaluator"],
        api_key=os.getenv("TOGETHER_API_KEY"),
    ),
    feedback_key="finance_correctness",
)


def safe_print(text):
    """Replace problematic characters (e.g., ₦) with safe alternatives for console output.

    Args:
        text (str): Input text containing potentially problematic characters.

    Returns:
        str: Text with special characters (e.g., ₦) replaced with safe alternatives
            (e.g., 'NGN').
    """
    # Replace the Naira symbol with 'NGN' for console compatibility
    return text.replace('\u20a6', 'NGN')


def load_test_cases_from_csv(csv_file="data/finance_eval_dataset.csv"):
    """Load test cases from a CSV file located in the data folder.

    Reads test cases from a CSV file containing input and expected output columns,
    handling file not found and other errors gracefully.

    Args:
        csv_file (str): Path to the CSV file (default: 'data/finance_eval_dataset.csv').

    Returns:
        list: List of dictionaries containing 'inputs' and 'outputs' for each test case.
        Empty list if the file is not found or an error occurs.
    """
    test_cases = []
    try:
        # Open and read the CSV file with UTF-8 encoding
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Append each test case as a dictionary
                test_cases.append({
                    "inputs": row["Input"],
                    "outputs": row["Output"]
                })
        return test_cases
    except FileNotFoundError:
        # Handle missing CSV file
        print(f"Error: {csv_file} not found in the data folder.")
        return []
    except Exception as e:
        # Handle other CSV reading errors
        print(f"Error loading test cases: {e}")
        return []


def evaluate_finance():
    """Run financial evaluations using test cases from a CSV file.

    Executes the Aza Man LangGraph workflow on test inputs, evaluates outputs using
    an OpenEvals LLM judge, and saves results to a CSV file. Maintains conversation
    history and state for context-aware evaluations.

    Saves results to 'finance_eval_results.csv' with test number, input, output,
    expected output, score, and comment.
    """
    # Print evaluation start message
    print(f"Running {PROJECT_CONFIG['project_name']} Financial Evaluations with Test Cases from CSV...\n")
    
    # Load test cases from CSV
    test_cases = load_test_cases_from_csv()
    if not test_cases:
        # Exit if no test cases are loaded
        print("No test cases loaded. Exiting.")
        return
    
    results = []
    conversation_history = []
    # Initialize state for evaluation
    state = {"messages": [], "summary": ""}
    config = {"configurable": {"user_id": "testuser01", "thread_id": "eval_thread"}}
    
    for i, test in enumerate(test_cases, 1):
        # Append input to conversation history
        conversation_history.append(test["inputs"])
        full_inputs = "\n".join(conversation_history)
        
        # Add user input to state
        state["messages"].append({"role": "user", "content": test["inputs"]})
        # Invoke the LangGraph workflow
        output_state = graph.invoke(state, config)
        # Extract the latest output message
        output = output_state["messages"][-1].content if output_state["messages"] else "No response generated."
        
        # Print test case details
        print(f"Test {i}:")
        print(f"Input: {test['inputs']}")
        print(f"Output: {safe_print(output)}")
        print(f"Expected: {safe_print(test['outputs'])}")
        try:
            # Evaluate the output using the OpenEvals judge
            eval_result = evaluator(
                inputs=full_inputs,
                outputs=output,
                reference_outputs=test['outputs']
            )
            score = eval_result.get('score', 'N/A')
            comment = eval_result.get('comment', 'Evaluation failed')
            print(f"Score: {score}")
            print(f"Comment: {comment}")
        except Exception as e:
            # Handle evaluation errors
            print(f"Evaluator error: {e}")
            score = 'N/A'
            comment = f"Evaluation failed: {str(e)}"
        print("-" * 50)
        
        # Append results for CSV output
        results.append({
            "Test Number": i,
            "Input": test["inputs"],
            "Output": output,
            "Expected": test["outputs"],
            "Score": score,
            "Comment": comment
        })
        
        # Update conversation history and state
        conversation_history.append(output)
        state["messages"].append({"role": "assistant", "content": output})
        if "summary" in output_state:
            state["summary"] = output_state["summary"]

    # Save evaluation results to CSV
    csv_file = "finance_eval_results.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Test Number", "Input", "Output", "Expected", "Score", "Comment"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Evaluation results saved to {csv_file}")


if __name__ == "__main__":
    evaluate_finance()
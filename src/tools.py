from langchain_core.tools import tool
from typing import Union, List, Dict, Any
from project_config import PROJECT_CONFIG

ALL_TOOLS = []

@tool
def budget(income: float, savings_goal: Union[str, float], currency: str = PROJECT_CONFIG["currency_default"]) -> Dict[str, Any]:
    """Allocate a budget based on the user's income and savings goal.

    This tool calculates the savings and budget for expenses based on the provided income
    and savings goal, which can be a fixed amount or a percentage of income. The result
    includes the income, savings, budget for expenses, currency, and a formatted message.

    Args:
        income (float): The user's total income.
        savings_goal (Union[str, float]): The desired savings amount, either as a number
            or a percentage string (e.g., "40%").
        currency (str): The currency code (e.g., "NGN"). Defaults to project config.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - income (float): The provided income.
            - savings (float): The calculated savings amount.
            - budget_for_expenses (float): The remaining amount for expenses.
            - currency (str): The provided currency code.
            - message (str): A formatted confirmation message.
    """
    if isinstance(savings_goal, str) and "%" in savings_goal:
        savings_goal = float(savings_goal.strip("%")) / 100 * income
    else:
        savings_goal = float(savings_goal)
    savings = savings_goal
    budget_for_expenses = income - savings
    return {
        "income": income,
        "savings": savings,
        "budget_for_expenses": budget_for_expenses,
        "currency": currency,
        "message": f"Budget created! Income: {income:,.2f} {currency}, Savings: {savings:,.2f} {currency}, Expenses: {budget_for_expenses:,.2f} {currency}"
    }

ALL_TOOLS.append(budget)

@tool
def log_expenses(expenses: List[Dict[str, Any]], currency: str = PROJECT_CONFIG["currency_default"]) -> Dict[str, Any]:
    """Log user expenses and calculate the total.

    This tool processes a list of expense entries, each containing an amount and category,
    and calculates the total expense. The result includes the total expense, the list of
    expenses, the currency, and a formatted message.

    Args:
        expenses (List[Dict[str, Any]]): A list of dictionaries, each with "amount" (float)
            and "category" (str) keys representing an expense.
        currency (str): The currency code (e.g., "NGN"). Defaults to project config.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - expense (float): The total sum of expense amounts.
            - expenses (List[Dict[str, Any]]): The provided list of expenses.
            - currency (str): The provided currency code.
            - message (str): A formatted confirmation message.
    """
    total_expense = sum(expense["amount"] for expense in expenses)
    return {
        "expense": total_expense,
        "expenses": expenses,
        "currency": currency,
        "message": f"Expenses logged! Total: {total_expense:,.2f} {currency}"
    }

ALL_TOOLS.append(log_expenses)

@tool
def math_tool(numbers: List[float], operation: str) -> float:
    """Perform a mathematical operation on a list of numbers.

    This tool executes the specified mathematical operation (add, subtract, multiply, or
    divide) on a list of numbers. At least one number is required for addition or
    multiplication, and at least two numbers are required for subtraction or division.

    Args:
        numbers (List[float]): A list of numbers to operate on.
        operation (str): The mathematical operation to perform ("add", "subtract",
            "multiply", or "divide").

    Returns:
        float: The result of the mathematical operation.

    Raises:
        ValueError: If no numbers are provided, if subtract or divide operations have
            fewer than two numbers, if division by zero is attempted, or if an unsupported
            operation is specified.
    """
    if not numbers:
        raise ValueError("At least one number required.")
    if operation == "add":
        return sum(numbers)
    if operation == "subtract":
        if len(numbers) < 2:
            raise ValueError("Subtract needs two numbers.")
        result = numbers[0]
        for num in numbers[1:]:
            result -= num
        return result
    if operation == "multiply":
        result = 1.0
        for num in numbers:
            result *= num
        return result
    if operation == "divide":
        if len(numbers) < 2:
            raise ValueError("Divide needs two numbers.")
        result = numbers[0]
        for num in numbers[1:]:
            if num == 0:
                raise ValueError("Division by zero.")
            result /= num
        return result
    raise ValueError(f"Unsupported operation: {operation}.")

ALL_TOOLS.append(math_tool)

@tool
def set_username(username: str) -> Dict[str, Any]:
    """Set the user's username.

    This tool stores the provided username and returns a confirmation message.

    Args:
        username (str): The username to set.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - username (str): The provided username.
            - message (str): A confirmation message indicating the username was set.
    """
    return {"username": username, "message": f"Username set to {username}"}

ALL_TOOLS.append(set_username)
from langchain_core.tools import tool
from typing import Union, List, Dict, Any
from project_config import PROJECT_CONFIG

ALL_TOOLS = []

@tool
def budget(income: float, savings_goal: Union[str, float], currency: str = PROJECT_CONFIG["currency_default"]) -> Dict[str, Any]:
    """Allocate a budget based on the user's income and savings goal.

    Args:
        income (float): The user's total income. Must be positive.
        savings_goal (Union[str, float]): The desired savings amount, either as a number
            or a percentage string (e.g., "40%").
        currency (str): The currency code (e.g., "NGN"). Defaults to project config.

    Returns:
        Dict[str, Any]: A dictionary containing income, savings, budget_for_expenses,
            currency, and a message.

    Raises:
        ValueError: If income is not positive, savings_goal is invalid, or savings exceed income.
    """
    if income <= 0:
        raise ValueError("Income must be positive.")
    if isinstance(savings_goal, str):
        if not savings_goal.endswith("%"):
            raise ValueError("Savings goal percentage must end with '%'.")
        try:
            savings_percentage = float(savings_goal.strip("%")) / 100
            if savings_percentage < 0 or savings_percentage > 1:
                raise ValueError("Savings goal percentage must be between 0% and 100%.")
            savings = savings_percentage * income
        except ValueError:
            raise ValueError("Invalid savings goal percentage.")
    else:
        savings = float(savings_goal)
        if savings < 0:
            raise ValueError("Savings goal must be non-negative.")
    if savings > income:
        raise ValueError("Savings goal cannot exceed income.")
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

    Args:
        expenses (List[Dict[str, Any]]): List of dictionaries with "amount" (float) and
            "category" (str) keys. Amounts must be positive.
        currency (str): The currency code (e.g., "NGN"). Defaults to project config.

    Returns:
        Dict[str, Any]: A dictionary containing expense total, expenses list, currency,
            and a message.

    Raises:
        ValueError: If any expense amount is not positive or if the list is empty.
    """
    if not expenses:
        raise ValueError("At least one expense must be provided.")
    total_expense = 0.0
    for expense in expenses:
        amount = expense.get("amount")
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Expense amount must be a positive number.")
        total_expense += amount
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

    Args:
        numbers (List[float]): List of numbers to operate on.
        operation (str): Operation to perform ("add", "subtract", "multiply", "divide").

    Returns:
        float: Result of the mathematical operation.

    Raises:
        ValueError: If arguments are insufficient, division by zero occurs, or operation is unsupported.
    """
    if not numbers:
        raise ValueError("At least one number is required.")
    if operation in ["subtract", "divide"] and len(numbers) < 2:
        raise ValueError(f"{operation.capitalize()} requires at least two numbers.")
    if operation == "add":
        return sum(numbers)
    elif operation == "subtract":
        result = numbers[0]
        for num in numbers[1:]:
            result -= num
        return result
    elif operation == "multiply":
        result = 1.0
        for num in numbers:
            result *= num
        return result
    elif operation == "divide":
        result = numbers[0]
        for num in numbers[1:]:
            if num == 0:
                raise ValueError("Division by zero.")
            result /= num
        return result
    else:
        raise ValueError(f"Unsupported operation: {operation}.")

ALL_TOOLS.append(math_tool)

@tool
def set_username(username: str) -> Dict[str, Any]:
    """Set the user's username.

    Args:
        username (str): The username to set. Must not be empty.

    Returns:
        Dict[str, Any]: A dictionary containing the username and a confirmation message.

    Raises:
        ValueError: If the username is empty.
    """
    if not username.strip():
        raise ValueError("Username cannot be empty.")
    return {"username": username, "message": f"Username set to {username}"}

ALL_TOOLS.append(set_username)
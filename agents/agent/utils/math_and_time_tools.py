import math
import datetime
from typing import Optional
import dateparser

def format_to_datetime(timestamp = None) -> Optional[datetime.datetime]:
    """
    Parses a timestamp and formats it to a datetime object using dateparser.

    Args:
        timestamp: date/time expression.

    Returns:
        datetime.datetime | None: Parsed datetime object, or None if parsing fails.
    """

    if timestamp is None:
        return None

    parsed_timestamp = dateparser.parse(timestamp)
    if parsed_timestamp is None:
        return None

    return parsed_timestamp

def math_tool(expression: str) -> float:

    """
    Safely evaluates a mathematical expression using Python.
    Only allows: numbers, + - * / **, parentheses, and math module functions.
    """

    #   Allow math functions
    allowed_math_functions = {
        name: value
        for name, value in math.__dict__.items()
        if not name.startswith("__")
    }

    #   Block Python built-in functions
    blocked_builtins = {"__builtins__": {}}

    #   Evaluate expression, blocking builtins
    result = eval(expression, blocked_builtins, allowed_math_functions)

    return float(result)
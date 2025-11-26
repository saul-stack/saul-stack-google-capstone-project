import math
import datetime
from typing import Optional, Any, TypedDict
import dateparser

## Class Definitions
class DateTimeDict(TypedDict):
    timestamp: datetime.datetime
    status: str
    time_iso: str
    timezone: str
    day_number: str
    day_name: str
    month_name: str
    year: str

## Validators
def is_datetime_object(x: Any) -> bool:
    """
    Check if the given value is a datetime.datetime object.

    Args:
        x: Any Python variable or object.

    Returns:
        bool: True if value is a datetime.datetime object, False otherwise.
    """
    return isinstance(x, datetime.datetime)

## Formatters
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

def format_to_datetime_dict(timestamp: datetime.datetime) -> DateTimeDict:
    """
    Converts a datetime object into a structured dictionary of relvant fields.
    """

    return {
        "timestamp": timestamp,
        "time_iso": timestamp.isoformat(),
        "day_number": str(timestamp.day),
        "day_name": timestamp.strftime("%A"),
        "month_name": timestamp.strftime("%B"),
        "year": str(timestamp.year),
        "timezone": str(timestamp.tzinfo),
    }

## Other Utilities
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
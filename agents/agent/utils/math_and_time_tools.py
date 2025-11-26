import math
import datetime
from typing import Optional, Any, TypedDict, Literal, NotRequired
import dateparser
import isodate

## Class Definitions
class ToolResult(TypedDict):
    status: Literal["success", "error"]
    message: NotRequired[str]
    body: NotRequired[Any]

class DateTimeDict(TypedDict):
    timestamp: datetime.datetime
    time_google_calendar: str
    time_iso: str
    timezone: str
    day_number: str
    day_name: str
    month_name: str
    year: str

## Agent Tools
def get_current_date_and_time(utc: bool = False) -> DateTimeDict:
    """
    Get the current day name, date and time with detailed metadata.

    Returns a structured dictionary containing:
    - The original timestamp as a datetime object
    - ISO 8601 formatted string
    - Timezone
    - Day and year numbers
    - Human-readable day and month names

    Args:
        utc (bool): If True, returns the current UTC time. 
                    If False (default), returns the local timezone time.

    Returns:
        DateTimeDict: Structured dictionary with datetime metadata.
    """

    now = datetime.datetime.now(datetime.timezone.utc) if utc else datetime.datetime.now().astimezone()
    result = format_to_datetime_dict(now)
    return result

def get_relative_date_and_time(base_timestamp: Optional[str] = None, delta: str = None) -> DateTimeDict:
    """
    Calculate a date/time given a time delta relative to an optional base timestamp. Base timestamp defaults to current time if not provided
    Supports ISO 8601 durations (e.g., 'P1D', 'PT2H', 'P-1D') and natural language deltas.
    """

    if delta is None:
        raise ValueError("No time delta provided")

    # Determine base datetime
    if base_timestamp is None:
        base_timestamp = get_current_date_and_time()["timestamp"]
        if isinstance(base_timestamp, str):
            base_timestamp = dateparser.parse(base_timestamp)
            if base_timestamp is None:
                raise ValueError(f"Could not parse timestamp from get_current_date_and_time(): {base_timestamp}")
    else:
        if not isinstance(base_timestamp, datetime.datetime):
            base_timestamp = dateparser.parse(base_timestamp)
            if base_timestamp is None:
                raise ValueError(f"Could not parse base timestamp: {base_timestamp}")

    if base_timestamp.tzinfo is None:
        base_timestamp = base_timestamp.replace(tzinfo=datetime.timezone.utc)

    # if iso_8601 time delta
    if delta.startswith("P") or delta.startswith("p"):
        try:
            duration = parse_iso_duration(delta)
            relative_timestamp = base_timestamp + duration
        except Exception:
            raise ValueError(f"Could not parse ISO 8601 duration: {delta}")
    else:
        relative_timestamp = dateparser.parse(delta, settings={"RELATIVE_BASE": base_timestamp})
        if relative_timestamp is None:
            raise ValueError(f"Could not parse delta: {delta}")

    return format_to_datetime_dict(relative_timestamp)

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

## Formatters/parsers
def format_time_to_calendar(timestamp:str = None) -> str:

    if timestamp is None:
        return None

    parsed_timestamp = dateparser.parse(timestamp)
    if parsed_timestamp is None:
        return None

    if parsed_timestamp.tzinfo is None:
        parsed_timestamp = parsed_timestamp.replace(tzinfo=datetime.timezone.utc)

    parsed_timestamp = parsed_timestamp.isoformat(timespec="microseconds").replace("+00:00", "Z")

    return parsed_timestamp

def format_to_datetime_dict(timestamp: datetime.datetime) -> DateTimeDict:
    """
    Converts a datetime object into a structured dictionary of relevant fields.
    """

    return {
        "timestamp": timestamp,
        "time_google_calendar": format_time_to_calendar(timestamp.isoformat()),
        "time_iso": timestamp.isoformat(),
        "day_number": str(timestamp.day),
        "day_name": timestamp.strftime("%A"),
        "month_name": timestamp.strftime("%B"),
        "year": str(timestamp.year),
        "timezone": str(timestamp.tzinfo),
    }

def parse_iso_duration(time_delta: str) -> datetime.timedelta:
    """
    Parse an ISO 8601 duration string including a negative duration (e.g. P-1D).
    Returns a datetime.timedelta.
    """
    if not time_delta or not (time_delta.startswith("P") or time_delta.startswith("p")):
        raise ValueError("Not an ISO 8601 duration")

    delta_is_negative = False

    if len(time_delta) > 1 and time_delta[1] == "-":
        delta_is_negative = True
        time_delta = "P" + time_delta[2:]

    duration = isodate.parse_duration(time_delta)

    if not isinstance(duration, datetime.timedelta):
        duration = datetime.timedelta(
            days=duration.days,
            seconds=duration.totalseconds() % 86400
        )

    if delta_is_negative:
        duration = -duration

    return duration

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
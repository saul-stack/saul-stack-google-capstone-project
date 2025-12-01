import math
import datetime
from typing import Optional, Any, TypedDict, Literal, NotRequired, Dict
import dateparser
import isodate

TIME_OF_DAY_RULES = {
    "early morning": (3, 0),
    "mid-morning": (10, 0),
    "morning": (8, 0),
    "early afternoon": (13, 0),
    "afternoon": (15, 0),
    "evening": (18, 0),
    "night": (21, 0),
}

TIME_KEYWORDS = sorted(TIME_OF_DAY_RULES.keys(), key=len, reverse=True)

def extract_date_and_time_phrase(delta: str):
    """
    Split a natural language delta into:
    - a date phrase ("tomorrow", "next Tuesday")
    - a time-of-day phrase ("morning", "evening")
    """
    text = delta.lower()

    for key in TIME_KEYWORDS:
        if key in text:
            date_part = text.replace(key, "").strip()
            return date_part, key

    return text, None

def apply_time_of_day(dt: datetime.datetime, tod_key: str) -> datetime.datetime:
    """Assign the configured hour/min for the matched time-of-day descriptor."""
    if tod_key is None:
        return dt

    hour, minute = TIME_OF_DAY_RULES[tod_key]
    return dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

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

def get_current_date_and_time(utc: bool = False) -> DateTimeDict:
    """
    Get the current time with structured fields.
    """
    now = datetime.datetime.now(datetime.timezone.utc) if utc else datetime.datetime.now().astimezone()
    return format_to_datetime_dict(now)

def get_relative_date_and_time(base_timestamp: Optional[str] = None, delta: str = None) -> Dict:
    """
    Parse a natural-language or ISO-8601 time delta into a concrete datetime.

    --------------------------------------------------------------
    IMPORTANT INSTRUCTIONS FOR THE AGENT
    --------------------------------------------------------------

    1. If the delta **already contains its own date anchor**, such as:
           "tomorrow", 
           "next Tuesday",
           "this Friday evening",
           "in 3 hours",
       then **DO NOT pass a base_timestamp**.
       Dateparser will correctly interpret these relative expressions
       using the current moment.

    2. If the delta **does NOT contain a date anchor**, such as:
           "afternoon",
           "evening",
           "morning",
           "at 4pm",
       then you MUST pass a base_timestamp so the function can apply
       the time to the correct existing day.

    3. Time-of-day descriptors (morning, evening, etc.) are applied by
       *custom rules*, NOT by dateparser. The module automatically:
           - extracts the date portion ("tomorrow")
           - extracts the time descriptor ("morning")
           - parses date portion normally
           - assigns time using TIME_OF_DAY_RULES

    --------------------------------------------------------------

    Parameters
    ----------
    base_timestamp : datetime or str or None
        A reference timestamp ONLY for deltas without their own date anchor.
        If None is provided for such deltas, the system uses current time.

    delta : str
        Natural-language or ISO-8601 duration.

    Returns
    -------
    dict
        Structured DateTimeDict
    """

    if delta is None:
        raise ValueError("No time delta provided")

    delta_lower = delta.lower()
    if delta_lower.startswith("p"):
        duration = parse_iso_duration(delta)

        if base_timestamp is None:
            base_dt = datetime.datetime.now(datetime.timezone.utc)
        else:
            base_dt = (
                dateparser.parse(base_timestamp)
                if isinstance(base_timestamp, str)
                else base_timestamp
            )

        if base_dt.tzinfo is None:
            base_dt = base_dt.replace(tzinfo=datetime.timezone.utc)

        return format_to_datetime_dict(base_dt + duration)

    date_phrase, tod_phrase = extract_date_and_time_phrase(delta)

    has_self_anchor = any(
        kw in delta_lower
        for kw in [
            "tomorrow", "yesterday", "today",
            "next", "last",
            "tonight", "this",
            "in ",         # "in 3 hours"
            "from now",
        ]
    )

    if date_phrase.strip() == "" and not has_self_anchor:
        if base_timestamp is None:
            base_dt = datetime.datetime.now(datetime.timezone.utc)
        else:
            base_dt = dateparser.parse(base_timestamp) if isinstance(base_timestamp, str) else base_timestamp

        if base_dt is None or not isinstance(base_dt, datetime.datetime):
            raise ValueError("base_timestamp must be datetime or parseable string")

        if base_dt.tzinfo is None:
            base_dt = base_dt.replace(tzinfo=datetime.timezone.utc)

        parsed_dt = base_dt

    elif has_self_anchor:
        parsed_dt = dateparser.parse(date_phrase)

    else:
        if base_timestamp is not None:
            base_dt = (
                dateparser.parse(base_timestamp)
                if isinstance(base_timestamp, str)
                else base_timestamp
            )
            if base_dt.tzinfo is None:
                base_dt = base_dt.replace(tzinfo=datetime.timezone.utc)

            parsed_dt = dateparser.parse(
                date_phrase,
                settings={"RELATIVE_BASE": base_dt},
            )
        else:
            parsed_dt = dateparser.parse(date_phrase)

    if parsed_dt is None:
        raise ValueError(f"Could not parse date portion: '{date_phrase}'")

    parsed_dt = apply_time_of_day(parsed_dt, tod_phrase)

    if parsed_dt.tzinfo is None:
        parsed_dt = parsed_dt.replace(tzinfo=datetime.timezone.utc)

    return format_to_datetime_dict(parsed_dt)

def is_datetime_object(x: Any) -> bool:
    return isinstance(x, datetime.datetime)

def format_time_to_calendar(timestamp: str) -> str:
    if timestamp is None:
        return None

    parsed_timestamp = dateparser.parse(timestamp)
    if parsed_timestamp is None:
        return None

    if parsed_timestamp.tzinfo is None:
        parsed_timestamp = parsed_timestamp.replace(tzinfo=datetime.timezone.utc)

    return parsed_timestamp.isoformat(timespec="microseconds").replace("+00:00", "Z")


def format_to_datetime_dict(timestamp: datetime.datetime) -> DateTimeDict:
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
    if not time_delta or not (time_delta.startswith("P") or time_delta.startswith("p")):
        raise ValueError("Not an ISO 8601 duration")

    delta_is_negative = False

    if len(time_delta) > 1 and time_delta[1] == "-":
        delta_is_negative = True
        time_delta = "P" + time_delta[2:]

    duration = isodate.parse_duration(time_delta)

    if not isinstance(duration, datetime.timedelta):
        duration = datetime.timedelta(days=duration.days, seconds=duration.totalseconds() % 86400)

    return -duration if delta_is_negative else duration

def math_tool(expression: str) -> float:
    allowed_math_functions = {name: value for name, value in math.__dict__.items() if not name.startswith("__")}
    blocked_builtins = {"__builtins__": {}}
    return float(eval(expression, blocked_builtins, allowed_math_functions))


def calculate_time_duration_hours(event: dict):
    try:
        start_str = event["start"]["dateTime"]
        end_str = event["end"]["dateTime"]
    except (KeyError, TypeError):
        return None

    try:
        start_dt = datetime.datetime.fromisoformat(start_str)
        end_dt = datetime.datetime.fromisoformat(end_str)
    except ValueError:
        return None

    return (end_dt - start_dt).total_seconds() / 3600.0


def get_local_timezone() -> str:
    return datetime.datetime.now().astimezone().tzname() or "UTC"
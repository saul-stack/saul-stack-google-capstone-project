from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .utils.math_and_time_tools import (
    math_tool, get_current_date_and_time, get_relative_date_and_time,
    format_time_to_calendar, calculate_time_duration_hours
)
from .utils.calendar_tools import get_events, schedule_new_event, cancel_event

get_events_tool = FunctionTool(get_events)
schedule_new_event_tool = FunctionTool(schedule_new_event)
cancel_event = FunctionTool(cancel_event)

math_tool = FunctionTool(math_tool)

math_and_time_utility_agent = Agent(
    name="math_and_time_utility_agent",
    description="Handles date/time calculations and math operations.",
    instruction=(
        "If unable to complete a task, return to the calender_interaction_team. "
        "Never respond directly to the user. Only call tools. "
        "Once an instruction is complete, pass the results as structured JSON to the calender_interaction_team. "
        "Use get_current_date_and_time for today, get_relative_date_and_time for relative times, "
        "calculate_time_duration_hours for durations, and format_time_to_calendar for time deltas. "
        "For natural language deltas (e.g., 'in 3 hours', 'next Tuesday'), first get current time, "
        "then resolve relative time using get_relative_date_and_time. "
        "Weekday names without dates refer to the next occurrence after today "
        "(e.g., 'Friday' after Monday 24 Nov 2025 → Friday 28 Nov 2025)."
    ),
    tools=[
        get_current_date_and_time, get_relative_date_and_time,
        math_tool, calculate_time_duration_hours, format_time_to_calendar
    ]
)

calendar_interaction_agent = Agent(
    name="calendar_interaction_agent",
    description=(
        "Interact with the user's calendar. "
    ),
    instruction=(
        "Invoke get_events to fetch events from the calendar. "
        "Invoke schedule_new_event to add an event to the calendar. " 

        "When invoking tools, values which you are not provided may be optional. In this case, invoke the tool without requesting these missing values from the user. "

        "When the user asks you to schedule an event on a named day, without giving an explicit date, the user is referring to the first instance of that named day, AFTER the current date. "
        "For example: 'schedule it on Friday' - if today is Monday 24th, you must schedule it on Friday 28th "

        "To get any day/date, including the current day/date, or to calculate a relative day/date, invoke your sibling agent - math_and_time_utility_agent. "

        "If asked to find or schedule events without an explicit date/time, you must calculate the desired date/time relative to today. "

        "When scheduling an event, 'at' or 'in' refer to the location of the event. Examples: 1. 'at work' - location is 'work'. 2. 'in London' - location is 'London'. "


        "You must NEVER respond directly to the user. "
        "Only call tools and return their results to your caller. "

    ),
    tools=[get_events, schedule_new_event],
)

calendar_agent_team = Agent(
    name="calendar_agent_team",
    description=(
        "Manages the user's calendar: resolves times, calculates durations, "
        "and interacts with Google Calendar through sub-agents. Can schedule and cancel events. "
    ),
    instruction=(
        "If unable to complete a task, return to the root_agent. "
        "Never respond directly to the user. Only call sub-agents. "
        "To get, cancel or schedule events, invoke calendar_interaction_agent. "
        "For date/time calculations, invoke math_and_time_utility_agent. "
        "Use math_and_time_utility_agent to calculate durations, free time, and relative dates. "

        "For scheduling without an explicit start time, default start time is 9am. "
        "For scheduling without an explicit end time, default duration is 1 hour. "

        "Once an operation is complete, pass the results to the root agent. "
        "Examples: "

        "'Next Tuesday' = get the current time with math_and_time_utility_agent, then find the soonest Tuesday after that. "
        "'Next week/month' = period starting after current week/month. "
        "'This week/month' = period starting now until end of current week/month. "
        "Scheduling on a weekday without date defaults to the next occurrence after today."
    ),
    sub_agents=[calendar_interaction_agent, math_and_time_utility_agent]
)
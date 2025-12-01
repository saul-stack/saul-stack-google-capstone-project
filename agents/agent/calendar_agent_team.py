from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .utils.math_and_time_tools import (
    math_tool, get_current_date_and_time, get_relative_date_and_time,
    format_time_to_calendar, calculate_time_duration_hours
)
from .utils.calendar_tools import get_events, schedule_new_event, cancel_event

get_events_tool = FunctionTool(get_events)
schedule_new_event_tool = FunctionTool(schedule_new_event)
cancel_event_tool = FunctionTool(cancel_event)

math_tool = FunctionTool(math_tool)

math_and_time_utility_agent = Agent(
    name="math_and_time_utility_agent",
    description="Handles date/time calculations and math operations.",
    instruction=(

        "get the current time before doing any time-based calculations. You may not need to use it, but get it first with get_current_date_and_time. "
        "The days of the week start on Monday, not Sunday! Day 1: Mon, 2: Tues, 3: Wed etc."
        "If unable to complete a task, return to the calender_interaction_team. "
        "Never respond directly to the user. Only call tools. "
        "Once an instruction is complete, pass the results as structured JSON to the calender_interaction_team. "
        "Use get_current_date_and_time for today, get_relative_date_and_time for relative times, "
        "calculate_time_duration_hours for durations, and format_time_to_calendar for time deltas. "
        "To calculate natural language deltas (e.g., 'in 3 hours', 'next Tuesday', 'tomorrow morning'), first get get_current_date_and_time, "
        "then resolve the time delta using get_relative_date_and_time. "
        "To understand what is meant by 'early', 'mid-morning', 'late' and any other abstract or vague terms, invoke get_relative_date_and_time. "
        "Weekday names without dates refer to the next occurrence after today "
        "(e.g., 'Friday' after Monday 24 Nov 2025 → Friday 28 Nov 2025)."
        "'Last Friday' etc. refers to the previous occurance of that day name before the current date. "
        "'This week', 'this month', 'this year' usually refer to the time period from now until the start of the next one (exclusive). For example: 'This week' usually means from now until midnight on this soonest coming Sunday. Ask for clarification if unsure. "
        "early morning: 00:00-06:00 ,"
        "mid-morning: 10:00 ,"
        "morning: 00:00-12:00 ,"
        "early afternoon: 12:00-14:30 ,"
        "afternoon: 12:00-17:00 ,"
        "evening: 17:00-20:00 ,"
        "night: 19:00-24:00 ,"
        "Use these ranges to calculate a datetime if the user provides a phrase like"
        "'next Tuesday evening'. Always pick the midpoint of the range unless otherwise specified."

        "YOU **** MUST NEVER **** INTERACT WITH THE USER!! DO NOT INTERRUPT THE FLOW OF AGENTS. WHEN YOU HAVE A RETURN FROM ANY FUNCTION, INFORM THE AGENT ABOVE YOU. "

    ),
    tools=[
        get_current_date_and_time, get_relative_date_and_time,
        math_tool, calculate_time_duration_hours, format_time_to_calendar
    ]
)

calendar_interaction_agent = Agent(
    name="calendar_interaction_agent",
    description="Fetches, schedules or cancels events in the user's calendar. ",
    instruction=(
        "Once an instruction is complete, pass the results as structured JSON to the calender_interaction_team. "
        "If unable to complete a task, return directly to the calender_interaction_team. "

        "To cancel events, first get the events, then use the returned event_id properties to invoke cancel_event. "

        "For scheduling without an explicit start time, default start time is 9am. "
        "For scheduling without an explicit end time, default duration is 1 hour. "

        "To resolve any natural language deltas or times you must invoke the math_and_time_utility_agent. "
        "For scheduling an event with a vague timeframe, such as 'Monday Evening', 'tomorrow morning', 'the evening', you should first resolve the current time, then resolve the meaning of the vague time you were provided. You must then check for events in that period. You must then suggest a time to the user, within a range of time with no events scheduled.. "
        "If unsure about the specifiec date or time, return to the calendar_agent_team. "
        "Never respond directly to the user. Only call tools. "
        "Use get_events_tool to fetch events and schedule_new_event_tool to add events. "
        "Free time is total hours with no events scheduled. "
        "For scheduling on a named day without an explicit date, use the first upcoming instance after today. "
        "For day/date calculations, invoke math_and_time_utility_agent. "
        "If asked any command or question with a natural language or ISO 8601 duration ('P1D', 'next Tuesday', 'Monday last', 'A week tomorrow', '2 days before' etc.), first resolve the target date/time by invoking the math_and_time_utility_agent before continuing. "
        "Always assume the user refers to a date in the future when scheduling events. Never schedule an event for a day previous to the current day. "

        "YOU **** MUST NEVER **** INTERACT WITH THE USER!! DO NOT INTERRUPT THE FLOW OF AGENTS. WHEN YOU HAVE A RETURN FROM ANY FUNCTION, INFORM THE AGENT ABOVE YOU. "
    ),
    tools=[get_events_tool, schedule_new_event_tool, cancel_event_tool],
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
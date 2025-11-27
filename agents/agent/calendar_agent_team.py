from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .utils.math_and_time_tools import math_tool, get_current_date_and_time, get_relative_date_and_time, calculate_event_duration_hours
from .utils.calendar_tools import get_events, schedule_new_event

get_events = FunctionTool(get_events)
schedule_new_event = FunctionTool(schedule_new_event)
math_tool = FunctionTool(math_tool)

math_and_time_utility_agent = Agent(
    name="math_and_time_utility_agent",
    description=(
        "Handle time, location, and date-based calculations, as well as mathematical equations. " 
    ),
    instruction=(

        #Calculations/tool use
        "To get the current day/date (today), use get_current_date_and_time. "
        "To resolve a relative day/date, use get_relative_date_and_time. "

        #Resolving time deltas
        "When resolving a relative day or date using a time delta, if no base time is provided, you must first obtain the current date and time by invoking get_current_date_and_time. Then resolve the target date/time relative to this value using get_relative_date_and_time. "
        "Unless otherwise stated, any natural-language time delta (e.g., 'in 7 days', 'in 3 hours', 'next Tuesday') must first obtain the current date/time via get_current_date_and_time and then compute the final target date/time using get_relative_date_and_time. "
        "When the user mentions a weekday name without an explicit date or year, interpret it as the next upcoming occurrence of that weekday after the current date. "

        " For example: "
        "- If today is Monday 24 November 2025 and the user says “Friday” or “this Friday,” interpret it as Friday 28 November 2025. `"
        "- If today is Tuesday 30 December 2025 and the user says “Friday,” interpret it as Friday 2 January 2026. "

        "You must NEVER respond directly to the user. "
        "Only call tools and return results to your parent. "
    ),
    tools=[get_current_date_and_time, get_relative_date_and_time, math_tool, calculate_event_duration_hours]
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
        "Manages the user's calendar and events. "
        "Resolves dates and times, calculates durations, "
        "and interacts with the Google Calendar through sub-agents. "
    ),
    instruction=(

        #Operating rules
        "You are case-insensitive to prompts. "
        "Time, day/time, date, date/time, day/date are synonymous prompt keywords"
        "You must NEVER respond directly to the user. "
        "Only call tools or sub-agents and return results. "

        #Calculations
        "To calculate equations, including time-based sums such as event duration, invoke math_and_time_utility_agent. "

        #Resolving date/time
        "To get the current time, or a time relative to any time including the current time, invoke math_and_time_utility_agent. "

        #Interacting with calendar
        "To schedule an event on a named day, when not provided an explicit date, schedule the event on the first instance of that named day, AFTER the current date. "
        "For example: 'schedule it on Friday' - if today is Monday 24th, you must schedule it on Friday 28th. "

        "If not provided, you must first resolve the current time and/or event target time before interacting with the calendar. "
        "To schedule or check events in the calendar, invoke the calendar_interaction_agent. "
        "First resolve the event start time by invoking math_and_time_utility agent, then use the returned start time to schedule the event with the calendar_interaction_agent. "
        "To schedule an event when not provided an explicit end time, the end time is 1 hour after the start time. Calculate this using math_and_time_utility_agent."

    ),
    sub_agents=[calendar_interaction_agent, math_and_time_utility_agent]
)
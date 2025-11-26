from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .utils.math_and_time_tools import math_tool, get_current_date_and_time, get_relative_date_and_time
from .utils.calendar_tools import get_events

get_events = FunctionTool(get_events)
math_tool = FunctionTool(math_tool)


calendar_interaction_agent = Agent(
    name="calendar_interaction_agent",
    description="Interact with the user's calendar",
    tools=[get_events]
)

time_utility_agent = Agent(
    name="time_utility_agent",
    description="Get the current date and time, calculate date and time based questions",
    tools=[get_current_date_and_time]
)

events_analyser_agent = Agent(
    name="events_analyser_agent",
    description="You will receive a list of events as input. Each event has start and end times. Your task is to calculate requested event metrics such as event duration. Use the math_tool for calculations.",
    tools=[math_tool]
)

calendar_agent_team = Agent(
    name="calendar_agent_team",
    description="Manage the user's calendar and events, answer questions about date and time",
    sub_agents=[calendar_interaction_agent, events_analyser_agent, time_utility_agent]
)

root_agent = Agent(
    name="personal_assistant_agent",
    model="gemini-2.0-flash",
    description=(
        "Personal assistant agent"
    ),
    instruction=(
        "You are a helpful assistant, who will help the user to manage their timetable and plan events."
    ),
    sub_agents=[calendar_agent_team],
)
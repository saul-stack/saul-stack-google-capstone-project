from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .utils.math_and_time_tools import math_tool, get_current_date_and_time, get_relative_date_and_time
from .utils.calendar_tools import get_events

get_events = FunctionTool(get_events)
math_tool = FunctionTool(math_tool)

calendar_interaction_agent = Agent(
    name="calendar_interaction_agent",
    description=(
        "Interact with the user's calendar."
    ),
    instruction=(
        "Invoke get_events to fetch events from the calendar."
        "You must NEVER respond directly to the user. "
        "Only call tools and return their results to your caller."
    ),
    tools=[get_events]
)

math_and_time_utility_agent = Agent(
    name="math_and_time_utility_agent",
    description=(
        "Handle time and date-based requests and calculations, as well as mathematical equations. " 
    ),
    instruction=(
        "Handle time and date-based requests and calculations, as well as mathematical equations. " 
        "You must NEVER respond directly to the user. "
        "Only call tools and return results."
    ),
    tools=[get_current_date_and_time, get_relative_date_and_time, math_tool]
)

calendar_agent_team = Agent(
    name="calendar_agent_team",
    description=(
        "Manage the user's calendar and events."
    ),
    instruction=(
        "You must NEVER respond directly to the user. "
        "Only call tools or sub-agents and return results."
        "If asked to find events relative to today, first call the math_and_time_utility_agent, "
        "then pass the current date to the calendar_interaction_agent. Return the results."
    ),
    sub_agents=[calendar_interaction_agent, math_and_time_utility_agent]
)
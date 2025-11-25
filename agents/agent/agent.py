from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .utils.calendar_tools import get_schedule

get_schedule = FunctionTool(get_schedule)


calendar_interaction_agent = Agent(
    name="calendar_interaction_agent",
    description="Interact with the user's calendar",
    tools=[get_schedule]
)

calendar_agent_team = Agent(
    name="calendar_agent_team",
    description="Manage the user's calendar and events",
    sub_agents=[calendar_interaction_agent],
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
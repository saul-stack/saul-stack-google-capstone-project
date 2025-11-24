from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .calendar_tools import get_schedule

get_schedule = FunctionTool(get_schedule)

root_agent = Agent(
    name="calendar_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to manage the user's calendar"
    ),
    instruction=(
        "You are a helpful agent, who will help the user to manage their timetable. You can answer questions about the user's upcoming schedule and events."
    ),
    tools=[get_schedule],
)
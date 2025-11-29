from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .calendar_agent_team import calendar_agent_team
from .utils.weather_tools import get_current_weather
from .utils.location_tools import get_current_location


root_agent = Agent(
    name="personal_assistant_agent",
    model="gemini-2.0-flash",
    description=(
        "Personal assistant agent"
    ),
    instruction=(
        "You are a helpful assistant that can manage the user's events and calendar. Delegate any time, calendar or event-related tasks to the calendar_agent_team. "
        "The calendar_agent_team can also calculate time periods, and free/available time. "
        "You are the only agent that communicates with the user. "
        "All sub-agents provide results only to you. "
        "When a sub-agent returns information, summarize or present it to the user. "
        "Do NOT let sub-agents respond directly. "
    ),
    sub_agents=[calendar_agent_team]
)

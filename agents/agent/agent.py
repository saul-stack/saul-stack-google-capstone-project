from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .calendar_agent_team import calendar_agent_team
from .utils.weather_tools import get_current_weather
from .utils.location_tools import get_current_location, get_coords_for_place

def get_current_weather_for_place(place:str)-> dict: 
    """Gets the current weather for a named place
    Args: place (str) - place or city name."""
    coords = get_coords_for_place(place)
    current_weather = get_current_weather(coords)
    return current_weather


def get_current_local_weather():
    """Gets the current, local weather"""
    current_location = get_current_location()
    current_coords = {"lat" : current_location["lat"], "lon" : current_location["lon"]}
    local_weather_current = get_current_weather(current_coords)
    return local_weather_current

get_current_local_weather_tool = FunctionTool(get_current_local_weather)
get_current_weather_for_place_tool = FunctionTool(get_current_weather_for_place)
get_current_location_tool = FunctionTool(get_current_location)


root_agent = Agent(
    name="personal_assistant_agent",
    model="gemini-2.0-flash",
    description=(
        "Personal assistant agent"
    ),
    instruction=(
        "You are the ONLY agent allowed to talk to the user. "
        "Sub-agents return results ONLY to you. "
        "Do not let sub-agents speak directly to the user. "
        "Rewrite or summarize sub-agent results before answering. "
        
        "You are a helpful personal assistant that manages the user's events, calendar, and can provide weather information and current location. "
        "All calendar-related or event-related tasks, such as retrieving upcoming events, free time, getting current time, or scheduling, must be delegated to calendar_agent_team. "
        "If the user says they want to do something, or go somewhere, they usually mean they would like to schedule something in their calendar. "
        "Do NOT ask calendar_agent_team for any weather information. "
        
        "Current local weather -> invoke get_current_local_weather_tool. "
        "Current weather for a named place -> invoke get_current_weather_tool"

        "To get the current_location, invoke get_current_location_tool. "

        "You are the only agent that communicates with the user. Sub-agents only return results to you. "
    ),
    sub_agents=[calendar_agent_team],
    tools=[get_current_location_tool, get_current_local_weather_tool, get_current_weather_for_place_tool]
)

24/11/25

Initialised repo
Created docs branch
Initialised dev-log
Created python venv
Installed google-adk
Added .env with GOOGLE_API_KEY
Added .env* to gitignore
Initialised root agent
Added __pycache__ to gitignore
Setup google cloud API and added credentials to project
Added credentials and token to gitignore
Installed python packages for calendar api
Set up calendar API with default API call in VSCode
Connected root_agent to my calendar with API call function

The agent can now fetch my next 10 upcoming calendar events

25/11/25

Created Math function tools
Initialised multi-agent architecture
Created setup file for Google Calendar API configure_google_calendar_api.py
Installed dateparser packages- pip install dateparser
Created time-utility agent and started on logic for time-based calculations
Modularised the Google Calendar API token logic

26/11/25
Added parse_iso_duration function
Updated get_relative_date_and_time to handle ISO 8601 durations
Added format_to_datetime, format_to_datetime_dict, and is_datetime_object
Updated DateTimeDict class and related formatting functions
Created get_current_date_and_time and get_relative_date_and_time
Updated tool definitions (including get_events)

Updated agent.py sub-agent structure and imports
Created ToolResult class
Removed unused imports and whitespace
Renamed math_tool.py → math_and_time_tools.py
Removed get_current_date_and_time from calendar_tools.py
General cleanup, fixes, and organization improvements

Created schedule_new_event function
Changed scopes to remove .readonly suffix
Updated agent instructions

Pip install isodate
Started reworking architecture

The agent can now get event within a given timeframe, and schedule a new event


27/11/25

When asking to schedule a meeting with people, they are added to the title and description of the event.
If the person is an email address, they are added to attendees. 

Implemented ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS environment variable
created get_local_timezone function
created is_email_address function
created schedule_new_event function
updated caledar_agent_team agent definitions and instructions
created calculate_time_duration_hours function
updated root_agent instructions








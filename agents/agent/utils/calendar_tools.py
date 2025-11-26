from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .handle_credentials import get_creds
from .math_and_time_tools import format_time_to_calendar, get_current_date_and_time

def get_events(start_time = None, end_time = None, max_results: int=10) -> dict:

    """Gets the upcoming events in the calendar
    Args:
        max_results (int) - optional: the max number of events to fetch.
        start_time - optional: the starting bounds for events to fetch
        end_time - optional: the ending bounds for events to fetch

    Returns:
        A dictionary containing upcoming events and success message.
    """

    try:
        creds = get_creds()
    except Exception as e:
        return {"status": "error", "events": f"Cannot get credentials: {e}"}

    try:
        service = build("calendar", "v3", credentials=creds)

        if start_time == None:
            start_time = get_current_date_and_time()
            start_time = format_time_to_calendar(start_time["time_iso"])

        else:
            start_time = format_time_to_calendar(start_time)  

        params = {
        "calendarId":"primary",
        "timeMin":start_time,
        "maxResults": max_results,
        "singleEvents":True,
        "orderBy":"startTime",
        }

        if end_time is not None:
            params["timeMax"] = format_time_to_calendar(end_time)   

        events_result = (
            service.events()
            .list(**params)
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return {"status": "success", "message": "No upcoming events found."}

        return {"status": "success", "events": events}

    except HttpError as error:
        return {"status": "error", "events": f"An error occurred: {error}"}

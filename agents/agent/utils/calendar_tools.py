import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .handle_credentials import get_creds
from datetime import timezone
from typing import Dict

def get_current_date_and_time(utc: bool = False) -> Dict[str, str]:
    """
    Returns the current date and time with additional information.

    Args:
        utc (bool): If True, return time in UTC. Default is False (local timezone).

    Returns:
        dict: Contains:
            - status: "success"
            - current_time_iso: ISO 8601 formatted string
            - day_number: Day of the month (string)
            - day_name: Name of the day (string)
            - month_name: Name of the month (string)
            - year: Year (string)
    """
    now = datetime.datetime.now(datetime.timezone.utc) if utc else datetime.datetime.now().astimezone()

    return {
        "status": "success",
        "current_time_iso": now.isoformat(),
        "day_number": str(now.day),
        "day_name": now.strftime("%A"),
        "month_name": now.strftime("%B"),
        "year": str(now.year),
    }

def get_events(max_results: int=10) -> dict:
    """Gets the upcoming events in the calendar

    Args:
        max_results (int): the max number of events to fetch.

    Returns:
        A dictionary containing upcoming events and success message.
    """

    try:
        creds = get_creds()
    except Exception as e:
        return {"status": "error", "events": f"Cannot get credentials: {e}"}

    try:
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults= max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return {"status": "success", "message": "No upcoming events found."}

        return {"status": "success", "events": events}

    except HttpError as error:
        return {"status": "error", "events": f"An error occurred: {error}"}

import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .handle_credentials import get_creds

def get_events(max_results: int=10) -> dict:
    """Gets the upcoming events in the calendar

    Args:
        max_results: the number of events to fetch.

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

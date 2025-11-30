from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .handle_credentials import get_creds
from .math_and_time_tools import format_time_to_calendar, get_current_date_and_time, get_local_timezone, get_relative_date_and_time
import re

def get_events(start_time = None, end_time = None, max_results: int=10) -> dict:

    """Gets the upcoming events in the calendar
    Args:
        max_results (int) - optional: the max number of events to fetch. 
        start_time - optional: the starting bounds for events to fetch. 
        end_time - optional: the ending bounds for events to fetch. 

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

def schedule_new_event(params: dict) -> dict:
    
    """
    Description: schedule an event in the Google Calendar.
    
    Args:
        params (dict): Dictionary of event parameters.
            Required:
                - event_title (str): Title of the event
                - start_datetime (str): Start date/time in ISO format or natural language

            Optional:
                - end_datetime (str): End date/time, defaults to 1 hour after start
                - location (str)
                - description (str)
                - recurrence (list of str)
                - attendees (list of str)
                - reminders (dict)
    
    Returns:
        dict: Response from Google Calendar API or error info.
    """

    def format_new_event(params: dict) -> dict:

        required_keys = ['event_title', 'start_datetime']
        missing_keys = [key for key in required_keys if key not in params]
        if missing_keys:
            return {"status": "error", "message": f"Missing required parameters: {', '.join(missing_keys)}"}

        start_time = format_time_to_calendar(params['start_datetime'])
        if start_time is None:
            return {"status": "error", "message": f"Could not parse start_datetime: {params['start_datetime']}"}

        end_time = format_time_to_calendar(params.get('end_datetime')) if params.get('end_datetime') else get_relative_date_and_time(params['start_datetime'], "+ 1 hour").get("time_google_calendar")
        event_title = params.get('event_title').title()
        timezone = get_local_timezone()
        description = params.get('description') or ''

        attendees = params.get("attendees")

        attendee_email_addresses = []
        attendee_names = []

        if attendees is not None:

            for attendee in attendees:

                if is_email_address(attendee):
                    attendee_email_addresses.append({'email': attendee})

                attendee_names.append(attendee)

            if len(attendee_names) > 0:
                description += "With"
                description += " " + ", ".join(attendee_names)

        formatted_event = {
            'summary': event_title,
            'location': params.get('location'),
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
            'recurrence': params.get('recurrence', []),
            'attendees': attendee_email_addresses,
            'reminders': params.get('reminders', {'useDefault': True, 'overrides': []}),
        }

        return formatted_event


    def add_event_to_calendar(event: dict) -> dict:
        try:
            creds = get_creds()
        except Exception as e:
            return {"status": "error", "message": f"Cannot get credentials: {e}"}

        try:
            service = build("calendar", "v3", credentials=creds)
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            return {"status": "success", "event": created_event}
        except HttpError as error:
            return {"status": "error", "message": f"An error occurred: {error}"}
    
    formatted_event = format_new_event(params)
    return add_event_to_calendar(formatted_event)

def cancel_event(event_id: str) -> dict:
    """
    Cancel (delete) an event from the user's primary Google Calendar.

    Args:
        event_id (str): The unique Google Calendar event ID.

    Returns:
        dict: Status and message about the deletion.
    """

    if not event_id:
        return {"status": "error", "message": "Missing required parameter: event_id"}
    try:
        creds = get_creds()
    except Exception as e:
        return {"status": "error", "message": f"Cannot get credentials: {e}"}
    try:
        service = build("calendar", "v3", credentials=creds)

        service.events().delete(
            calendarId="primary",
            eventId=event_id
        ).execute()

        return {
            "status": "success",
            "message": f"Event '{event_id}' has been cancelled successfully."
        }

    except HttpError as error:
        return {
            "status": "error",
            "message": f"Failed to cancel event: {error}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {e}"
        }

def is_email_address(x: str) -> bool:
    if not x or not isinstance(x, str):
        return False

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, x))
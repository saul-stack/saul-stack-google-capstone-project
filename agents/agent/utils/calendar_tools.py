from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import dateparser
from .handle_credentials import get_creds
from .math_and_time_tools import format_time_to_calendar, get_current_date_and_time, get_local_timezone, get_relative_date_and_time, parse_iso_duration
import re

def get_events(start_time=None, end_time=None, max_results: int = 10) -> dict:
    """Gets the upcoming events in the calendar
    Args:
        max_results (int) - optional: the max number of events to fetch. 
        start_time - optional: the starting bounds for events to fetch. 
        end_time - optional: the ending bounds for events to fetch. 
        Defaults from current time to 1 week from the current time. 
        Provide the time window to the user when you show your results, for example: 'Upcoming events from Monday Nov 5th to Thursday Nov 8th: {bullet pointed list}. '

    Returns:
        A dictionary containing:
        - upcoming events
        - start and end datetime (human-readable)
        - status
        - message if no events
    """

    try:
        creds = get_creds()
    except Exception as e:
        return {"status": "error", "events": f"Cannot get credentials: {e}"}

    try:
        service = build("calendar", "v3", credentials=creds)

        # Determine start_time
        if start_time is None:
            current_dt = get_current_date_and_time()
            start_dt = current_dt["timestamp"]
            start_time = format_time_to_calendar(current_dt["time_iso"])
        else:
            start_dt = start_time if isinstance(start_time, datetime.datetime) else dateparser.parse(start_time)
            start_time = format_time_to_calendar(start_dt.isoformat())

        # Determine end_time
        if end_time is None:
            one_week_later = get_relative_date_and_time(start_dt, "P1W")
            end_dt = one_week_later["timestamp"]
            end_time = format_time_to_calendar(one_week_later["time_iso"])
        else:
            end_dt = end_time if isinstance(end_time, datetime.datetime) else dateparser.parse(end_time)
            end_time = format_time_to_calendar(end_dt.isoformat())

        params = {
            "calendarId": "primary",
            "timeMin": start_time,
            "timeMax": end_time,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }

        events_result = service.events().list(**params).execute()
        events = events_result.get("items", [])

        if not events:
            return {
                "status": "success",
                "message": "No upcoming events found.",
                "start_date": start_dt.strftime("%A %d %B %Y"),
                "end_date": end_dt.strftime("%A %d %B %Y"),
            }

        return {
            "status": "success",
            "events": events,
            "start_date": start_dt.strftime("%A %d %B %Y"),
            "end_date": end_dt.strftime("%A %d %B %Y"),
        }

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
                - end_datetime (str): End date/time in ISO format or natural language

            Optional:
                - location (str)
                - description (str)
                - recurrence (list of str)
                - attendees (list of str)
                - reminders (dict)
    
    Returns:
        dict: Response from Google Calendar API or error info.
    """


    end_time = params.get("end_datetime")
    if end_time == None:

        return {"status": "error", "message": "Missing required end_datetime key in input dict. Set the end_datetime to an hour after the start datetime. "}
    



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
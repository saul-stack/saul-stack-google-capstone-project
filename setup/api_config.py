import os

def configure_scopes():
    # Default to read-only calendar access
    ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS = os.getenv("ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS", "false").lower() == 'true'

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

    if ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS:
        SCOPES = ["https://www.googleapis.com/auth/calendar"]
    
    return SCOPES

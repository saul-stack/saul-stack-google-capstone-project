import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(CURRENT_DIRECTORY, "../../../setup/token.json")

def configure_scopes():
    # Default to read-only calendar access
    ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS = os.getenv("ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS", "false").lower() == 'true'

    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    if ALLOW_GOOGLE_CALENDAR_WRITE_ACCESS:
        SCOPES = ["https://www.googleapis.com/auth/calendar"]
    
    return SCOPES

SCOPES = configure_scopes()


def get_creds() -> Credentials:
    """
    Returns valid Google API credentials from token.json, refreshing token if necessary.
    Raises FileNotFoundError if token.json not found, or ValueError if token is invalid/could not be refreshed.
    """

    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError("Error: setup/credentials.json not found. Cannot authenticate.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                error = (f"Error refreshing token: {e}")
                print(error)
                raise ValueError("Error refreshing token.")
        else:
            error = "Token is invalid. Please generate a new token."
            print(error)
            raise ValueError(error)

    return creds
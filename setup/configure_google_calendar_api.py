import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Define the scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Paths to credentials files
CREDENTIALS_PATH = os.path.join(CURRENT_DIRECTORY, "credentials.json")
TOKEN_PATH = os.path.join(CURRENT_DIRECTORY, "token.json")

def ping_calendar(creds):
    """Ping calendar without fetching events."""
    try:
        service = build("calendar", "v3", credentials=creds)
        service.calendarList().list(maxResults=1).execute()
        return True
    except HttpError as error:
        print(f"Error connecting to Google Calendar: {error}")
        return False

def main():
    creds = None

    # Load credentials from token.json if it exists
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # No valid credentials found
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"Error: setup/credentials.json not found. Cannot authenticate.")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    if ping_calendar(creds):
        print("\n--- Successfully connected to your Google Calendar ---\n--- ! DO NOT EXPOSE 'token.json' or 'credentials.json' ! ---\n--- Treat these like passwords- they provide sensitive access to your Google Calendar ---\n")
    else:
        print("Failed to connect to Google Calendar.")

if __name__ == "__main__":
    main()
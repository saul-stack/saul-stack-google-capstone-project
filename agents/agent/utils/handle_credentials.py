import os
from pathlib import Path

USE_SERVICE_ACCOUNT = os.getenv("USE_SERVICE_ACCOUNT", "false").lower() == "true"

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CURRENT_DIRECTORY = Path(__file__).resolve().parent

if USE_SERVICE_ACCOUNT:
    # ---------------- Service Account Path ----------------
    from google.oauth2 import service_account

    SERVICE_ACCOUNT_PATH = CURRENT_DIRECTORY / "../../../setup/test-credentials.json"

    def get_creds():
        """
        Returns Google API credentials using a service account.
        Raises FileNotFoundError if the key file is missing.
        """
        if not SERVICE_ACCOUNT_PATH.exists():
            raise FileNotFoundError(f"Service account key not found at {SERVICE_ACCOUNT_PATH}")

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_PATH,
            scopes=SCOPES
        )
        return creds

else:
    # ---------------- User OAuth Path ----------------
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    TOKEN_PATH = CURRENT_DIRECTORY / "../../../setup/token.json"

    def get_creds():
        """
        Returns valid Google API credentials from token.json, refreshing token if necessary.
        Raises FileNotFoundError if token.json not found, or ValueError if token is invalid/could not be refreshed.
        """
        if not TOKEN_PATH.exists():
            raise FileNotFoundError(f"Token not found at {TOKEN_PATH}")

        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    raise ValueError(f"Error refreshing token: {e}")
            else:
                raise ValueError("Token is invalid. Please generate a new token.")

        return creds
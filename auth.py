"""
Handles OAuth2 authentication with the Gmail API.

On first run, opens a browser window for the user to authorize the app.
The resulting token is saved to token.json so subsequent runs skip the
browser prompt.
"""

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

TOKEN_PATH = Path("token.json")
CREDENTIALS_PATH = Path("credentials.json")


def get_credentials() -> Credentials:
    """Return valid Gmail API credentials, refreshing or re-authorizing as needed."""
    creds: Credentials | None = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    "credentials.json not found.\n"
                    "Download it from the Google Cloud Console and place it in the "
                    "project root directory.\n"
                    "See README.md for step-by-step instructions."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json())

    return creds

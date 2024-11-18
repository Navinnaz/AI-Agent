import pandas as pd
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define the required Google Sheets API scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def authenticate_user():
    """Initiate OAuth flow to allow user authorization."""
    creds = None

    # Check if there are existing user credentials and refresh them if needed
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials are available, prompt user login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh token using Request
        else:
            # Run OAuth flow to get user authorization
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=8502)  # Ensure this matches your redirect URI

        # Save the credentials for future access
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def get_google_sheet_data(sheet_id, range_name):
    """Fetch data from Google Sheets using OAuth credentials."""
    creds = authenticate_user()  # Use OAuth to get credentials for each user
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    try:
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        rows = result.get('values', [])
        
        if not rows:
            print("No data found in the specified range.")
            return pd.DataFrame()  # Return an empty DataFrame if no data

        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of error

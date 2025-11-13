#!/usr/bin/env python3
"""
Script to fetch the current spreadsheet ID from the Google Drive JSON config file.

Usage: 
    Command line: python3 fetch_spreadsheet_id.py
    Import in code: from fetch_spreadsheet_id import get_latest_spreadsheet_id
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io


# Configuration
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'account.json')
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]
CONFIG_FILE_NAME = 'timesheet_config.json'


def get_latest_spreadsheet_id(verbose=False):
    """
    Fetch the latest spreadsheet ID from Google Drive's timesheet_config.json file.
    
    Args:
        verbose: If True, prints progress messages. If False, silent mode.
    
    Returns:
        str: The current spreadsheet ID from Google Drive
    
    Raises:
        FileNotFoundError: If service account file or config file is not found
        ValueError: If spreadsheet ID is not found in config file
        Exception: For any other errors during fetching
    """
    # Check if service account file exists
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account file not found: {SERVICE_ACCOUNT_FILE}\n"
            f"Please ensure timesheet-fetcher.json exists in the project root."
        )
    
    # Authenticate with Google Drive
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    
    # Search for the config file
    results = service.files().list(
        q=f"name='{CONFIG_FILE_NAME}' and trashed=false",
        spaces='drive',
        fields='files(id, name, modifiedTime)',
        orderBy='modifiedTime desc',
        pageSize=1
    ).execute()
    
    files = results.get('files', [])
    if not files:
        raise FileNotFoundError(
            f"Config file '{CONFIG_FILE_NAME}' not found in Google Drive.\n"
            f"Please run the Apps Script to create a timesheet first, or\n"
            f"ensure the service account has access to the file."
        )
    
    # Download and parse the config file
    file_id = files[0]['id']
    request = service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    file_stream.seek(0)
    config_data = json.load(file_stream)
    
    spreadsheet_id = config_data.get('current_spreadsheet_id')
    if not spreadsheet_id:
        raise ValueError(
            f"'current_spreadsheet_id' not found in {CONFIG_FILE_NAME}.\n"
            f"The config file may be corrupted or incomplete."
        )
    
    if verbose:
        print(f"✓ Fetched latest spreadsheet ID from Drive")
        print(f"  Month: {config_data.get('month', 'N/A')} {config_data.get('year', '')}")
        print(f"  ID: {spreadsheet_id}")
        print(f"  URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    
    return spreadsheet_id


def main():
    """
    Main function - displays the current spreadsheet ID from Google Drive
    """
    print("=" * 60)
    print("Fetching Spreadsheet ID from Google Drive")
    print("=" * 60)
    
    try:
        spreadsheet_id = get_latest_spreadsheet_id(verbose=True)
        
        print("\n" + "=" * 60)
        print("✓ SUCCESS!")
        print("=" * 60)
        print(f"\nCurrent Spreadsheet ID: {spreadsheet_id}")
        print("\nYou can now use this in your scripts by importing:")
        print("  from fetch_spreadsheet_id import get_latest_spreadsheet_id")
        
        return True
    
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        return False
    
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        return False
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

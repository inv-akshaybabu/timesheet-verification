#!/usr/bin/env python3
"""
Test script to verify Google Drive API access and service account credentials.
Run this before using fetch_spreadsheet_id.py to ensure everything is set up correctly.
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'account.json')
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]


def test_service_account_file():
    """Test if service account file exists and is valid JSON."""
    print("1. Testing service account file...")
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"   ✗ FAILED: Service account file not found at {SERVICE_ACCOUNT_FILE}")
        print("   → Please download the JSON key from Google Cloud Console")
        print("   → Save it as 'account.json' in the project root")
        return False
    
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"   ✗ FAILED: Missing required fields: {', '.join(missing_fields)}")
            return False
        
        if data['type'] != 'service_account':
            print(f"   ✗ FAILED: Invalid account type: {data['type']}")
            print("   → Expected 'service_account'")
            return False
        
        print("   ✓ Service account file is valid")
        print(f"   → Project: {data.get('project_id', 'N/A')}")
        print(f"   → Email: {data.get('client_email', 'N/A')}")
        return True
    
    except json.JSONDecodeError:
        print("   ✗ FAILED: Invalid JSON format")
        return False
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return False


def test_authentication():
    """Test authentication with Google Drive API."""
    print("\n2. Testing authentication with Google Drive API...")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        
        print("   ✓ Authentication successful")
        return service
    
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        print("   → Check if your service account credentials are correct")
        return None


def test_drive_access(service):
    """Test if we can access Google Drive."""
    print("\n3. Testing Google Drive access...")
    
    try:
        # Try to list files (even if empty)
        results = service.files().list(
            pageSize=5,
            fields='files(id, name, mimeType, modifiedTime)'
        ).execute()
        
        files = results.get('files', [])
        
        print(f"   ✓ Drive access successful")
        print(f"   → Can see {len(files)} file(s)")
        
        if files:
            print("\n   Recent files accessible to service account:")
            for file in files[:3]:  # Show first 3
                print(f"     - {file['name']} (ID: {file['id'][:20]}...)")
        else:
            print("   ⚠ WARNING: No files found")
            print("   → Make sure to share the Google Drive folder with the service account")
            print("   → Service account email from step 1")
        
        return True
    
    except HttpError as e:
        print(f"   ✗ FAILED: HTTP Error {e.resp.status}")
        print(f"   → {e.error_details}")
        return False
    
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return False


def test_config_file_search(service):
    """Test if we can find the timesheet config file."""
    print("\n4. Testing for 'timesheet_config.json'...")
    
    try:
        results = service.files().list(
            q="name='timesheet_config.json' and trashed=false",
            spaces='drive',
            fields='files(id, name, modifiedTime, owners)'
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("   ⚠ WARNING: Config file not found")
            print("   → Run the Apps Script to create a timesheet first")
            print("   → Or share an existing config file with the service account")
            return False
        
        print(f"   ✓ Found {len(files)} config file(s)")
        for file in files:
            print(f"     - {file['name']}")
            print(f"       ID: {file['id']}")
            print(f"       Modified: {file.get('modifiedTime', 'N/A')}")
        
        return True
    
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Google Drive API - Credentials Test")
    print("=" * 60)
    
    # Test 1: Service account file
    if not test_service_account_file():
        print("\n" + "=" * 60)
        print("❌ TEST FAILED: Fix the service account file first")
        print("=" * 60)
        return False
    
    # Test 2: Authentication
    service = test_authentication()
    if not service:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED: Authentication error")
        print("=" * 60)
        return False
    
    # Test 3: Drive access
    if not test_drive_access(service):
        print("\n" + "=" * 60)
        print("❌ TEST FAILED: Cannot access Google Drive")
        print("=" * 60)
        return False
    
    # Test 4: Config file search
    test_config_file_search(service)  # This can fail if file doesn't exist yet
    
    # Final result
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    print("\nYou can now run: python fetch_spreadsheet_id.py")
    
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

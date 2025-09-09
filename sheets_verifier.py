from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json
from datetime import datetime, timedelta
from openai import OpenAI
import calendar
from json_repair import repair_json
from config import *

class SheetsVerifier:
    def __init__(self):
        self.credentials = self._get_credentials()
        self.openai_client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
        
    def _get_credentials(self):
        """Initialize Google Sheets credentials"""
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials
    
    def get_current_month_sheet_name(self):
        """Get current month sheet name (e.g., 'July', 'August')"""
        current_month = datetime.now().strftime("%B")
        return current_month
    
    def is_holiday(self, date):
        """Check if a given date is a holiday"""
        date_str = date.strftime("%Y-%m-%d")
        return date_str in HOLIDAYS
    
    def get_last_working_day(self):
        """Get the last working day (excluding weekends and holidays)"""
        today = datetime.now()
        current_day = today.weekday()  # 0=Monday, 6=Sunday
        
        # Skip if today is weekend
        if current_day in [5,6]:  # Monday or Sunday
            return None
            
        # Find the last working day
        check_date = today - timedelta(days=1)
        
        # Keep going back until we find a non-weekend, non-holiday day
        while check_date.weekday() in [5, 6] or self.is_holiday(check_date):  # Saturday=5, Sunday=6
            check_date = check_date - timedelta(days=1)
            
        return check_date.strftime("%-d-%b")  # Format like "15-Jul"

    def get_current_day(self):
        """Get current day"""
        today = datetime.now()
        current_day = today.weekday()  # 0=Monday, 6=Sunday
        
        # Skip if today is weekend
        if current_day in [5, 6] or self.is_holiday(today):
            return None
            
        return today.strftime("%d-%b")  # Format like "15-Jul"

    def get_sheet_data(self, spreadsheet_id, range_name):
        """Fetch data from Google Sheet"""
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}"
        headers = {"Authorization": f"Bearer {self.credentials.token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('values', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sheet data: {e}")
            return []
    
    def get_engineer_sheet_data(self, engineer_name, current_month):
        """Fetch data from a specific engineer's sheet within the main spreadsheet"""
        # Build range: 'EngineerName'!A1:K100 for current month data
        sheet_range = f"'{engineer_name}'!{SHEET_DATA_RANGE}"
        
        try:
            return self.get_sheet_data(MAIN_SPREADSHEET_ID, sheet_range)
        except Exception as e:
            print(f"Error fetching data for engineer {engineer_name}: {e}")
            return []


    def parse_last_working_day_entries(self, sheet_data, target_date):
        """Parse entries for the last working day from sheet data - includes configurable rows after date"""
        if not sheet_data or len(sheet_data) < 2:
            return []
        
        # Find header row (look for 'Date' in column B, index 1)
        header_row = None
        for i, row in enumerate(sheet_data):
            if len(row) > 1 and 'Date' in str(row[1]):  # Date is in column B (index 1)
                header_row = i
                break
        
        if header_row is None:
            print("Could not find header row with 'Date' in column B")
            return []
        
        # Extract entries for the target date and next configurable rows
        target_entries = []
        i = header_row + 1
        
        while i < len(sheet_data):
            row = sheet_data[i]
            if len(row) == 0:
                i += 1
                continue
                
            # Check if this row has the target date in column B (index 1)
            date_cell = str(row[1]).strip() if len(row) > 1 else ""
            
            if target_date in date_cell or date_cell == target_date:
                print(f"Found target date '{target_date}' at row {i + 1} (column B)")
                
                # Parse this row and the next configurable rows for all tasks on this date
                rows_to_check = ROWS_TO_CHECK_AFTER_DATE + 1  # +1 to include the current row
                for j in range(i, min(i + rows_to_check, len(sheet_data))):
                    task_row = sheet_data[j]
                    if len(task_row) == 0:
                        continue
                    
                    # Skip if this is another date row (unless it's the first one)
                    if j > i and len(str(task_row[1]).strip()) > 0 and any(char.isdigit() for char in str(task_row[1])):
                        # This looks like a new date in column B, stop processing
                        print(f"  Found new date at row {j + 1}, stopping task collection")
                        break
                    
                    # Parse the task data according to correct column structure
                    entry = {
                        'row_number': j + 1,  # For debugging
                        'date': target_date,  # Use the target date for all related tasks
                        'module_area': task_row[2] if len(task_row) > 2 else '',  # Column C
                        'task_details': task_row[3] if len(task_row) > 3 else '',  # Column D
                        'status': task_row[4] if len(task_row) > 4 else '',  # Column E
                        'activity_type': task_row[5] if len(task_row) > 5 else '',  # Column F
                        'start_time': task_row[6] if len(task_row) > 6 else '',  # Column G
                        'end_time': task_row[7] if len(task_row) > 7 else '',  # Column H
                        'remarks': task_row[10] if len(task_row) > 10 else ''  # Column K
                    }
                    
                    # Only add entries that have meaningful task details
                    if entry['task_details'].strip() or entry['module_area'].strip():
                        target_entries.append(entry)
                        print(f"  Added task from row {j + 1}: {entry['task_details'][:50]}...")
                
                # Move to the row after the processed block
                i = min(i + rows_to_check, len(sheet_data))
            else:
                i += 1
        
        print(f"Total entries found for {target_date}: {len(target_entries)}")
        return target_entries
    
    def analyze_employee_data(self, employee_name, last_day_entries):
        """Analyze employee's last working day task data"""
        
        # Format the entries for AI analysis
        formatted_entries = []
        for entry in last_day_entries:
            entry_text = f"""
Task: {entry['task_details']}
Module/Area: {entry['module_area']}
Status: {entry['status']}
Activity Type: {entry['activity_type']}
Time: {entry['start_time']} - {entry['end_time']}
Remarks: {entry['remarks']}
"""
            formatted_entries.append(entry_text)
        
        data_text = "\n" + "="*50 + "\n".join(formatted_entries)
        
        # Calculate total time and task counts
        total_tasks = len(last_day_entries)
        completed_tasks = len([e for e in last_day_entries if 'completed' in str(e.get('status', '')).lower()])
        
        # Prepare detailed prompt for task validation
        prompt = f"""
Analyze the last working day task report for {employee_name}:

{data_text}

IMPORTANT CONTEXT:
- This engineer worked on {total_tasks} tasks on their last working day
- {completed_tasks} tasks are marked as completed
- Each task shows time spent and detailed remarks
- "Remarks" field may contain additional tasks outside the main project

Please provide ONLY a structured summary in the following format (no additional text, explanations, or notes):
1. Employee name and total hours worked (sum of all task durations)
2. A tree-like structure listing:
    - Each task/activity (with time in hours)
    - Grouped under meaningful labels (e.g., Dev, QA, Meetings)
3. Keep formatting similar to:
    👤 John Doe (Total: 8.5h)
    ├ Dev – Feature A (3h)
    ├ Meeting – Sprint Planning (1.5h)
    └ Code Review (4h)
4. Remarks out of the projects so merge all remarks and make a summary based on this no need to include on the project summary also count total hours mentioned there

Use unicode symbols like ├ and └ for clarity. Sort tasks by start time.
"""
        
        return self._get_ai_analysis(employee_name, prompt)
    
    def _get_ai_analysis(self, employee_name, prompt):
        """Get AI analysis using OpenAI client with OpenRouter"""
        try:
            completion = self.openai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": SITE_URL,
                    "X-Title": SITE_NAME,
                },
                model=AI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            ai_response = completion.choices[0].message.content
            
            return ai_response,True
                
        except Exception as e:
            print(f"Error getting AI analysis for {employee_name}: {e}")
            return (employee_name,True)
    
    def verify_all_employees(self):
        """Verify all employee sheets and return analysis results"""
        results = []
        
        # Get current month and last working day
        current_month = self.get_current_month_sheet_name()
        last_working_day = self.get_last_working_day()
        
        print(f"Checking entries for working day: {last_working_day}")
        print(f"Using main spreadsheet ID: {MAIN_SPREADSHEET_ID}")
        
        for engineer_name in ENGINEER_NAMES:
            print(f"Checking {engineer_name}'s sheet...")
            
            # Get sheet data from the engineer's sheet within the main spreadsheet
            sheet_data = self.get_engineer_sheet_data(engineer_name, current_month)
            
            # Parse last working day entries
            last_day_entries = self.parse_last_working_day_entries(sheet_data, last_working_day)
            
            print(f"Found {len(last_day_entries)} entries for {engineer_name} on {last_working_day}")
            if last_day_entries:
                # Analyze the data
                # analysis = self.analyze_employee_data(engineer_name, last_day_entries)
                analysis = ""
                results.append(analysis)
            else:
                results.append((engineer_name, False))
        
        return results
    
    def send_google_chat_message(self, message, webhook_url=None):
        """Send message to Google Chat space"""
        if TEST_MODE:
            print(f"TEST MODE: Would send Google Chat message: {message}")
            return True
            
        url = webhook_url or GOOGLE_CHAT_WEBHOOK_URL
        if not url:
            print("Google Chat webhook URL not configured")
            return False
        
        payload = {
            "text": message
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            print("Message sent to Google Chat successfully")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Google Chat: {e}")
            return False
    

    
    def send_employee_reminder(self, employees_to_remind):
        """Send reminder message to employees who haven't submitted timesheets"""
        if not employees_to_remind or not EMPLOYEE_ALERT_WEBHOOK_URL:
            return False

        # Create mentions for employees with chat IDs
        mentions = []
        employee_mentions = []
        
        for employee in employees_to_remind:
            chat_id = EMPLOYEE_CHAT_IDS.get(employee)
            if chat_id:
                mentions.append({
                    "id": chat_id,
                    "type": "USER"
                })
                employee_mentions.append(f"<users/{chat_id}>")
            else:
                # Fallback to name if no chat ID configured
                employee_mentions.append(employee)
                print(f"Warning: No chat ID configured for {employee}, using name instead")
        
        # Build message with proper mentions
        if employee_mentions:
            message = f'Dear {", ".join(employee_mentions)},\n\n'
        else:
            message = 'Dear team,\n\n'
            
        message += 'This is a friendly reminder to update your time sheets. '
        message += 'It is important to keep our records accurate and up-to-date.\n\n'
        message += 'Thank you for your attention to this matter.\n\n'
        message += 'Best regards'
        
        # Send message with mentions if available
        return self.send_google_chat_message(message,EMPLOYEE_ALERT_WEBHOOK_URL)
    
   
    
    def run_daily_verification(self):
        """Main method to run the daily verification process"""
        print("Starting daily task verification...")
        today = datetime.now().strftime("%Y-%m-%d")
        # Check if we should run verification today
        last_working_day = self.get_last_working_day()
        if not last_working_day:
            print("No verification needed - today is weekend or no valid working day to check")
            return []
        # Verify all employee sheets
        results = self.verify_all_employees()
        
        # Find employees who need to be reminded (no data or poor performance)
        employees_to_remind = []
        summary_message=f"📊 Daily Task Report Summary - {today} \n"
        for data,status in results:
            if not status:
                employees_to_remind.append(data)
                summary_message +=data  +"❌ Not Added \n"
            else:
                summary_message +=data+"\n"
        
        # Send employee reminders if needed
        if employees_to_remind:
            print(f"Sending reminders to: {', '.join(employees_to_remind)}")
            self.send_employee_reminder(employees_to_remind)
        else:
            print("No employee reminders needed - all timesheets are properly submitted")
        

        print("\n" + "="*50)
        print("VERIFICATION SUMMARY")
        print("="*50)
        print(summary_message)
        print("="*50)
        
        self.send_google_chat_message(summary_message)
        
        return results

def main():
    """Main function to run the verification"""
    verifier = SheetsVerifier()
    results = verifier.run_daily_verification()


if __name__ == "__main__":
    main()

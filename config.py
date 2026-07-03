import os
from dotenv import load_dotenv
from fetch_spreadsheet_id import get_latest_spreadsheet_id

load_dotenv()

# Google Sheets Configuration
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Single Google Sheet ID containing all engineer sheets
# This will automatically fetch the latest ID from Google Drive when the module is imported
MAIN_SPREADSHEET_ID = get_latest_spreadsheet_id(verbose=False)

# Engineer names (these will be used as sheet names within the main spreadsheet)
ENGINEER_NAMES = [
    # 'Abdul Fahad Rahman',
    # 'Adarsh Varghese K.J',
    'Akshay Babu',
    'Amal Anand',
    'Angaliya Vincent',
    'Anjusha P',
    'Anusha Ramesh',
    'Betsy M Baby',
    'Navaneeth Krishna',
    'Sarath U',
    # 'Shilpa Modi',
    'Sooraj V Rajan',
    'Vishnu B'
    # Add more engineer names as needed
]

# Employee Google Chat IDs for mentioning - Add numerical user IDs for proper mentions
EMPLOYEE_CHAT_IDS = {
    'Abdul Fahad Rahman': '104940719795598447961',
    'Adarsh Varghese K.J': '103780210602100226072', # Replace with actual numerical chat ID
    'Akshay Babu':'107266041361482630574',
    'Amal Anand':'113967709910634727711',
    'Angaliya Vincent': '113456956135387674036',
    'Anjusha P':'116685560808750021293',
    'Anusha Ramesh': '106714156322946827862',
    'Betsy M Baby':'101583516415278809098',
    'Navaneeth Krishna': '100205661721437124403',
    'Sarath U':'107267410676956151194',
    'Shilpa Modi': '100266655928069373143',
    'Sooraj V Rajan':'111321564331554271713',
    'Vishnu B':'106329475361764589052'
    # Add more employees and their chat IDs like:
    # 'Employee Name': 'their_numerical_chat_id',
}

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
SITE_URL = os.getenv('SITE_URL', 'https://your-site.com')  # Optional
SITE_NAME = os.getenv('SITE_NAME', 'Task Verifier')  # Optional
AI_MODEL = "deepseek/deepseek-chat-v3-0324:free"

# Google Chat Configuration
GOOGLE_CHAT_WEBHOOK_URL = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')  # For manager reports
EMPLOYEE_ALERT_WEBHOOK_URL = os.getenv('EMPLOYEE_ALERT_WEBHOOK_URL')  # For employee reminders

# Test Mode Configuration
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'  # When True, no notifications are sent

# Holiday Configuration (2025 holidays)
HOLIDAYS = [
    "2025-04-10",  # April 10, 2025
    "2025-05-01",  # May 1, 2025
    "2025-08-03",  # August 3, 2025
    "2025-08-15",  # August 15, 2025
    "2025-09-14",  # September 14, 2025
    "2025-10-01",  # October 1, 2025
    "2025-10-02",  # October 2, 2025
    "2025-10-20",  # October 20, 2025
    "2025-12-09",  # December 9, 2025
    "2025-12-25",  # December 25, 2025
    "2026-01-01",
    "2026-01-26",
    "2026-03-20",
    "2026-04-03",
    "2026-04-15",
    "2026-05-01",
    "2026-08-15",
    "2026-08-25",
    "2026-08-26",
    "2026-09-04",
    "2026-10-02",
    "2026-10-20",
    "2026-12-25"
]

# Spreadsheet ID for timesheet link
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '1t-MNuCK1fthR4K1SsgBR8vdiVtZtDcm0')

# Sheet configuration
SHEET_HEADERS = {
    'date': 'B',  # Date is in column B (index 1)
    'module_area': 'C', 
    'task_details': 'D',
    'status': 'E',
    'activity_type': 'F',
    'start_time': 'G',
    'end_time': 'H',
    'duration_task': 'I',
    'duration_total': 'J',
    'remarks': 'K'
}

# Sheet range to read (covers all data rows) - starts from column A
SHEET_DATA_RANGE = 'A1:K150'  # Adjust end row as needed

# Number of rows to check after finding a date (configurable)
ROWS_TO_CHECK_AFTER_DATE = 5  # Change this number as needed

# Jira Configuration
JIRA_URL = os.getenv('JIRA_URL')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

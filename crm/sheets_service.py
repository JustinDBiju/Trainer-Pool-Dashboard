import gspread
from django.conf import settings
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(settings.GOOGLE_SHEET_CREDENTIALS, scopes=SCOPES)
client = gspread.authorize(creds)

# Google Sheet Details
SPREADSHEET_ID = "" # Replace with your Google Sheet ID
SHEET_NAME = "Form Responses 1"

def fetch_google_sheets_data():
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    raw_data = sheet.get_all_values()

    if not raw_data:
        print("⚠️ Google Sheet is empty!")
        return []

    # Clean headers: Replace spaces, newlines, and special characters with underscores
    headers = [
        header.replace("\n", " ")  # Replace newlines with spaces
              .replace(" ", "_")   # Replace spaces with underscores
              .replace("'", "")    # Remove single quotes
              .replace("/", "_")   # Replace slashes with underscores
              .replace(":", "_")   # Replace colons with underscores
        for header in raw_data[0]
    ]
    print("✅ Google Sheet Headers:", headers)  # Debugging

    feedback_list = []
    for row in raw_data[1:]:
        feedback_list.append(dict(zip(headers, row)))

    print("✅ Fetched Feedback Data:", feedback_list[:5])  # Debugging first 5 rows
    return feedback_list
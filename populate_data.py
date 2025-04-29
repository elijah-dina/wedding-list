import gspread
from oauth2client.service_account import ServiceAccountCredentials
from slugify import slugify as pyslugify  # Rename to avoid conflict
from urllib.parse import urljoin

# Google Sheets connection details
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
SHEET_NAME = "guest_list"
sheet = client.open(SHEET_NAME).sheet1

# Replace with your Flask app's base URL
BASE_URL = "YOUR_APP_DEPLOYMENT_URL"  # e.g., "https://your-app.herokuapp.com/"

def generate_invite_link(guest_name, guest_id):
    guest_name_slug = pyslugify(guest_name)  # Use the imported and renamed function
    return urljoin(BASE_URL, f"/guest/{guest_name_slug}/{guest_id}")

# Get all existing data
records = sheet.get_all_records()

# Find the index of the "NAME" column (case-insensitive)
try:
    name_column_index = [i for i, col in enumerate(sheet.row_values(1)) if col.lower() == "name"][0] + 1
except IndexError:
    print("Error: 'NAME' column not found in the sheet.")
    exit()

# Find the next available column for the invite link
header_row = sheet.row_values(1)
next_column_index = len(header_row) + 1

# Add the "INVITE_LINK" header if it doesn't exist
if "INVITE_LINK" not in [header.upper() for header in header_row]:
    sheet.update_cell(1, next_column_index, "INVITE_LINK")

# Generate and update the invite links for each guest
for index, record in enumerate(records):
    guest_name = record["NAME"]
    guest_id = index
    invite_link = generate_invite_link(guest_name, guest_id)
    sheet.update_cell(index + 2, next_column_index, invite_link)
    print(f"Generated link for {guest_name}: {invite_link}")

print("Invite links have been added to the Google Sheet.")
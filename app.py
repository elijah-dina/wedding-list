import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, request, redirect, url_for
import os
from slugify import slugify
from urllib.parse import urljoin  # Import for creating absolute URLs

app = Flask(__name__)

# Connect to Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open your sheet by name
SHEET_NAME = "guest_list"  # Or use `open_by_key('your_sheet_id')`
sheet = client.open(SHEET_NAME).sheet1  # First tab


# Function to get the base URL of your application
def get_base_url():
    # This will work if you are accessing the request context
    # which is available during request handling.
    # Outside of a request context, you might need to configure this.
    return request.url_root


# Load all rows (as a list of dicts) with the invitation link
def load_guest_data():
    records = sheet.get_all_records()
    updated_records = []
    for index, record in enumerate(records):
        guest_name_slug = slugify(record["NAME"])
        guest_id = index
        # Construct the absolute URL for the guest's invite page
        invite_link = urljoin(get_base_url(), url_for('show_guest', guest_name=guest_name_slug, guest_id=guest_id))
        record['INVITE_LINK'] = invite_link  # Add the new key-value pair
        updated_records.append(record)
    return updated_records


@app.route("/guest/<guest_name>/<int:guest_id>")
def show_guest(guest_name, guest_id):
    records = load_guest_data()
    if 0 <= guest_id < len(records):
        guest = records[guest_id]
        if slugify(guest["NAME"]) == guest_name:
            return render_template("index.html", name=guest["NAME"], number=guest["NUMBER"], guest_id=guest_id, guest_name=guest_name) # Pass guest_name to the template
    return "Guest not found", 404


@app.route("/journey/<guest_name>/<int:guest_id>")
def journey(guest_name, guest_id):
    records = load_guest_data()
    if 0 <= guest_id < len(records):
        guest = records[guest_id]
        if slugify(guest["NAME"]) == guest_name:
            return render_template(
                "page2.html",
                name=guest["NAME"],
                number=guest["NUMBER"],
                guest_id=guest_id,
                remove=guest["REMOVE"],
                invite_link=guest['INVITE_LINK'],
                guest_name=guest_name  # Explicitly pass guest_name again
            )
    return "Guest not found", 404


@app.route("/rsvp/<guest_name>/<int:guest_id>", methods=["POST"])
def rsvp(guest_name, guest_id):
    records = load_guest_data()
    if 0 <= guest_id < len(records):
        guest = records[guest_id]
        if slugify(guest["NAME"]) == guest_name:
            attending = request.form.get("will_attend")
            guests = request.form.get("guests") if attending == "yes" else "Not attending"
            sheet.update_cell(guest_id + 2, 5, guests)  # Column 5 = 'CONFIRMED_RESERVATIONS'
            # Instead of redirecting immediately, pass a message to the thank you page.
            return redirect(url_for("thank_you", guest_name=guest_name, guest_id=guest_id, rsvp_status="Your RSVP has been saved!"))
    return "Guest not found", 404


@app.route("/thankyou/<guest_name>/<int:guest_id>")
def thank_you(guest_name, guest_id):
    records = load_guest_data()
    if 0 <= guest_id < len(records):
        guest = records[guest_id]
        if slugify(guest["NAME"]) == guest_name:
            #  Get the rsvp_status from the URL.  Default to None if not present.
            rsvp_status = request.args.get('rsvp_status', None)
            return render_template("thankyou.html", name=guest["NAME"], rsvp_status=rsvp_status) # Pass to template
    return "Guest not found", 404


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



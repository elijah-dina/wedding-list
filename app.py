import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Load the Excel file
EXCEL_PATH = "guest_list.xlsx"
df = pd.read_excel(EXCEL_PATH, usecols=["NAME", "NUMBER", "REMOVE"])
df = df.reset_index().rename(columns={'index': 'ID'})
print(df)

# Route to the main invitation page
@app.route("/guest/<int:guest_id>")
def show_guest(guest_id):
    if 0 <= guest_id < len(df):
        guest = df.iloc[guest_id]
        return render_template("index.html", name=guest["NAME"], number=guest["NUMBER"], guest_id=guest["ID"])
    return "Guest not found", 404

# Route for the journey page (RSVP page) for a specific guest
@app.route("/journey/<int:guest_id>")
def journey(guest_id):
    if 0 <= guest_id < len(df):
        guest = df.iloc[guest_id]
        return render_template(
            "page2.html",
            name=guest["NAME"],
            number=guest["NUMBER"],
            guest_id=guest["ID"],
            remove=guest["REMOVE"],  # Pass REMOVE column too
        )
    return "Guest not found", 404

# Route to save RSVP responses
@app.route("/rsvp/<int:guest_id>", methods=["POST"])
def rsvp(guest_id):
    if 0 <= guest_id < len(df):
        attending = request.form.get("will_attend")
        guests = request.form.get("guests") if attending == "yes" else "Not attending"
        df.at[guest_id, "CONFIRMED_RESERVATIONS"] = guests
        df.to_excel(EXCEL_PATH, index=False)
        return redirect(url_for("thank_you", guest_id=guest_id))
    return "Guest not found", 404

# Route for thank you page after submitting RSVP
@app.route("/thankyou/<int:guest_id>")
def thank_you(guest_id):
    if 0 <= guest_id < len(df):
        guest = df.iloc[guest_id]
        return render_template("thankyou.html", name=guest["NAME"])
    return "Guest not found", 404


if __name__ == "__main__":
    app.run(debug=True)

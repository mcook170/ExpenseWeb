from flask import Flask, render_template, request, redirect, flash, get_flashed_messages
from datetime import datetime, timedelta
import openpyxl
import os
from flask import session, redirect, url_for
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)

# print("ENV DIGITS:", os.environ.get("DIGITS"))
# print("ENV TOKEN:", os.environ.get("TOKEN"))

# Timeout for Session
app.permanent_session_lifetime = timedelta(minutes=15)

app.secret_key = os.environ.get("TOKEN", "dev-secret")

# Set a secret key for session management
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("pin", "").strip() == os.environ.get("DIGITS", "1234").strip():
            session["authenticated"] = True
            session.permanent = True  # activates the timeout
            return redirect(url_for("index"))
        return "Incorrect PIN", 403
    return render_template("login.html")

# Actual app logic
@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    if request.method == "POST":
        description = request.form.get("description")
        expense_type = request.form.get("expense_type")
        amount = request.form.get("amount")
        note = request.form.get("note")
        date = datetime.now().strftime("%m/%d/%Y")

        # Load styled template
        template_path = os.path.join(app.root_path, "expenses - app.xlsx")
        wb = openpyxl.load_workbook(template_path)
        sheet = wb["Expenses"]
        print("Using sheet:", sheet.title)

        # Append the data
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0.0

        sheet.append([date, expense_type, description, amount, note])
        print([date, expense_type, description, amount, note])

        # Save to disk instead of returning as a download
        wb.save(template_path)
        print(f"Saved to: {os.path.abspath(template_path)}")
        print("Workbook saved!")
        return redirect("/")
    
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
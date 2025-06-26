from flask import Flask, render_template, request, redirect
from datetime import datetime
import openpyxl
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        description = request.form.get("description")
        expense_type = request.form.get("expense_type")
        amount = request.form.get("amount")
        note = request.form.get("note")
        date = datetime.now().strftime("%m/%d/%Y")

        # Load styled template
        template_path = "expenses - app.xlsx"
        wb = openpyxl.load_workbook(template_path)
        sheet = wb.active

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
    
    if __name__ == "__main__":
        app.run(debug=True)
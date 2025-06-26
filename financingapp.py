from flask import Flask, render_template, request, send_file
from datetime import datetime
import openpyxl
import os
import io

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

        # Save to an in-memory stream
        file_stream = io.BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)

        return send_file(
            file_stream,
            as_attachment=True,
            download_name="my_expenses.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    return render_template("index.html")
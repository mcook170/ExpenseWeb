from flask import Flask, render_template, request, redirect, flash, session, url_for
from datetime import datetime, timedelta
import openpyxl
import os
from dotenv import load_dotenv
from pathlib import Path
from models import db, User  # ← import User model

from werkzeug.security import generate_password_hash, check_password_hash

# Load .env
env_path = Path(__file__).parent / "expensive_stuff.env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
app.config['SECRET_KEY'] = os.environ.get("TOKEN", "dev-secret")
app.permanent_session_lifetime = timedelta(minutes=15)

db.init_app(app)

with app.app_context():
    db.create_all()

# 🧾 Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))

        user = User(username=username, pin_hash=generate_password_hash(pin))
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

# 🔐 Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pin = request.form["pin"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.pin_hash, pin):
            session["user_id"] = user.id
            session["username"] = user.username
            session.permanent = True
            return redirect(url_for("index"))

        flash("Invalid username or PIN.")
        return redirect(url_for("login"))

    return render_template("login.html")

# 🧾 Tracker Route
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_id = session["user_id"]
    filename = f"{username}_expenses.xlsx"
    filepath = os.path.join(app.root_path, filename)

    # Create file if it doesn't exist
    if not os.path.exists(filepath):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "Expenses"
        sheet.append(["Date", "Type", "Description", "Amount", "Note"])
        wb.save(filepath)

    if request.method == "POST":
        description = request.form.get("description")
        expense_type = request.form.get("expense_type")
        amount = request.form.get("amount")
        note = request.form.get("note")
        date = datetime.now().strftime("%m/%d/%Y")

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0.0

        wb = openpyxl.load_workbook(filepath)
        sheet = wb["Expenses"]
        sheet.append([date, expense_type, description, amount, note])
        wb.save(filepath)

        return redirect(url_for("index"))

    return render_template("index.html", username=username)

# 🚪 Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
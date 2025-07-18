from flask import Flask, render_template, request, redirect, flash, session, url_for, send_file 
from datetime import datetime, timedelta 
import openpyxl 
import os 
from dotenv import load_dotenv 
from pathlib import Path 
from models import db, User  # ← import User model
import shutil

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

        template_path = os.path.join(app.root_path, "expenses-template.xlsx")
        user_file = os.path.join(app.root_path, f"{username}_expenses.xlsx")
        if not os.path.exists(user_file):
            shutil.copy(template_path, user_file)

        if not os.path.exists(template_path):
            flash("Template file is missing. Please contact support.")
            return redirect(url_for("register"))

        return redirect(url_for("login"))

    return render_template("register.html")

def get_user_filepath(username):
    if "username" not in session:
        flash("Session expired. Please log in.")
        return redirect(url_for("login"))
    return os.path.join(app.root_path, f"{username}_expenses.xlsx")


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
    # filepath = os.path.join(app.root_path, filename) 
    filepath = get_user_filepath(username)

# Handle form submission
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
    return render_template("index.html", username=username, filename=filename)

#📊 Download Route
@app.route("/download") 
def download(): 
    username = session["username"]
    if "user_id" not in session or "username" not in session:
        flash("Session expired. Please log in.")
        return redirect(url_for("login"))

    filepath = get_user_filepath(session["username"])

    if not os.path.exists(filepath):
        flash("No spreadsheet found. Please re-register or contact support.")
        return redirect(url_for("index"))

    return send_file(filepath, as_attachment=True, download_name=f"{username}_expenses.xlsx")

# 🗑️ Delete Account Route
@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if user:
        db.session.delete(user)
        db.session.commit()

    user_file = get_user_filepath(session["username"])
    if os.path.exists(user_file):
        os.remove(user_file)

    session.clear()
    flash("Account deleted. You may now re-register.")
    return redirect(url_for("register"))

# Refresh Template Route
@app.route("/refresh_workbook", methods=["POST"])
def refresh_workbook():
    if "username" not in session:
        return redirect(url_for("login"))

    filepath = get_user_filepath(session["username"])
    template_path = os.path.join(app.root_path, "expenses-template.xlsx")

    if os.path.exists(template_path):
        shutil.copy(template_path, filepath)
        flash("Workbook refreshed with the latest template.")
    else:
        flash("Template file is missing. Please contact support.")

    return redirect(url_for("index"))

#🚪 Logout
@app.route("/logout") 
def logout(): 
    session.clear() 
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
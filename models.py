from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pin_hash = db.Column(db.String(128), nullable=False)
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.now)
    expense_type = db.Column(db.String(50))
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(500))
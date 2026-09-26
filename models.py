from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id"),
                        nullable=False)

    source = db.Column(db.String(100), nullable=False)

    amount = db.Column(db.Float, nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
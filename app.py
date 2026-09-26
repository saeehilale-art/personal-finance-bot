import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Income, Expense
from ai_engine import generate_budget

app = Flask(__name__)
app.secret_key = "saee_finance_project"
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, "database"), exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database", "finance.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_name"] = user.name

            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/income", methods=["GET", "POST"])
def income():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        source = request.form["source"]
        amount = float(request.form["amount"])

        new_income = Income(
            user_id=session["user_id"],
            source=source,
            amount=amount
        )

        db.session.add(new_income)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("income.html")

@app.route("/expense", methods=["GET", "POST"])
def expense():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        expense = Expense(
            user_id=session["user_id"],
            category=request.form["category"],
            title=request.form["title"],
            amount=float(request.form["amount"])
        )

        db.session.add(expense)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("expense.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    incomes = Income.query.filter_by(
        user_id=session["user_id"]
    ).all()

    expenses = Expense.query.filter_by(
        user_id=session["user_id"]
    ).all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    savings = total_income - total_expense

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        income=total_income,
        expense=total_expense,
        savings=savings,
        expenses=expenses
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/budget")
def budget():

    if "user_id" not in session:
        return redirect("/login")

    incomes = Income.query.filter_by(user_id=session["user_id"]).all()
    expenses = Expense.query.filter_by(user_id=session["user_id"]).all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)

    advice = generate_budget(total_income, total_expense)

    return render_template("budget.html", advice=advice)

from collections import defaultdict

@app.route("/report")
def report():

    if "user_id" not in session:
        return redirect("/login")

    incomes = Income.query.filter_by(user_id=session["user_id"]).all()
    expenses = Expense.query.filter_by(user_id=session["user_id"]).all()

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    savings = total_income - total_expense

    category_data = defaultdict(float)

    for item in expenses:
        category_data[item.category] += item.amount

    return render_template(
        "report.html",
        income=total_income,
        expense=total_expense,
        savings=savings,
        expenses=expenses,
        category_data=category_data
    )
if __name__ == "__main__":
    app.run(debug=True)
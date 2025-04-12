from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import requests

# Load env variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['UPLOAD_FOLDER'] = 'static/receipts'

db = SQLAlchemy(app)

# Define database models
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    satisfaction = db.Column(db.Integer, nullable=False)
    receipt_image = db.Column(db.String(100), nullable=True)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Routes

@app.route('/')
def home():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    goals = Goal.query.all()

    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    balance = total_income - total_expense

    return render_template('home.html', incomes=incomes, expenses=expenses, goals=goals,
                           total_income=total_income, total_expense=total_expense, balance=balance)

@app.route('/add-income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        source = request.form['source']
        income = Income(amount=amount, source=source)
        db.session.add(income)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_income.html')

@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        satisfaction = int(request.form['satisfaction'])
        receipt = request.files['receipt']
        receipt_filename = secure_filename(receipt.filename)
        if receipt_filename:  # Save only if file uploaded
            receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_filename))
        else:
            receipt_filename = None

        expense = Expense(amount=amount, category=category,
                          satisfaction=satisfaction, receipt_image=receipt_filename)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_expense.html')

@app.route('/goals', methods=['GET', 'POST'])
def goals():
    if request.method == 'POST':
        name = request.form['name']
        target_amount = float(request.form['target_amount'])
        goal = Goal(name=name, target_amount=target_amount)
        db.session.add(goal)
        db.session.commit()
        return redirect(url_for('home'))
    goals = Goal.query.all()
    return render_template('goals.html', goals=goals)

# Optional: keep your Gemini chatbot!
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-key')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'chat_history' not in session:
        session['chat_history'] = []

    response_text = ""
    if request.method == 'POST':
        user_input = request.form['message']
        response_text = ask_gemini(user_input)

        # Append both user message and bot response to history
        session['chat_history'].append({"sender": "user", "message": user_input})
        session['chat_history'].append({"sender": "bot", "message": response_text})

    return render_template('chat.html', chat_history=session['chat_history'])

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return "Sorry, something went wrong with the response."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

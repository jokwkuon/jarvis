from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import requests
from emotion_detector import detect_emotion

from extensions import db
from models import Income, Expense, Goal
from agents.budget_agent import get_budget_summary
from agents.context_agent import build_context
from context_store import read_context, append_chat_history, get_chat_history, write_context, init_context

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['UPLOAD_FOLDER'] = 'static/receipts'

db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    incomes = Income.query.all()
    expenses = Expense.query.all()
    goals = Goal.query.all()

    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    balance = total_income - total_expense

    goal_progress = []
    for goal in goals:
        progress = (balance / goal.target_amount) * 100 if goal.target_amount > 0 else 0
        progress = min(progress, 100)
        status = "On Track" if progress >= 100 else "In Progress"
        goal_progress.append({
            'name': goal.name,
            'progress': round(progress, 2),
            'status': status
        })

    budget = get_budget_summary(db)

    return render_template('home.html',
                           incomes=incomes,
                           expenses=expenses,
                           goals=goals,
                           total_income=total_income,
                           total_expense=total_expense,
                           balance=balance,
                           goal_progress=goal_progress,
                           budget_status=budget['status'],
                           budget_advice=budget['advice'])

@app.route('/add-income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        source = request.form['source']
        income = Income(amount=amount, source=source)
        db.session.add(income)
        db.session.commit()
        write_context(db)
        return redirect(url_for('home'))
    return render_template('add_income.html')

@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        satisfaction = int(request.form['satisfaction'])
        receipt = request.files['receipt']
        receipt_filename = secure_filename(receipt.filename) if receipt.filename else None

        if receipt_filename:
            receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_filename))

        expense = Expense(amount=amount, category=category,
                          satisfaction=satisfaction, receipt_image=receipt_filename)
        db.session.add(expense)
        db.session.commit()
        write_context(db)
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
        write_context(db)
        return redirect(url_for('home'))
    goals = Goal.query.all()
    return render_template('goals.html', goals=goals)

# Chatbot route
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-gemini-key')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    response_text = ""  # ✅ ALWAYS define this first!

    if request.method == 'POST':
        user_input = request.form['message']

        # ✅ Step 1: Build context string
        context = build_context(db)
        full_prompt = f"{context}\n\nUser question: {user_input}"

        print("=== PROMPT SENT TO GEMINI ===")
        print(full_prompt)
        print("=============================")

        try:
            response_text = ask_gemini(full_prompt)
        except Exception as e:
            response_text = "Sorry, I'm having trouble responding right now."
            print("Gemini error:", e)

        # ✅ Step 2: Emotion detection
        from models import detect_emotion
        emotion, score = detect_emotion(user_input)
        print(f"User emotion: {emotion} ({score:.2f})")

        # ✅ Step 3: Add emotional response
        if emotion == "sad":
            response_text += "\n\nI'm here for you. Want to review your spending together?"
        elif emotion == "joy":
            response_text += "\n\nNice! Looks like you're feeling good about your budget!"
        elif emotion == "anger":
            response_text += "\n\nWhoa! Let's take a breath and talk through what happened."

        # ✅ Step 4: Save chat history
        append_chat_history("user", user_input)
        append_chat_history("bot", response_text)

    chat_history = get_chat_history()
    return render_template('chat.html', chat_history=chat_history)


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
        init_context()  #removed db argument
    app.run(debug=True)

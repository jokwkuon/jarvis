import json
import os
from models import Income, Expense, Goal 

CONTEXT_FILE = 'context_store.json'


def write_context(db):
    incomes = db.session.query(Income).all()
    expenses = db.session.query(Expense).all()
    goals = db.session.query(Goal).all()

    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    balance = total_income - total_expense

    budget_status = "Healthy" if balance >= 0 else "Needs Attention"
    budget_advice = "Your budget looks good!" if balance >= 0 else "Try to reduce expenses."

    context = {
        "budget": {
            "status": budget_status,
            "advice": budget_advice
        },
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "goals": [
            {"name": g.name, "target": g.target_amount}
            for g in goals
        ],
        "chat_history": [] 
    }

    with open(CONTEXT_FILE, 'w') as f:
        json.dump(context, f, indent=4)


def init_context():
    if not os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, 'w') as f:
            json.dump({
                "budget": {
                    "status": "Unknown",
                    "advice": "No data yet."
                },
                "total_income": 0,
                "total_expense": 0,
                "balance": 0,
                "goals": [],
                "chat_history": []
            }, f, indent=4)


def update_context(data):
    with open(CONTEXT_FILE, 'r') as f:
        context = json.load(f)

    context.update(data)

    with open(CONTEXT_FILE, 'w') as f:
        json.dump(context, f, indent=4)


def read_context():
    if not os.path.exists(CONTEXT_FILE):
        init_context()
    with open(CONTEXT_FILE, 'r') as f:
        return json.load(f)


def append_chat_history(sender, message):
    context = read_context()

    if 'chat_history' not in context:
        context['chat_history'] = []

    context['chat_history'].append({"sender": sender, "message": message})

    # Keep only last 50 messages for performance
    context['chat_history'] = context['chat_history'][-50:]

    with open(CONTEXT_FILE, 'w') as f:
        json.dump(context, f, indent=4)


def get_chat_history():
    context = read_context()
    return context.get('chat_history', [])

from extensions import db
from models import Income, Expense

def get_budget_summary(db):
    incomes = Income.query.all()
    expenses = Expense.query.all()

    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)

    balance = total_income - total_expense

    if total_income == 0:
        status = "No income yet. Add some!"
        advice = "Try adding income sources to get started."
    elif total_expense > total_income:
        status = "Deficit ❌"
        advice = "Your expenses exceed your income. Consider reducing spending."
    elif total_expense > 0.7 * total_income:
        status = "Warning ⚠️"
        advice = "You're spending more than 70% of your income."
    else:
        status = "Healthy ✅"
        advice = "Your budget looks good!"

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "status": status,
        "advice": advice
    }

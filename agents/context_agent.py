from models import Income, Expense, Goal

def build_context(db):
    incomes = db.session.query(Income).all()
    expenses = db.session.query(Expense).all()
    goals = db.session.query(Goal).all()

    total_income = sum(income.amount for income in incomes)
    total_expenses = sum(expense.amount for expense in expenses)
    balance = total_income - total_expenses

    # Build goals progress
    goal_context = []
    for goal in goals:
        progress = (balance / goal.target_amount) * 100 if goal.target_amount > 0 else 0
        status = "On Track 🚀" if progress >= 50 else "Needs Attention ⚠️"
        goal_context.append(f"{goal.name}: {progress:.1f}% complete ({status})")

    # Build recent transactions
    recent_incomes = incomes[-3:] if len(incomes) >= 3 else incomes
    recent_expenses = expenses[-3:] if len(expenses) >= 3 else expenses

    income_context = ", ".join(f"${income.amount} from {income.source}" for income in recent_incomes)
    expense_context = ", ".join(f"${expense.amount} on {expense.category}" for expense in recent_expenses)

    # Assemble full context string
    context = (
        f"Current balance: ${balance:.2f}. "
        f"Total income: ${total_income:.2f}. Total expenses: ${total_expenses:.2f}. "
        f"Recent incomes: {income_context}. "
        f"Recent expenses: {expense_context}. "
        f"Goals: {'; '.join(goal_context)}."
    )

    return context

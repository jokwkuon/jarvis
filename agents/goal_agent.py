from extensions import db
from models import Income, Goal

def get_goal_progress():
    incomes = Income.query.all()
    goals = Goal.query.all()

    total_income = sum(income.amount for income in incomes)

    goal_progress = []

    for goal in goals:
        if goal.target_amount == 0:
            progress_percentage = 100  # Avoid division by zero
        else:
            progress_percentage = min(100, (total_income / goal.target_amount) * 100)

        status = "On Track 🚀" if progress_percentage >= 50 else "Needs Focus ⚠️"

        goal_progress.append({
            'name': goal.name,
            'target': goal.target_amount,
            'progress': round(progress_percentage, 2),
            'status': status
        })

    return goal_progress

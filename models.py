from transformers import pipeline
from extensions import db


# Load the classifier once
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

def detect_emotion(text):
    result = emotion_classifier(text)
    top_emotion = result[0]  # First result from top_k=1
    return top_emotion['label'], top_emotion['score']

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

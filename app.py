from flask import Flask, render_template, request, session
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for session management

GEMINI_API_KEY = "AIzaSyDBAcSGW3la_wpRSc0ZUfA9redDO6RwyUg"

@app.route('/')
def home():
    return render_template('home.html')

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
    app.run(debug=True)

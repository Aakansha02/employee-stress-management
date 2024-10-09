import logging
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
import sqlite3
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='hr_notifications.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database setup
def init_db():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            stress_level INTEGER,
            comments TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Gemini API settings
GEMINI_API_URL = "https://api.gemini.com/v1/chat"
GEMINI_API_KEY = "GEMINI API KEY"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    if user_message:
        response = get_gemini_response(user_message)
    else:
        response = "Please send a valid message."

    return jsonify({"response": response})

def get_gemini_response(user_message):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": user_message
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and "reply" in response_data:
            return response_data["reply"]
        else:
            return "Sorry, I couldn't process that request."
    except Exception as e:
        return f"Error communicating with AI: {e}"

@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    employee_id = data.get("employee_id")
    stress_level = data.get("stress_level")
    comments = data.get("comments", "")

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (employee_id, stress_level, comments)
        VALUES (?, ?, ?)
    ''', (employee_id, stress_level, comments))
    conn.commit()
    conn.close()

    # Notify HR if necessary
    if stress_level > 3:
        message = "High stress level reported."
        send_hr_alert(employee_id, stress_level, message)

    return jsonify({"status": "success"})

@app.route('/hr_alert', methods=['POST'])
def hr_alert():
    data = request.get_json()
    employee_id = data.get("employee_id")
    stress_level = data.get("stress_level")
    message = data.get("message")

    # Log the HR alert
    logging.warning(f"HR Alert: {message} (Employee ID: {employee_id}, Stress Level: {stress_level})")

    # Notify HR if stress level exceeds threshold
    if stress_level > 3:
        send_email_notification(employee_id, stress_level, message)

    return jsonify({"status": "success"})

def send_email_notification(employee_id, stress_level, message):
    sender_email = "your_email@gmail.com"  # Update with your email
    receiver_email = "hr_email@gmail.com"    # Update with HR's email
    subject = "High Stress Level Alert"
    body = f"Employee ID: {employee_id}\nStress Level: {stress_level}\nMessage: {message}\nPlease take necessary actions."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, "your_password")  # Update with your email password
            server.send_message(msg)
        logging.info(f"Email notification sent to HR for Employee ID: {employee_id}, Stress Level: {stress_level}")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return jsonify({"status": "success", "message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists."}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "message": "Login successful!"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid email or password."}), 401

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

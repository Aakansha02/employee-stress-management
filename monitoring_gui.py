import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import sqlite3
import cv2  
import numpy as np  

def init_user_db():
    conn = sqlite3.connect('feedback.db')  # Use the same database as your app.py
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_user(email, password):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists
    finally:
        conn.close()

def validate_user(email, password):
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

class LoginPage:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.configure(bg='#f0f0f0')

        tk.Label(master, text="Email:", bg='#f0f0f0').pack(pady=5)
        self.email_entry = tk.Entry(master)
        self.email_entry.pack(pady=5)

        tk.Label(master, text="Password:", bg='#f0f0f0').pack(pady=5)
        self.password_entry = tk.Entry(master, show='*')
        self.password_entry.pack(pady=5)

        login_button = ttk.Button(master, text="Login", command=self.login)
        login_button.pack(pady=10)

        register_button = ttk.Button(master, text="Register", command=self.register)
        register_button.pack(pady=5)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if validate_user(email, password):
            self.master.destroy()  # Close the login window
            self.open_main_app()   # Open the main application
        else:
            messagebox.showerror("Login Error", "Invalid email or password.")

    def register(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if register_user(email, password):
            messagebox.showinfo("Registration Success", "User registered successfully!")
        else:
            messagebox.showerror("Registration Error", "Email already exists.")

    def open_main_app(self):
        root = tk.Tk()
        app = StressApp(root)
        root.mainloop()

class StressApp:
    def __init__(self, master):
        self.master = master
        master.title("Emotion Recognition and Mental Health Support System")
        master.configure(bg='#f0f0f0')

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)

        # Tabs
        self.emotion_recognition_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.emotion_recognition_frame, text='Emotion Recognition')
        self.create_emotion_recognition_tab()

        self.feedback_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.feedback_frame, text='Feedback Check-In')
        self.create_feedback_tab()

        self.chatbot_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chatbot_frame, text='Chatbot Interaction')
        self.create_chatbot_tab()

        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text='Project Overview')
        self.create_overview_tab()

        self.features_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.features_frame, text='Key Features')
        self.create_features_tab()

        self.data_usage_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_usage_frame, text='Data Usage Explanation')
        self.create_data_usage_tab()

    def create_emotion_recognition_tab(self):
        tk.Label(self.emotion_recognition_frame, text="Emotion Recognition Module",
                 font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)
        tk.Label(self.emotion_recognition_frame, text="Upload a video or image for analysis:",
                 bg='#f0f0f0').pack(pady=5)
        upload_button = ttk.Button(self.emotion_recognition_frame, text="Upload", command=self.upload_emotion)
        upload_button.pack(pady=5)
        self.emotion_result = tk.Text(self.emotion_recognition_frame, height=10, width=50)
        self.emotion_result.pack(pady=10)

    def upload_emotion(self):
        file_path = filedialog.askopenfilename(title="Select an Image or Video",
                                                filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), 
                                                           ("Video files", "*.mp4;*.avi"), 
                                                           ("All files", "*.*")))
        if file_path:
            self.analyze_emotion(file_path)

    def analyze_emotion(self, file_path):
        stress_level = self.detect_emotion(file_path)

        # Display result
        self.emotion_result.delete("1.0", tk.END)
        self.emotion_result.insert(tk.END, f"Detected Stress Level: {stress_level}\n")

        if stress_level > 3:
            self.trigger_hr_alert(stress_level)

    def detect_emotion(self, file_path):
        # Placeholder for emotion detection logic
        return np.random.randint(0, 6)  # Replace with actual detection logic

    def trigger_hr_alert(self, stress_level):
        hr_data = {
            "employee_id": "123",  # Use actual employee ID
            "stress_level": stress_level,
            "message": "High stress level detected! Please intervene."
        }
        try:
            response = requests.post('http://127.0.0.1:5000/hr_alert', json=hr_data)
            if response.status_code == 200:
                messagebox.showinfo("HR Alert", "HR has been notified of the high stress level.")
            else:
                messagebox.showerror("Error", "Failed to notify HR.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to the server: {e}")

    def create_feedback_tab(self):
        tk.Label(self.feedback_frame, text="Feedback Check-In",
                 font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)

        tk.Label(self.feedback_frame, text="Stress Level (1-5):", bg='#f0f0f0').pack(pady=5)
        self.stress_level = tk.Entry(self.feedback_frame)
        self.stress_level.pack(pady=5)

        tk.Label(self.feedback_frame, text="Comments:", bg='#f0f0f0').pack(pady=5)
        self.comments = tk.Text(self.feedback_frame, height=5, width=30)
        self.comments.pack(pady=5)

        submit_button = ttk.Button(self.feedback_frame, text="Submit", command=self.submit_feedback)
        submit_button.pack(pady=10)

    def submit_feedback(self):
        stress_level = self.stress_level.get()
        comments = self.comments.get("1.0", tk.END).strip()

        if not stress_level.isdigit() or not (1 <= int(stress_level) <= 5):
            messagebox.showerror("Input Error", "Please enter a valid stress level (1-5).")
            return

        data = {
            "employee_id": "123",  # Use actual employee ID
            "stress_level": int(stress_level),
            "comments": comments
        }

        try:
            response = requests.post('http://127.0.0.1:5000/checkin', json=data)
            if response.json().get("status") == "success":
                messagebox.showinfo("Success", "Check-in submitted successfully!")
                self.stress_level.delete(0, tk.END)
                self.comments.delete("1.0", tk.END)
            else:
                messagebox.showerror("Error", "Failed to submit check-in.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to the server: {e}")

    def create_chatbot_tab(self):
        tk.Label(self.chatbot_frame, text="Chatbot Interaction",
                 font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)

        tk.Label(self.chatbot_frame, text="Type your message:", bg='#f0f0f0').pack(pady=5)
        self.chatbot_input = tk.Entry(self.chatbot_frame, width=50)
        self.chatbot_input.pack(pady=5)

        send_button = ttk.Button(self.chatbot_frame, text="Send", command=self.send_chat)
        send_button.pack(pady=5)

        self.chatbot_response = tk.Text(self.chatbot_frame, height=10, width=50, state='disabled')
        self.chatbot_response.pack(pady=10)

    def send_chat(self):
        user_message = self.chatbot_input.get()
        self.chatbot_response.config(state='normal')
        self.chatbot_response.insert(tk.END, f"You: {user_message}\n")

        data = {"message": user_message}
        try:
            response = requests.post('http://127.0.0.1:5000/chat', json=data)
            chatbot_reply = response.json().get("response", "Sorry, I didn't understand that.")
            self.chatbot_response.insert(tk.END, f"Chatbot: {chatbot_reply}\n")
        except Exception as e:
            self.chatbot_response.insert(tk.END, f"Chatbot: Error connecting to API: {e}\n")

        self.chatbot_response.config(state='disabled')
        self.chatbot_input.delete(0, tk.END)

    def create_overview_tab(self):
        overview_text = (
            "Objective:\n"
            "To develop a non-intrusive system that monitors employee stress levels using "
            "emotion recognition technology and provides timely support through feedback "
            "mechanisms and a chatbot, fostering a healthier workplace environment."
        )
        tk.Label(self.overview_frame, text=overview_text, wraplength=500, justify="left",
                 bg='#f0f0f0', font=('Arial', 12)).pack(padx=10, pady=10)

    def create_features_tab(self):
        features_text = (
            "Key Features:\n\n"
            "1. Real-Time Stress Detection:\n"
            "   - Utilizing OpenCV and a trained deep learning model, we analyze facial expressions.\n"
            "   - Our focus is on identifying stress indicators such as furrowed brows and tight lips.\n\n"
            "2. Self-Reported Stress Check-Ins:\n"
            "   - Employees can anonymously report their stress levels through surveys.\n\n"
            "3. Mood Tracking:\n"
            "   - Combining our emotion recognition data with self-reported mood inputs helps us create a comprehensive view of well-being.\n\n"
            "4. AI-Powered Chatbot Support System:\n"
            "   - Integrated with OpenAI for immediate support, enhancing accessibility to mental health resources.\n\n"
            "5. Automated Alerts for HR:\n"
            "   - High stress levels trigger alerts to HR for timely intervention.\n\n"
            "6. Monitoring Behavioral and Environmental Changes:\n"
            "   - Analyzing behavioral patterns to identify changes indicating stress."
        )
        tk.Label(self.features_frame, text=features_text, wraplength=500, justify="left",
                 bg='#f0f0f0', font=('Arial', 12)).pack(padx=10, pady=10)

    def create_data_usage_tab(self):
        data_usage_text = (
            "Data Usage:\n\n"
            "In our system, we collect data to improve employee well-being:\n"
            "- We gather feedback from employees about their stress levels and comments.\n"
            "- This data helps us identify trends and areas where support is needed.\n"
            "- All collected data is stored securely in compliance with privacy regulations.\n"
            "- We use aggregated data to refine our algorithms and improve our chatbot responses.\n"
            "- Individual feedback is kept confidential and only used for analytical purposes."
        )
        tk.Label(self.data_usage_frame, text=data_usage_text, wraplength=500, justify="left",
                 bg='#f0f0f0', font=('Arial', 12)).pack(padx=10, pady=10)

if __name__ == "__main__":
    init_user_db()  # Initialize the user database
    root = tk.Tk()
    login_page = LoginPage(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import sqlite3
import cv2, os
import numpy as np
from emotion_detector import detect_emotion
import customtkinter as ctk
from llm_clients import GeminiClient
from pydantic import BaseModel
from dotenv import load_dotenv
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()
EMAIL = os.getenv("email")
APP_PASSWORD = os.getenv("app_password")
GEMINI_KEY = os.getenv("GEMINI_KEY")


def init_user_db():
    conn = sqlite3.connect("feedback.db")  # Use the same database as your app.py
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def register_user(email, password):
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)", (email, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists
    finally:
        conn.close()


def validate_user(email, password):
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?", (email, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None


class LoginPage:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.geometry("500x400")
        ctk.set_appearance_mode("dark")  # Options: "System", "Light", "Dark"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

        # Creating the frame for the login page
        self.frame = ctk.CTkFrame(master)
        self.frame.pack(pady=0, padx=0, fill="both", expand=True)

        ctk.CTkLabel(self.frame, text="Email:", font=("Arial", 20, "bold")).pack(pady=5)
        self.email_entry = ctk.CTkEntry(self.frame, placeholder_text="Enter your email")
        self.email_entry.pack(pady=5)

        ctk.CTkLabel(self.frame, text="Password:", font=("Arial", 20, "bold")).pack(
            pady=5
        )
        self.password_entry = ctk.CTkEntry(
            self.frame,
            placeholder_text="Enter your password",
            show="*",
        )
        self.password_entry.pack(pady=5)

        login_button = ctk.CTkButton(
            self.frame, text="Login", font=("Arial", 20, "bold"), command=self.login
        )
        login_button.pack(pady=10)

        register_button = ctk.CTkButton(
            self.frame,
            text="Register",
            command=self.register,
            font=("Arial", 20, "bold"),
        )
        register_button.pack(pady=5)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if validate_user(email, password):
            self.master.destroy()  # Close the login window
            self.open_main_app()  # Open the main application
        else:
            messagebox.showerror("Login Error", "Invalid email or password.")

    def register(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if self.register_user(email, password):
            messagebox.showinfo("Registration Success", "User registered successfully!")
        else:
            messagebox.showerror("Registration Error", "Email already exists.")

    def open_main_app(self):
        root = ctk.CTk()  # Initialize CustomTkinter window
        app = StressApp(root)
        root.mainloop()


def capture_and_detect_emotion():
    cap = cv2.VideoCapture(camera_indices[0])  # Use the default camera
    ret, frame = cap.read()  # Capture a single frame
    cap.release()  # Release the camera immediately after capturing

    if ret:
        # Call your emotion detection function
        emotion = detect_emotion(frame)
        return emotion, frame
    else:
        print("Failed to capture image.")
        return None, None


class StressApp:
    def __init__(self, master):
        self.master = master
        master.title("Emotion Recognition and Mental Health Support System")
        master.configure(bg="#f0f0f0")
        master.title("Login")
        master.geometry("900x700")
        ctk.set_appearance_mode("dark")  # Options: "System", "Light", "Dark"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

        # Create a CTkTabview (instead of ttk.Notebook)
        self.tabview = ctk.CTkTabview(master)
        self.tabview.pack(fill="both", expand=True)

        # Add tabs (no 'text' argument, use key-based tab names)
        self.tabview.add("Emotion Recognition")
        self.tabview.add("Wearable Devices")
        self.tabview.add("BuddyAlert")
        self.tabview.add("Chatbot Interaction")
        self.tabview.add("Project Overview")
        self.tabview.add("Key Features")
        self.tabview.add("Data Usage Explanation")

        # Call the functions to add content to the tabs
        self.create_emotion_recognition_tab()
        self.create_wearable_devices_tab()
        self.create_feedback_tab()
        self.create_chatbot_tab()
        self.create_overview_tab()
        self.create_features_tab()
        self.create_data_usage_tab()

    def create_emotion_recognition_tab(self):
        # Content for the "Emotion Recognition" tab
        emotion_tab = self.tabview.tab("Emotion Recognition")
        ctk.CTkLabel(
            emotion_tab, text="Emotion Recognition Module", font=("Arial", 20, "bold")
        ).pack(pady=10)
        ctk.CTkLabel(emotion_tab, text="Capture image for emotion analysis:").pack(
            pady=5
        )
        upload_button = ctk.CTkButton(
            emotion_tab, text="Detect", command=self.upload_emotion
        )
        upload_button.pack(pady=5)
        self.emotion_result = ctk.CTkTextbox(emotion_tab, height=300, width=400)
        self.emotion_result.pack(pady=10)

    def create_wearable_devices_tab(self):
        # Content for the "Wearable Devices" tab
        emotion_tab = self.tabview.tab("Wearable Devices")

        # Title label
        ctk.CTkLabel(
            emotion_tab, text="Connect Wearable Devices", font=("Arial", 20, "bold")
        ).pack(pady=10)

        # Instruction label
        ctk.CTkLabel(emotion_tab, text="Connect Device for emotion analysis:").pack(
            pady=5
        )

        # Create the devices frame
        devices = ctk.CTkFrame(emotion_tab)
        devices.pack(pady=10)

        # Configure the grid for 2 columns
        for i in range(2):
            devices.grid_columnconfigure(i, weight=1)

        # Create circular buttons
        self.create_circular_buttons(devices)

    def create_circular_buttons(self, frame):

        button = ctk.CTkButton(
            frame,
            text=f"Apple Watch",
            command=self.button_command,
            width=60,  # Set width for a circular shape
            height=60,  # Set height for a circular shape,
            corner_radius=60,
            font=("Arial", 20, "bold"),
        )
        button.grid(row=0, column=0, padx=10, pady=10)

        button = ctk.CTkButton(
            frame,
            text=f"Google Watch",
            command=self.button_command,
            width=60,  # Set width for a circular shape
            height=60,  # Set height for a circular shape,
            corner_radius=60,
            font=("Arial", 20, "bold"),
        )
        button.grid(row=0, column=1, padx=10, pady=10)

        button = ctk.CTkButton(
            frame,
            text=f"Fitbit Watch",
            command=self.button_command,
            width=60,  # Set width for a circular shape
            height=60,  # Set height for a circular shape,
            corner_radius=60,
            font=("Arial", 20, "bold"),
        )
        button.grid(row=1, column=0, padx=10, pady=10)

        button = ctk.CTkButton(
            frame,
            text=f"Samsung Watch",
            command=self.button_command,
            width=60,  # Set width for a circular shape
            height=60,  # Set height for a circular shape,
            corner_radius=60,
            font=("Arial", 20, "bold"),
        )
        button.grid(row=1, column=1, padx=10, pady=10)

        button = ctk.CTkButton(
            frame,
            text=f"Bolt Watch",
            command=self.button_command,
            width=60,  # Set width for a circular shape
            height=60,  # Set height for a circular shape,
            corner_radius=60,
            font=("Arial", 20, "bold"),
        )
        button.grid(row=2, column=0, padx=10, pady=10)

    def button_command(self):
        print("Button clicked!")

    def create_feedback_tab(self):
        feedback_tab = self.tabview.tab("BuddyAlert")
        ctk.CTkLabel(feedback_tab, text="BuddyAlert", font=("Arial", 20, "bold")).pack(
            pady=10
        )

        # Input for user email
        ctk.CTkLabel(feedback_tab, text="Your Email:").pack(pady=5)
        self.user_email = ctk.CTkEntry(feedback_tab)
        self.user_email.pack(pady=5)

        # Input for stress level
        ctk.CTkLabel(feedback_tab, text="Stress Level (1-5):").pack(pady=5)
        self.stress_level = ctk.CTkEntry(feedback_tab)
        self.stress_level.pack(pady=5)

        # Input for comments
        ctk.CTkLabel(feedback_tab, text="Comments:").pack(pady=5)
        self.comments = ctk.CTkTextbox(feedback_tab, height=300, width=400)
        self.comments.pack(pady=5)

        # Submit button
        submit_button = ctk.CTkButton(
            feedback_tab, text="Submit", command=self.submit_feedback
        )
        submit_button.pack(pady=10)

        # Label for feedback message
        self.feedback_message = ctk.CTkLabel(
            feedback_tab, text="", fg_color="lightgrey"
        )
        self.feedback_message.pack(pady=10)

    def submit_feedback(self):
        user_email = self.user_email.get()
        stress_level = self.stress_level.get()
        comments = self.comments.get("1.0", "end").strip()  # Get text from the textbox

        # Check if the email input is valid
        if not user_email:
            self.feedback_message.configure(
                text="Please enter your email.", fg_color="red"
            )
            return

        subject = "BuddyAlert Feedback Submission"
        body = f"Stress Level: {stress_level}\n\nComments:\n{comments}"

        # Call the email sending function
        success = self.send_email(subject, body, user_email)

        # Update the feedback message based on success or failure
        if success:
            self.feedback_message.configure(
                text="Email sent successfully!", fg_color="green"
            )
        else:
            self.feedback_message.configure(
                text="Failed to send email.", fg_color="red"
            )

    def send_email(self, subject, body, to_email):
        # Gmail SMTP server details
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        from_email = EMAIL
        app_password = APP_PASSWORD

        # Create message container
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # Attach the message body
        msg.attach(MIMEText(body, "plain"))

        try:
            # Set up the SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Start TLS encryption
            server.login(from_email, app_password)  # Log in to the server

            # Send the email
            server.sendmail(from_email, to_email, msg.as_string())

            # Close the connection to the server
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def create_chatbot_tab(self):
        chatbot_tab = self.tabview.tab("Chatbot Interaction")
        ctk.CTkLabel(
            chatbot_tab, text="Chatbot Interaction", font=("Arial", 20, "bold")
        ).pack(pady=10)
        self.chatbot_response = ctk.CTkTextbox(
            chatbot_tab, height=300, width=500, state="disabled"
        )
        self.chatbot_response.pack(pady=10)
        ctk.CTkLabel(chatbot_tab, text="Type your message:").pack(pady=5)
        self.chatbot_input = ctk.CTkTextbox(chatbot_tab, width=400, height=70)
        self.chatbot_input.pack(pady=5)
        send_button = ctk.CTkButton(chatbot_tab, text="Send", command=self.send_chat)
        send_button.pack(pady=5)

    def create_overview_tab(self):
        # Content for the "Project Overview" tab
        overview_tab = self.tabview.tab("Project Overview")
        overview_text = (
            "Objective:\n"
            "To develop a non-intrusive system that monitors employee stress levels using "
            "emotion recognition technology and provides timely support through feedback "
            "mechanisms and a chatbot, fostering a healthier workplace environment."
        )
        ctk.CTkLabel(
            overview_tab,
            text=overview_text,
            wraplength=500,
            justify="left",
            font=("Arial", 20),
        ).pack(padx=10, pady=100)

    def create_features_tab(self):
        # Content for the "Key Features" tab
        features_tab = self.tabview.tab("Key Features")
        features_text = (
            "Key Features:\n\n"
            "1. Real-Time Stress Detection:\n"
            "   - Utilizing OpenCV and a trained deep learning model, we analyze facial expressions.\n\n"
            "2. Periodic Stress Monitoring:\n"
            "   - The system periodically monitors users' emotions and health parameters such as blood pressure (BP) and heart rate at 10-minute intervals. If the stress level crosses a certain threshold, it automatically initiates Self-Reported Stress Check-Ins and encourages users to take short breaks.\n\n"
            "3. Self-Reported Stress Check-Ins:\n"
            "   - Employees can contact their designated buddy through the application. However, the application also automatically initiates this process when it detects prolonged stress in the user.\n\n"
            "4. AI-Powered Chatbot Support System:\n"
            "   - Integrated with Gemini for immediate support, enhancing accessibility to mental health resources.\n"
        )
        ctk.CTkLabel(
            features_tab,
            text=features_text,
            width=800,
            wraplength=700,
            justify="left",
            font=("Arial", 20),
        ).pack(padx=10, pady=50)

    def create_data_usage_tab(self):
        # Content for the "Data Usage Explanation" tab
        data_usage_tab = self.tabview.tab("Data Usage Explanation")
        data_usage_text = (
            "Data Usage:\n\n"
            "We collect feedback from employees about their stress levels and comments to identify trends and provide support.\n"
            "- All data is securely stored in compliance with privacy regulations.\n"
        )
        ctk.CTkLabel(
            data_usage_tab,
            text=data_usage_text,
            wraplength=500,
            justify="left",
            font=("Arial", 20),
        ).pack(padx=10, pady=100)

    def upload_emotion(self):
        try:
            # Attempt to capture and detect emotion
            stress_level = capture_and_detect_emotion()

            # Update the UI with the detected emotion
            self.emotion_result.delete("1.0", tk.END)
            self.emotion_result.insert(
                tk.END,
                f"Detected Stress Level: {stress_level[0][0]['dominant_emotion']}\n",
            )
        except Exception as e:
            # In case of error, show an error message in the UI without crashing
            self.emotion_result.delete("1.0", tk.END)
            self.emotion_result.insert(
                tk.END, "Error: Failed to detect emotion. Please try again.\n"
            )
            print(f"Error during emotion detection: {e}")  # Log the error for debugging

        # if stress_level > 3:
        #   self.trigger_hr_alert(stress_level)

    def send_chat(self):
        user_input = self.chatbot_input.get("1.0", "end-1c").strip()
        if user_input:
            self.chatbot_input.delete("1.0", "end")
            gemini_client = GeminiClient(gemini_key=GEMINI_KEY)

            class ChatResponse(BaseModel):
                reply: str

            try:
                response = gemini_client.generate_response(
                    prompt=user_input,
                    structure=ChatResponse,
                )
                self.chatbot_response.configure(
                    state="normal"
                )  # Enable textbox editing
                self.chatbot_response.insert("end", f"User: {user_input}\n\n")
                self.chatbot_response.insert("end", f"MOJO: {response.reply}\n\n")
                self.chatbot_response.configure(
                    state="disabled"
                )  # Disable textbox editing again

            except Exception as e:
                self.chatbot_response.configure(
                    state="normal"
                )  # Enable textbox editing
                self.chatbot_response.insert("end", f"Error: {str(e)}\n\n")
                self.chatbot_response.configure(
                    state="disabled"
                )  # Disable textbox editing again


if __name__ == "__main__":
    init_user_db()  # Initialize the user database
    root = tk.Tk()
    camera_indices = []
    for i in range(10):  # Check the first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_indices.append(i)
            cap.release()
    login_page = LoginPage(root)
    root.mainloop()

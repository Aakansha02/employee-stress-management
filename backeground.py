import cv2
import time
import numpy as np
import json
from datetime import datetime
from emotion_detector import detect_emotion  # Import your emotion detection function


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


def save_emotions_to_json(emotions_list):
    with open("emotions.json", "r") as file:
        data = json.load(file)
    data.extend(emotions_list)
    with open("emotions.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


def capture_images(interval):
    emotions_list = []  # List to hold emotion data

    try:
        while True:  # Loop indefinitely
            # Capture an image and detect emotion
            emotion, frame = capture_and_detect_emotion()
            if emotion is not None:
                # Append emotion and timestamp to the list
                emotions_list.append(
                    {"timestamp": datetime.now().isoformat(), "emotion": emotion}
                )

                # Save emotions to a JSON file
                save_emotions_to_json(emotions_list)

                # Optionally display the frame
                cv2.putText(
                    frame,
                    f"Emotion: {emotion[0]['dominant_emotion']}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 0),
                    2,
                )
                cv2.imshow("Emotion Detection", frame)
                cv2.waitKey(1000)  # Display the image for 1 second

            # Wait for the specified interval (30 minutes)
            time.sleep(interval)

            # Check if a key is pressed to exit (break loop if 'q' is pressed)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    camera_indices = []
    for i in range(10):  # Check the first 10 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            camera_indices.append(i)
            cap.release()

    interval_in_minutes = 0.5
    interval_in_seconds = interval_in_minutes * 60  # Convert to seconds
    # capture_images(interval_in_seconds)
    capture_and_detect_emotion()
